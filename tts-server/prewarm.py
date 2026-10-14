#!/usr/bin/env python3
"""english_expressions 에서 **앱이 🔊 로 읽을 수 있는 모든 문장**의 음성을 미리 만든다.

VPS 안에서 돌린다 — 내부 IP 라 레이트 리밋 면제.

왜 필요한가 (2026-10-14): 캐시에 없는 문장은 첫 재생 때 서버가 그 자리에서 합성하는데,
429(레이트 리밋)·500(합성 실패)이면 앱이 **조용히 기기 음성으로 폴백**한다. 필러·연결어·한영매칭
교정처럼 기존 카드의 `expression` 을 PATCH 로 바꾼 작업은 프리워밍이 없어 전부 캐시 미스였다.
`hermes-sync.py` 의 prewarm 은 **새로 만든 카드**의 표현·예문만 다룬다.

대상 칸: expression · rhythm · question · context(예문) · variants(en, ex) · useCases(en) · chunks.
**글자 가공은 서버 clean() 에 맡긴다** — 앱 speechText() 와 같은 규칙이고 멱등이라, 원문(리듬 표기
포함)을 그대로 보내도 앱이 보내는 문장과 같은 캐시 키가 나온다.

사용:  python prewarm.py [음성,쉼표로] [속도]      기본 Emma,Puck / 0.9
       (index.html 의 기본 음성·TTS_SPEED, hermes-sync.py 의 TTS_VOICES·TTS_SPEED 와 같아야 한다)
"""
import json, re, sys, time, urllib.parse, urllib.request

API_KEY = "AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
PROJECT = "english-tracker-cea9f"
TTS = "http://127.0.0.1:8080/tts"
VOICES = (sys.argv[1] if len(sys.argv) > 1 else "Emma,Puck").split(",")
SPEED = sys.argv[2] if len(sys.argv) > 2 else "0.9"

# API 키에 HTTP 리퍼러 제한이 걸려 있다. hermes-sync.py 의 APP_REFERER 와 같은 값이어야 한다.
APP_REFERER = "https://jameskim01115-hub.github.io/english-tracker/"


def token():
    u = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    r = urllib.request.Request(u, data=b'{"returnSecureToken":true}',
                               headers={"Content-Type": "application/json",
                                        "Referer": APP_REFERER}, method="POST")
    return json.load(urllib.request.urlopen(r, timeout=20))["idToken"]


def all_docs(tok):
    """페이지를 넘겨 전부 읽는다 — 한 번에 300개만 읽으면 옛 카드가 빠진다."""
    base = (f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)"
            f"/documents/english_expressions?pageSize=300")
    page = ""
    while True:
        r = urllib.request.Request(base + page, headers={"Authorization": f"Bearer {tok}",
                                                         "Referer": APP_REFERER})
        j = json.load(urllib.request.urlopen(r, timeout=30))
        yield from j.get("documents", [])
        nxt = j.get("nextPageToken")
        if not nxt:
            return
        page = "&pageToken=" + urllib.parse.quote(nxt)


def g(f, k):
    return f.get(k, {}).get("stringValue", "")


def json_list(s):
    try:
        v = json.loads(s) if s else []
        return v if isinstance(v, list) else []
    except ValueError:
        return []


CHUNK_RE = re.compile(r"reusable chunks?\s*:", re.I)


def texts_of(f):
    out = [g(f, "expression"), g(f, "rhythm"), g(f, "question")]
    ctx = g(f, "context")
    if ctx and not CHUNK_RE.search(ctx):       # 막힌 표현의 context 는 「태그; chunks」 — 읽지 않는다
        out.append(ctx)
    for v in json_list(g(f, "variants")):
        if isinstance(v, dict):
            out += [str(v.get("en") or ""), str(v.get("ex") or "")]
    for c in json_list(g(f, "useCases")):
        if isinstance(c, dict):
            out.append(str(c.get("en") or ""))
    out += g(f, "chunks").split("|")
    return out


def main():
    texts, seen = [], set()
    for d in all_docs(token()):
        for t in texts_of(d["fields"]):
            t = t.strip()
            if t and t not in seen:
                seen.add(t)
                texts.append(t)

    print(f"대상 {len(texts)}문장 x {len(VOICES)}음성 = {len(texts) * len(VOICES)}")
    gen = hit = err = 0
    for i, t in enumerate(texts, 1):
        for v in VOICES:
            url = f"{TTS}?t={urllib.parse.quote(t)}&v={v}&s={SPEED}"
            try:
                t0 = time.time()
                with urllib.request.urlopen(url, timeout=120) as r:
                    n = len(r.read())
                el = time.time() - t0
                if el < 0.3:
                    hit += 1
                else:
                    gen += 1
                if el >= 0.3:       # 새로 만든 것만 찍는다 — 캐시 히트는 소음
                    print(f"  [{i}/{len(texts)}] {v} {el:5.2f}s {n:6d}B  {t[:46]}")
            except Exception as e:
                err += 1
                print(f"  [{i}/{len(texts)}] {v} ERROR {e}  {t[:40]}", file=sys.stderr)
    print(f"완료 — 생성 {gen} / 캐시 {hit} / 실패 {err}")
    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
