#!/usr/bin/env python3
"""Hermes english data -> Firestore sync (runs on Hostinger VPS host via cron).

Sources (written by Hermes cron jobs):
  - wanted_phrases.md : Patrick's stuck expressions   -> source=hermes-wanted
  - b2_vocab_log.md   : delivered chunks/words (AM/PM/10AM) -> source=hermes-delivered

These files are the contract. Any English cron job -- existing or newly added --
gets picked up automatically as long as it keeps appending to them. Editing or
creating cron jobs does not require touching this script.

Idempotent: doc id = sha1(source|date|expression). Existing docs are skipped
(POST createDocument returns 409 ALREADY_EXISTS), so review progress made in
the dashboard is never overwritten.

Near-duplicate guard (2026-08-25): doc-id idempotency only catches byte-identical
text. wanted_phrases and b2_vocab_log often teach the same real phrase a day or two
apart with slightly different wording -- see is_near_duplicate() / DEDUP_DAYS.

Deployed at: /root/english-sync/sync_english_to_firestore.py (cron hourly, :20)
Local copy:  02_projects/english-tracker/hermes-sync.py -- edit here, then deploy.
"""
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import date, timedelta

BASE = "/docker/hermes-agent-7jge/data/english"
# Hermes 크론이 실행 결과 전문을 남기는 곳. `b2_vocab_log.md` 는 중복 체크용 3칸(표현|뜻|예문)이라
# 리듬맵·한글발음·확장 표현이 **애초에 안 담긴다** — 그 원본이 여기 있다 (2026-08-17 발견).
# **잡 이름으로 거르지 않는다.** 영어 배달 잡 3개 중 하나는 이름이
# `patrick-b2-words-weekday-10am` 이라 `english` 가 안 들어간다 — 이름으로 걸렀다가
# 10AM 단어 카드가 통째로 누락됐다 (2026-08-17). 잡 이름은 언제든 바뀔 수 있다.
# 대신 **응답에 리듬 화살표(→ ↘ ↓ ↗)가 있는가**로 판별한다. 리듬맵의 공통 신호라
# 두 형식 모두 걸린다. `발음:` 라벨로 걸렀다가 라벨을 안 쓰는 10AM 형식을 또 놓쳤다.
CRON_OUT = "/docker/hermes-agent-7jge/data/cron/output"
LESSON_MARK_RE = re.compile(r"[→↘↓↗]")
# English Tracker 전용 프로젝트. M Building 프로젝트를 절대 여기에 넣지 말 것.
PROJECT = "english-tracker-cea9f"
API_KEY = "AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
COLLECTION = "english_expressions"
BACKFILL_DAYS = 7  # only sync items learned within this window

# 근접 중복 방지 (2026-08-25 Patrick 요청). doc_id 멱등은 **완전히 같은 문자열**만 막는다 —
# 막힌 표현(wanted)이 하루이틀 뒤 배달(delivered)로 문구만 바뀌어 다시 오거나, 회화 노트가
# 같은 문장을 살짝 다른 표현으로 반복 추출하면 doc_id가 달라져 별개 카드로 계속 쌓였다
# (실측: "settle up this month's company expenses" 가 wanted 8/17 · delivered 8/18 로 중복,
# "Could we move this to Friday?" 류가 8/23 하루에 3장). 최근 DEDUP_DAYS 일 내 기존 표현과
# 비교해 겹치면 새 카드를 만들지 않는다.
DEDUP_DAYS = 5
DEDUP_JACCARD = 0.6  # 단어 집합 겹침 비율. 관사 뺀 단어 기준(_loose 재사용)

# Supertonic TTS 릴레이 (같은 서버의 english-tts 컨테이너, localhost로만 열려 있다).
# 값은 index.html 의 TTS_SPEED / 기본 음성과 반드시 일치해야 한다 — 다르면 캐시가 안 맞는다.
TTS_URL = "http://127.0.0.1:8080/tts"
# 철자로 읽어야 하는 약어. **앱의 SPELL_OUT 과 같은 목록이어야 한다.**
# 표기만으로는 `**UNWIND**`(영어 단어)와 `**CUSA**`(약어)를 구분할 수 없다 — 둘 다 화면에선 피크다.
SPELL_OUT = re.compile(r"CUSA|CRBC|CRLC|OR|BIR|VAT|SSS|AEP|LOI|NTE|PO|STF|DPR|BFP|NTC|FSIC")

# Patrick이 고른 두 목소리(2026-08-15 블라인드 청취: Emma 유일한 ★5).
# 둘 다 미리 만들어 두면 앱에서 바꿔도 안 기다린다. index.html 의 DEFAULT_SRV_VOICE·prewarmTTS 와 같아야 한다.
TTS_VOICES = ["Emma", "Puck"]
TTS_SPEED = "0.9"

FIRESTORE_URL = (
    "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/%s"
    % (PROJECT, COLLECTION)
)

# 이 API 키에는 HTTP 리퍼러 제한이 걸려 있다 (2026-08-10, 유출 대비 조치).
# 브라우저가 아닌 이 스크립트는 Referer 를 안 보내서 그대로 두면
#   403 "Requests from referer <empty> are blocked"
# 로 죽는다 -- 실제로 크론이 조용히 실패하고 있었다.
# 허용 목록에 있는 앱 주소를 명시해서 보낸다. 우회가 아니라 같은 앱의 서버측 절반이다.
# GCP 콘솔에서 허용 도메인을 바꾸면 이 값도 같이 고칠 것.
APP_REFERER = "https://jameskim01115-hub.github.io/english-tracker/"


def api_headers(token=None):
    h = {"Content-Type": "application/json", "Referer": APP_REFERER}
    if token:
        h["Authorization"] = "Bearer %s" % token
    return h


def get_id_token():
    """Sign in anonymously. The tracker's Firestore rules require a signed-in
    session, so an unauthenticated write is rejected with 403."""
    url = ("https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=%s"
           % API_KEY)
    body = json.dumps({"returnSecureToken": True}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers=api_headers(), method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["idToken"]


def today_manila():
    # VPS is UTC; Manila = UTC+8. Good enough for date math without deps.
    from datetime import datetime, timezone
    return (datetime.now(timezone.utc) + timedelta(hours=8)).date()


def doc_id(source, learned, expression):
    key = "%s|%s|%s" % (source, learned, expression)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:20]


def fs_fields(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, bool):
            out[k] = {"booleanValue": v}
        elif isinstance(v, int):
            out[k] = {"integerValue": str(v)}
        else:
            out[k] = {"stringValue": str(v)}
    return out


def create_doc(did, data, token):
    """Create document; return True if created, False if it already existed."""
    url = "%s?documentId=%s&key=%s" % (FIRESTORE_URL, did, API_KEY)
    body = json.dumps({"fields": fs_fields(data)}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST", headers=api_headers(token),
    )
    try:
        urllib.request.urlopen(req, timeout=20)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 409:
            return False
        print("ERROR creating %s: HTTP %s %s" % (did, e.code, e.read()[:200]), file=sys.stderr)
        return False
    except Exception as e:  # network etc.
        print("ERROR creating %s: %s" % (did, e), file=sys.stderr)
        return False


def patch_doc(did, data, token, clear=None):
    """기존 문서에 **지정한 필드만** 덧쓴다 (updateMask).

    동기화는 create-only 라 새 필드(rhythm·pron·variants)가 옛 문서에는 안 붙는다.
    문서를 통째로 다시 쓰면 stage·nextReview 같은 **복습 진도가 날아간다** —
    updateMask 로 새 필드만 건드리는 게 유일하게 안전한 방법이다.
    """
    clear = clear or []
    if not data and not clear:
        return False
    # updateMask 에 넣고 fields 에서 빼면 **그 필드가 삭제된다.** 잘못 들어간 필드를 되돌릴 때 쓴다.
    mask = "&".join("updateMask.fieldPaths=%s" % k for k in list(data) + list(clear))
    url = "%s/%s?%s&key=%s" % (FIRESTORE_URL, did, mask, API_KEY)
    body = json.dumps({"fields": fs_fields(data)}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="PATCH", headers=api_headers(token),
    )
    try:
        urllib.request.urlopen(req, timeout=20)
        return True
    except Exception as e:
        print("ERROR patching %s: %s" % (did, e), file=sys.stderr)
        return False


def next_review_for(learned_iso, today):
    """Stage-0 next review = learned+1d; stagger past-due backfill over 5 days."""
    y, m, d = (int(x) for x in learned_iso.split("-"))
    nxt = date(y, m, d) + timedelta(days=1)
    if nxt < today:
        offset = int(hashlib.sha1(learned_iso.encode()).hexdigest(), 16) % 5
        nxt = today + timedelta(days=offset)
    return nxt.isoformat()


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _block_field(block, label):
    """Read a block-style field:  'Label:\\n<value lines>' until the next blank line."""
    m = re.search(r"^%s\s*:?\s*$\n((?:.+\n?)+?)(?:\n|\Z)" % re.escape(label), block, flags=re.M)
    if not m:
        m = re.search(r"^%s\s*:\s*(.+)$" % re.escape(label), block, flags=re.M)
        return m.group(1).strip() if m else ""
    return " ".join(l.strip() for l in m.group(1).splitlines() if l.strip())


# 라벨 동의어. **봇이 형식을 자주 바꾼다** — 2026-08-17에 `Original:` 대신
# `Preferred expression:`, `## 날짜` 헤더 대신 `---`+`Date:` 로 써서 블록이 통째로 안 읽혔다.
# 봇을 조이는 것보다 파서가 견디는 편이 낫다 (CLAUDE.md: "라벨 매칭은 장식에 견뎌야 한다").
# 새 라벨이 나오면 여기에 추가할 것.
WANTED_LABELS = {
    "expr": ["Original wanted expression(s)", "Original wanted expression",
             "Preferred expression", "Original", "English", "표현"],
    "ko":   ["Korean meaning", "Korean", "한국어", "뜻"],
    "rh":   ["Rhythm map", "Rhythm", "리듬맵", "리듬"],
    "pron": ["Korean pronunciation", "Pronunciation", "한글 발음", "발음"],
    "ctx":  ["Context", "Tags", "상황", "태그"],
    # 확장 표현. 봇이 부를 때마다 이름을 바꾼다 — 실제로 본 것만 넣지 말고 넉넉히 둘 것.
    "ex":   ["Related expressions", "Related expression", "Other ways to say",
             "Alternatives", "Alternative expressions", "Variations",
             "Examples", "Example",
             "이렇게도 말해요", "확장", "비슷한 표현", "다른 표현"],
}


def _label_get(block, keys, idx=""):
    """`- 라벨: 값` / `라벨: 값` 둘 다 받는다. 볼드·앞불릿 장식도 벗긴다.

    **한 블록에 문장이 둘이면 봇이 라벨에 번호를 붙인다** — `- Korean 2:` `- Rhythm 2:`.
    지금까지 `Original` 만 번호를 견디는 별도 정규식을 갖고 있었고, 나머지는 번호가 붙는
    순간 통째로 안 읽혔다. 그래서 카드에 문장과 덩어리만 나오고 **뜻·리듬·발음이 전부
    비어 있었다** (2026-08-20 Patrick 지적, 에러도 경고도 없었다).

    `idx` 가 주어지면 그 번호를 **먼저** 찾고, 없으면 번호 없는 라벨로 떨어진다.
    번호 없는 패턴이 `Korean 1:` 을 잘못 집을 일은 없다 — 라벨 뒤에 곧바로 `:` 를 요구한다.
    """
    pats = []
    if idx:
        pats += [(label, r"^\s*(?:[-*]\s*)?\**\s*%s\s*%s\s*\**\s*:\s*(.+)$"
                  % (re.escape(label), re.escape(idx))) for label in keys]
    pats += [(label, r"^\s*(?:[-*]\s*)?\**\s*%s\s*\**\s*:\s*(.+)$"
              % re.escape(label)) for label in keys]
    for _label, pat in pats:
        m = re.search(pat, block, flags=re.M | re.I)
        if m:
            v = m.group(1).strip().strip("*").strip()
            if v:
                return v
    return ""


def parse_wanted(text):
    """wanted_phrases.md 에서 (날짜, 표현, 상황, 한국어, 리듬, 발음, 확장) 을 뽑는다.

    **블록 형태가 세 가지고 전부 살아 있다.** 봇이 형식을 바꿔도 기존 카드가 깨지면 안 된다.

      1) compact   `## YYYY-MM-DD 막힌 표현` + `- Original:` …
      2) verbose   `## YYYY-MM-DD …` + `Original wanted expression:` (2026-07)
      3) 구분선형   `---` + `Date: YYYY-MM-DD …` + `Preferred expression:` … (2026-08-17~)

    라벨은 `WANTED_LABELS` 의 동의어로 찾는다. 날짜는 `## YYYY-MM-DD` 또는 `Date: YYYY-MM-DD`.
    """
    # `## ` 와 `---` 양쪽으로 자른다. 어느 쪽이든 날짜를 못 찾으면 그 조각은 버린다.
    blocks = re.split(r"^(?:## |---\s*$)", text, flags=re.M)
    for block in blocks:
        m = (re.match(r"\s*(\d{4}-\d{2}-\d{2})", block)
             or re.search(r"^\s*Date\s*:\s*(\d{4}-\d{2}-\d{2})", block, flags=re.M))
        if not m:
            continue
        learned = m.group(1)

        # 여러 Original 이 있으면 마지막이 선호형이다 (기존 동작 유지).
        # **`Original Korean:` 은 제외한다** — 한국어 원문이지 학습할 영어가 아니다.
        # 옛 정규식이 이걸 먹어서 카드 표현이 한국어로 들어갔다 (2026-08-18).
        # 접미사도 같이 잡는다 — `- Original 2:` 의 「2」로 Korean/Rhythm/Pronunciation 을 짝지어야 한다.
        # 안 그러면 2번 문장을 표현으로 쓰면서 1번 문장의 리듬·발음을 붙이게 된다.
        originals = re.findall(r"^- Original(?!\s+Korean)([^:]*):\s*(.+)$", block, flags=re.M)
        idx = ""
        if originals:
            suffix, chosen = originals[-1]
            expr = chosen.strip()
            m_idx = re.search(r"\d+", suffix)
            idx = m_idx.group(0) if m_idx else ""
        else:
            expr = _label_get(block, WANTED_LABELS["expr"])
        # 그래도 한국어만 잡혔으면 영어 라벨을 다시 뒤진다. 입력 형태가 매번 달라
        # (한글만 / 영문 / 섞임) 어느 라벨에 영어가 오는지 고정할 수 없다.
        if expr and not re.search(r"[A-Za-z]", expr):
            alt = _label_get(block, WANTED_LABELS["expr"])
            if alt and re.search(r"[A-Za-z]", alt):
                ko = ko or expr
                expr = alt
        ko = _label_get(block, WANTED_LABELS["ko"], idx)
        ctx = _label_get(block, WANTED_LABELS["ctx"], idx)
        rh = _label_get(block, WANTED_LABELS["rh"], idx)
        pron = _label_get(block, WANTED_LABELS["pron"], idx)
        ex = _label_get(block, WANTED_LABELS["ex"], idx)

        if not expr:
            # verbose(2026-07) 는 값이 라벨 **다음 줄**에 온다
            expr = (_block_field(block, "Original wanted expression(s)")
                    or _block_field(block, "Original wanted expression"))
            if not expr:
                continue
        ko = ko or _block_field(block, "Korean meaning")

        # 상황이 없으면 `Study focus:` 불릿에서 덩어리 목록을 만든다 (verbose 형식).
        # **이 처리를 expr 분기 안에 두면 안 된다** — 같은 줄에 값이 오는 verbose 블록은
        # 위에서 expr 이 잡혀 분기를 안 타고, 그래서 19건이 상황을 잃었다 (2026-08-17 회귀).
        if not ctx:
            known = re.compile(r"^\s*(%s)\s*:" % "|".join(
                re.escape(l) for ls in WANTED_LABELS.values() for l in ls), re.I)
            focus = [f.strip() for f in re.findall(r"^- (.+)$", block, flags=re.M)
                     if not known.match(f)]
            ctx = _block_field(block, "Possible practical situation")
            if focus:
                ctx = (ctx + "; " if ctx else "") + "reusable chunks: " + ", ".join(focus[:8])

        yield learned, expr, ctx, ko, rh, pron, examples_to_variants(ex) if ex else []


def parse_vocab(text):
    """Yield (date, slot, expression, meaning, example) from b2_vocab_log.md."""
    current = None  # (date, slot)
    for line in text.splitlines():
        h = re.match(r"^## (\d{4}-\d{2}-\d{2})\s*\([^)]*\)\s*\[([^\]]+)\]", line)
        if h:
            current = (h.group(1), h.group(2).strip().upper())
            continue
        if current and line.startswith("- "):
            parts = [p.strip() for p in line[2:].split("|")]
            if len(parts) >= 2 and parts[0]:
                example = parts[2] if len(parts) >= 3 else ""
                yield current[0], current[1], parts[0], parts[1], example


# ═══════════ 레슨 원문에서 리듬·발음·확장 뽑기 ═══════════

def _plain(s):
    """비교용 평문 — 리듬 표기와 구두점을 벗기고 소문자로."""
    s = re.sub(r"\*\*", "", s or "")
    s = re.sub(r"[→↘↓↗/]", " ", s)
    s = re.sub(r"[^\w\s']", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def _loose(s):
    """관사를 뺀 비교용 문자열. `issue an OR` 과 `issue the OR` 을 같게 본다 —
    확장 문장은 같은 표현을 관사만 바꿔 쓰는 일이 잦다."""
    return re.sub(r"\s+", " ", re.sub(r"\b(a|an|the)\b", " ", _plain(s))).strip()


def _has_hangul(s):
    return bool(re.search(r"[가-힣]", s or ""))


def list_recent_expressions(token, cutoff):
    """`cutoff`(YYYY-MM-DD) 이후 learnedDate 인 기존 문서의 (loose, expr, source, learned)
    목록. 근접 중복 판정용.

    전체 컬렉션이 아직 수백 건이라 한 번에 받아도 무리 없다 — 나중에 수천 건대가 되면
    `learnedDate >= cutoff` 서버측 필터(structured query)로 바꿀 것.
    """
    out = []
    page_token = None
    url_base = FIRESTORE_URL
    while True:
        url = "%s?pageSize=300" % url_base
        if page_token:
            url += "&pageToken=%s" % page_token
        req = urllib.request.Request(url, headers=api_headers(token), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
        except Exception as e:
            print("WARN dedup fetch failed (skipping dedup this run): %s" % e, file=sys.stderr)
            return []
        for d in data.get("documents", []):
            f = d.get("fields", {})
            learned = f.get("learnedDate", {}).get("stringValue", "")
            source = f.get("source", {}).get("stringValue", "")
            expr = f.get("expression", {}).get("stringValue", "")
            if learned >= cutoff and expr:
                loose = _loose(expr)
                if loose:
                    out.append((loose, expr, source, learned))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return out


def is_near_duplicate(expr, source, learned, recent):
    """`expr` 이 최근 표현들과 근접 중복인가. 중복이면 (True, 매칭된 원문), 아니면 (False, "").

    **(source, learnedDate, expr) 이 전부 같은 항목은 건너뛴다** — 그건 근접 중복이 아니라
    매 실행마다 창 안의 파일을 통째로 재파싱해서 생기는 정상적인 재처리다. `create_doc()` 의
    doc_id 멱등(409)이 이미 처리하므로, 여기서 먼저 걸러 「deduped」로 잘못 세면 안 된다.

    완전 동일 문자열(다른 소스·다른 날짜)은 그보다 느슨한 두 기준으로 본다:
    ① 포함 관계 — 짧은 쪽이 긴 쪽 안에 통째로 들어감 (예: "settle up expenses" ⊂
       "I need to settle up expenses this month.")
    ② 단어 집합 겹침 — 관사 뺀 단어 기준 자카드 유사도가 `DEDUP_JACCARD` 이상 (예: "move this
       to Friday" ~ "push it to Friday"). **짧은 청크(2단어 이하)는 이 기준을 건너뛴다** —
       "eat out"·"get on it" 같은 표현은 단어 하나만 겹쳐도 자카드가 쉽게 0.5를 넘어
       무관한 표현끼리 오탐하기 쉽다.
    """
    loose = _loose(expr)
    if not loose:
        return False, ""
    words = set(loose.split())
    if not words:
        return False, ""
    for r_loose, r_expr, r_source, r_learned in recent:
        if r_source == source and r_learned == learned and r_expr == expr:
            continue  # 같은 (소스·날짜·원문) — 정상 재처리, 근접 중복 판정 대상 아님
        if loose == r_loose or loose in r_loose or r_loose in loose:
            return True, r_loose
        if len(words) <= 2:
            continue
        r_words = set(r_loose.split())
        if not r_words:
            continue
        overlap = len(words & r_words) / len(words | r_words)
        if overlap >= DEDUP_JACCARD:
            return True, r_loose
    return False, ""


def _is_en_line(s):
    """영어 리듬맵 줄인가. 한글이 없고, 라틴 단어가 둘 이상이며, 리듬 표기가 있어야 한다."""
    if not s or _has_hangul(s):
        return False
    if not re.search(r"[*/→↘↓↗]", s):
        return False
    return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", s)) >= 2


def lesson_units(text):
    """레슨 전문에서 (영어 리듬맵, 한글 발음, 한국어 뜻) 단위를 뽑는다.

    **배달 잡마다 출력 형식이 다르다.** 라벨에 의존하면 한쪽이 통째로 누락된다 —
    실제로 10AM 단어 카드가 그래서 빠졌다 (2026-08-17).

      8AM 미션        질문: <리듬맵>      /  발음: <한글>  /  뜻: <한국어>
      10AM 단어 카드  <리듬맵>            /  <한글 발음>   /  <한국어 뜻>     ← 라벨 없음, 위치로
      10AM 확장       확장: 덩어리 · 덩어리                                  ← 문장이 아니라 조각

    그래서 **라벨이 아니라 줄의 생김새**로 판별한다. 영어 리듬맵 줄을 찾고,
    바로 다음 한글 줄을 발음, 그 다음 한글 줄을 뜻으로 본다.

    프롬프트 구간은 반드시 잘라낸다 — 앞쪽 770여 줄이 스킬 문서라 거기 있는
    `{리듬맵 표기 영어}` 같은 템플릿 자리표시자까지 긁어온다.
    """
    cut = [m.end() for m in re.finditer(r"^## Response$", text, flags=re.M)]
    if cut:
        text = text[cut[-1]:]

    lines = [l.strip().rstrip("　 ") for l in text.splitlines()]
    units, seen = [], set()
    in_variants = False
    owner = ""          # 10AM 카드의 대표 덩어리. `확장:` 을 이 표현에 묶어준다

    for i, line in enumerate(lines):
        if line.startswith("【") or line.startswith("━━━"):
            in_variants = "이렇게도" in line or "확장" in line
            if line.startswith("━━━"):
                owner = ""          # 새 카드 시작
        mo = re.match(r"^잘 쓰는 덩어리\s*:\s*(.+)$", line)
        if mo:
            owner = mo.group(1).strip()
            continue

        # 10AM 형식의 `확장: a · b` — 조각 나열이라 발음·뜻이 없다
        mv = re.match(r"^확장\s*:\s*(.+)$", line)
        if mv:
            for frag in re.split(r"\s*[·|]\s*", mv.group(1)):
                frag = frag.strip()
                if frag and frag.lower() not in seen:
                    seen.add(frag.lower())
                    units.append({"en": frag, "pron": "", "ko": "",
                                  "kind": "variant", "owner": owner})
            continue

        en = re.sub(r"^(?:질문|답변)\s*:\s*", "", line)
        en = re.sub(r"^[-*]\s+", "", en).strip()
        if not _is_en_line(en) or "{" in en or "}" in en:
            continue

        pron = ko = ""
        for nxt in lines[i + 1:i + 4]:
            if not nxt:
                continue
            t = re.sub(r"^(발음|뜻)\s*:\s*", "", nxt).strip()
            if re.match(r"^(질문|답변|확장|톤/사용|감정)\s*:", nxt) or nxt.startswith(("【", "━━━")):
                break
            if not _has_hangul(t):
                break
            # 리듬 표기가 남아 있으면 발음, 아니면 뜻
            if not pron and re.search(r"[*/→↘↓↗]", t):
                pron = t
            elif not ko:
                ko = t
                break

        key = re.sub(r"\W+", "", en).lower()
        if key in seen:
            continue
        seen.add(key)
        units.append({"en": en, "pron": pron, "ko": ko, "owner": owner,
                      "kind": "variant" if in_variants else "main"})
    return units


def enrich(expr, units, max_variants=2):
    """표현 하나에 대해 (리듬맵, 발음, 예문 뜻, 확장목록) 을 고른다.

    표현이 실제로 들어간 문장만 쓴다. 못 찾으면 빈 값을 돌려주고 호출부가 필드를
    아예 안 만든다 — 빈 문자열을 넣으면 앱이 「있음」으로 오인해 빈 블록을 그린다.
    """
    key, loose = _plain(expr), _loose(expr)
    if not key:
        return "", "", "", []

    def hit(u):
        # 10AM 카드의 `확장:` 은 조각이라 표현 전체를 포함하지 않는다 —
        # 같은 카드 소속(owner)이면 문자열이 안 겹쳐도 그 표현의 확장이다.
        if u.get("owner") and _loose(u["owner"]) == loose:
            return True
        return key in _plain(u["en"]) or (loose and loose in _loose(u["en"]))

    hits = [u for u in units if hit(u)]
    if not hits:
        return "", "", "", []
    # 예문은 질문/답변에서 고른다. 확장밖에 없으면 그거라도 쓴다.
    mains = [u for u in hits if u["kind"] == "main"] or hits
    main = mains[0]
    variants = [
        {"en": u["en"], "pron": u["pron"], "ko": u["ko"]}
        for u in hits if u["kind"] == "variant" and u["en"] != main["en"]
    ][:max_variants]
    # 예문의 한국어 뜻(`main["ko"]`)은 파서가 이미 뽑아두고도 여기서 버려지고 있었다
    # (2026-08-18 Patrick 지적). 배달 카드 화면에 예문만 영어로 나오던 원인이다.
    return main["en"], main["pron"], main["ko"], variants


def extras_only(data):
    """백필로 덧쓸 필드만 골라낸다. 진도(stage·nextReview)는 절대 포함하지 않는다.

    `ko` 도 넣는다 — 파서를 고쳐 뜻을 되찾아도 백필 대상이 아니면 기존 카드는 계속 비어 있다
    (2026-08-20 번호 붙은 라벨 수정 때 실제로 걸렸다). 막힌 표현의 뜻은 원본 파일이 유일한
    출처이고 앱에 수정 기능이 없으므로, 같은 값을 다시 쓰는 것이라 덮어써도 안전하다.
    값이 있을 때만 필드를 만든다 — 배달 카드는 `ko` 가 "" 라 여기서 걸러진다.
    """
    return {k: data[k] for k in ("rhythm", "pron", "variants", "contextKo", "ko") if data.get(k)}


def add_extras(data, pron, variants):
    """발음·확장을 문서에 붙인다. **값이 있을 때만** 필드를 만든다.

    빈 문자열을 넣으면 앱이 「있음」으로 보고 빈 블록을 그린다 — rhythm 에서 이미 겪은 함정이다.
    확장은 구분자 충돌(리듬맵에 `/`·`|` 가 들어간다)을 피하려고 JSON 문자열로 넣는다.
    """
    if pron:
        data["pron"] = pron
    if variants:
        data["variants"] = json.dumps(variants, ensure_ascii=False)


def examples_to_variants(raw, limit=2):
    """확장 표현 한 줄을 목록으로. 봇이 쓰는 구분자가 두 가지다.

        Examples:            en → ko; en → ko
        Related expressions: 문장1 / 문장2 / 문장3

    `/` 로도 자르되 **리듬 표기가 섞인 줄은 자르지 않는다** — 리듬맵의 청크 구분자도
    ` / ` 라서 한 문장이 조각나 버린다.
    """
    raw = (raw or "").strip()
    sep = r"\s*;\s*"
    if ";" not in raw and not re.search(r"\*\*|[→↘↓↗]", raw):
        sep = r"\s+/\s+"
    out = []
    for chunk in re.split(sep, raw):
        parts = re.split(r"\s*(?:→|->)\s*", chunk.strip(), maxsplit=1)
        en = parts[0].strip().rstrip(".")
        if not en:
            continue
        out.append({"en": en, "pron": "", "ko": parts[1].strip() if len(parts) > 1 else ""})
        if len(out) >= limit:
            break
    return out


_window_cache = {}


def lesson_units_window(today, days):
    """최근 `days` 일치 레슨을 전부 합친 단위 목록. 한 번만 읽고 캐시한다.

    막힌 표현은 **저장된 날 레슨에는 없다** — 봇이 그날 배달한 내용이 아니라
    Patrick이 그날 못 했던 말이기 때문. 대신 봇 규격상 저장된 막힌 표현은
    나중 레슨의 1순위 재료라, 며칠 뒤 레슨에 등장하면 그때 확장 표현을 얻을 수 있다.
    그래서 하루가 아니라 **기간 전체**를 훑는다.
    """
    key = (today.isoformat(), days)
    if key not in _window_cache:
        units = []
        for i in range(days + 1):
            units.extend(lesson_units(read_lesson((today - timedelta(days=i)).isoformat())))
        _window_cache[key] = units
    return _window_cache[key]


def read_lesson(day):
    """해당 날짜의 영어 배달 크론 출력 전문을 이어붙여 돌려준다. 없으면 빈 문자열."""
    import glob
    out = []
    for path in sorted(glob.glob("%s/*/%s_*.md" % (CRON_OUT, day))):
        try:
            with open(path, encoding="utf-8") as f:
                body = f.read()
        except OSError:
            continue
        # **파일마다 응답 구간만 잘라서** 담는다. 파일을 통째로 이어붙이면
        # lesson_units 의 「마지막 `## Response` 뒤부터」가 앞 파일 내용을 통째로 날린다 —
        # 실제로 10AM 단어 카드가 8AM 미션 뒤에 붙어 사라졌다 (2026-08-17).
        cut = [m.end() for m in re.finditer(r"^## Response$", body, flags=re.M)]
        if not cut:
            continue
        tail = body[cut[-1]:]
        if LESSON_MARK_RE.search(tail):     # 리듬 화살표가 있어야 레슨이다
            out.append(tail)
    return "\n\n".join(out)


def speech_text(raw: str) -> str:
    """리듬맵 표기를 벗겨 TTS 에 보낼 문장을 만든다.

    **앱의 plain()/unstressCaps() 와 글자 그대로 같은 규칙이어야 한다.** 어긋나면 캐시 키가
    달라져 미리 만들어 둔 음성을 앱이 못 찾고 처음 재생에서 다시 기다리게 된다.

    대문자를 소문자로 되돌리는 이유: TTS 가 대문자 덩어리를 약어로 보고 철자를 읽는다
    (`UNWIND` → 「유엔윈드」). 우리 표기에서 대문자는 피크 강세일 뿐 약어가 아니다.
    진짜 약어(CUSA·CRBC)는 볼드 밖에 있어 화면에서도 강세가 아니므로 그대로 둔다.
    """
    def bold(m):
        pre, inner, post = m.group(1), m.group(2), m.group(3)
        # 앞뒤에 글자가 붙어 있으면 단어 조각이다 — `de**POS**it` 의 POS 는 약어가 아니다.
        if not pre and not post and SPELL_OUT.fullmatch(inner):
            return inner
        # 여러 단어 피크(`**SAME HERE**`)도 잡아야 해서 공백을 허용한다.
        if re.fullmatch(r"[A-Z][A-Z' ]*", inner):
            return "%s**%s**%s" % (pre, inner.lower(), post)
        return m.group(0)

    # 볼드 안 대문자 = 피크 강세.
    t = re.sub(r"(\w*)\*\*(.+?)\*\*(\w*)", bold, raw)
    # 볼드 밖 대문자도 약어가 아니면 단어로 읽어야 한다 — AQUALINK 같은 회사명이 그렇다.
    # 볼드 유무로 갈리면 같은 이름이 카드마다 다르게 읽힌다. SPELL_OUT 만이 유일한 기준이다.
    t = re.sub(r"[A-Za-z']*[A-Z]{2,}[A-Za-z']*",
               lambda m: m.group(0) if SPELL_OUT.fullmatch(m.group(0)) else m.group(0).lower(),
               t)
    t = t.replace("**", "")
    t = re.sub(r"[→↘↓↗]", " ", t)
    t = re.sub(r"\s+/\s+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def prewarm(texts):
    """새 표현의 음성을 미리 만들어 캐시에 넣는다.

    앱에서 처음 🔊를 눌렀을 때 2초 기다리지 않게 하려는 것. 실패해도 무시한다 —
    앱은 필요할 때 직접 생성하고, 그것도 안 되면 기기 음성으로 폴백한다.
    """
    done = 0
    for raw in texts:
        t = speech_text(raw)
        if not t:
            continue
        for voice in TTS_VOICES:
            url = "%s?t=%s&v=%s&s=%s" % (TTS_URL, urllib.parse.quote(t), voice, TTS_SPEED)
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    r.read()
                done += 1
            except Exception as e:
                print("WARN prewarm failed: %s %s (%s)" % (voice, e, t[:40]), file=sys.stderr)
    return done


def main():
    # --backfill: 이미 있는 문서에 새 필드(rhythm·pron·variants)만 덧붙인다.
    # 진도(stage·nextReview)는 건드리지 않는다. 평소 크론은 이 모드를 쓰지 않는다.
    backfill = "--backfill" in sys.argv
    today = today_manila()
    token = get_id_token()
    cutoff = (today - timedelta(days=BACKFILL_DAYS)).isoformat()
    # `--days N` 은 **배달 카드 범위만** 넓힌다. 예문 뜻(`contextKo`) 처럼 나중에 추가한 필드를
    # 과거 카드에 소급해 채울 때 쓴다. 배달 카드의 재료는 `lessons[learned]` — 그 카드가
    # 배달된 날의 레슨 하나뿐이라 범위를 넓혀도 엉뚱한 문장이 붙지 않는다.
    # **막힌 표현은 7일에 고정한다.** 그쪽은 `lesson_units_window` 로 기간 전체를 훑는 구조라
    # 범위를 넓히면 몇 달 전 표현에 무관한 레슨의 리듬·발음이 붙는다.
    days_deliv = BACKFILL_DAYS
    for i, a in enumerate(sys.argv):
        if a == "--days" and i + 1 < len(sys.argv):
            days_deliv = max(BACKFILL_DAYS, int(sys.argv[i + 1]))
    cutoff_deliv = (today - timedelta(days=days_deliv)).isoformat()
    created = skipped = patched = deduped = 0

    fresh = []   # 새로 만든 문서의 읽어줄 텍스트 — 음성을 미리 만들어 둔다

    # 근접 중복 방지용 최근 표현 목록. 이번 실행에서 새로 만드는 것도 바로 추가해서
    # wanted → delivered 순서로 같은 표현이 연달아 들어와도 걸러지게 한다.
    dedup_cutoff = (today - timedelta(days=DEDUP_DAYS)).isoformat()
    recent_loose = list_recent_expressions(token, dedup_cutoff)

    for learned, expr, ctx, ko, rhythm, pron, variants in parse_wanted(
            read(BASE + "/wanted_phrases.md")):
        if learned < cutoff or not expr:
            continue
        is_dup, matched = is_near_duplicate(expr, "hermes-wanted", learned, recent_loose)
        if is_dup:
            deduped += 1
            print("DEDUP wanted %s: %r ~= %r" % (learned, expr, matched), file=sys.stderr)
            continue
        did = doc_id("hermes-wanted", learned, expr)
        data = {
            "expression": expr, "meaning": "", "context": ctx, "ko": ko,
            "source": "hermes-wanted", "slot": "", "learnedDate": learned,
            "stage": 0, "nextReview": next_review_for(learned, today),
        }
        # 리듬이 온 경우에만 필드를 만든다. 빈 문자열을 넣으면 앱이 "리듬 있음"으로
        # 오인해 평문 정답 대신 빈 화면을 그린다. pron·variants 도 같은 원칙.
        # 봇이 확장(Examples)을 안 보내는 형식으로 바뀌었다. 레슨 원문에서 같은 표현을
        # 찾아 확장·발음을 채운다 (2026-08-18 Patrick 요청 — C안).
        # **봇이 준 값이 있으면 그대로 둔다** — 레슨 것으로 덮어쓰지 않는다.
        if not variants or not pron:
            # 막힌 표현은 `ko` 에 이미 제 뜻이 있고 예문 블록 자체를 안 그린다 — 예문 뜻은 안 쓴다.
            l_rh, l_pron, _l_ko, l_var = enrich(expr, lesson_units_window(today, BACKFILL_DAYS))
            pron = pron or l_pron
            variants = variants or l_var
            rhythm = rhythm or l_rh
        if rhythm:
            data["rhythm"] = rhythm
        add_extras(data, pron, variants)
        if create_doc(did, data, token):
            created += 1
            fresh.append(expr)
            recent_loose.append((_loose(expr), expr, "hermes-wanted", learned))
        else:
            skipped += 1
            if backfill:
                patched += patch_doc(did, extras_only(data), token)

    # 레슨 전문은 날짜당 한 번만 읽어 캐시한다 (파일이 90KB대라 표현마다 읽으면 낭비다).
    lessons = {}
    for learned, slot, expr, meaning, example in parse_vocab(read(BASE + "/b2_vocab_log.md")):
        if learned < cutoff_deliv or not expr:
            continue
        is_dup, matched = is_near_duplicate(expr, "hermes-delivered", learned, recent_loose)
        if is_dup:
            deduped += 1
            print("DEDUP delivered %s: %r ~= %r" % (learned, expr, matched), file=sys.stderr)
            continue
        if learned not in lessons:
            lessons[learned] = lesson_units(read_lesson(learned))
        rhythm, pron, ctx_ko, variants = enrich(expr, lessons[learned])

        did = doc_id("hermes-delivered", learned, expr)
        data = {
            "expression": expr, "meaning": meaning, "context": example, "ko": "",
            "source": "hermes-delivered", "slot": slot, "learnedDate": learned,
            "stage": 0, "nextReview": next_review_for(learned, today),
        }
        # 로그의 `example` 은 평문이다. 레슨 원문에서 같은 문장의 리듬맵을 찾으면 그걸 쓴다 —
        # 화면에 강세·청크가 보여야 쉐도잉이 된다.
        #
        # **`rhythm` 필드가 아니라 `context`(예문) 에 넣는다.** 배달 카드의 학습 단위는
        # `eat out` 같은 덩어리지 문장 전체가 아니다. `rhythm` 에 넣으면 카드 앞면이
        # 덩어리 대신 문장으로 바뀌고, 예문 블록이 같은 문장을 평문으로 또 보여준다
        # (2026-08-17 화면에서 확인). 막힌 표현(wanted)은 문장 자체가 학습 단위라 그쪽은 rhythm 이 맞다.
        if rhythm:
            data["context"] = rhythm
        # 예문의 한국어 뜻. **기존 `ko` 에 넣으면 안 된다** — `promptFor()` 가 `ko` 를 먼저 보므로
        # 복습 한→영 앞면이 "이 예문 전체를 영작하라"로 바뀐다. 이 카드의 학습 단위는
        # `make a billing adjustment` 같은 덩어리지 문장 전체가 아니다.
        # 값이 있을 때만 필드를 만든다 (빈 문자열 = 앱이 「있음」으로 오인).
        if ctx_ko:
            data["contextKo"] = ctx_ko
        add_extras(data, pron, variants)
        if create_doc(did, data, token):
            created += 1
            fresh.extend([expr, example])
            recent_loose.append((_loose(expr), expr, "hermes-delivered", learned))
        else:
            skipped += 1
            if backfill:
                # 예문(context)에 리듬맵을 덧쓰고, 배달 카드에 잘못 들어갔던 rhythm 은 지운다.
                # rhythm 이 남아 있으면 앞면이 덩어리 대신 문장으로 나온다 (2026-08-17 실수).
                fields = extras_only(data)
                if data.get("context"):
                    fields["context"] = data["context"]
                patched += patch_doc(did, fields, token, clear=["rhythm"])

    warmed = prewarm(fresh)
    print("%s sync done: created=%d skipped=%d deduped=%d patched=%d tts_warmed=%d"
          % (today.isoformat(), created, skipped, deduped, patched, warmed))


if __name__ == "__main__":
    main()
