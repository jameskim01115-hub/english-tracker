#!/usr/bin/env python3
"""TTS 릴레이 — english-tracker 전용. 엔진 2개(Supertonic 3 / Microsoft Neural).

왜 있는가: iOS Safari가 다운로드한 Apple 프리미엄 음성을 웹페이지에 노출하지 않아
아이폰에서는 기계음(Samantha)밖에 못 쓴다. 서버가 음성을 만들어 mp3로 내려주면
맥·아이폰·아이패드에서 같은 품질이 나온다.

GET /tts?t=<text>&v=<voice>&s=<speed>[&ssml=1]  -> audio/mpeg
GET /health                                     -> ok

음성 이름으로 엔진이 갈린다 — `F1`~`M5`는 Supertonic, 그 외는 Microsoft Neural(`NEURAL_VOICES`).
2026-08-15 블라인드 청취에서 Azure Emma가 유일하게 만점(★5)을 받아 추가했다.
Supertonic은 그대로 두고 폴백으로 남긴다 — 기존 카드·프리워밍 캐시가 전부 그쪽이다.

`ssml=1`이면 `t`를 Patrick의 리듬 표기(`**강세**`·`/`·`↘`)로 보고 SSML을 만든다.
없으면 예전처럼 평문 취급 — 기존 앱 호출은 한 글자도 안 바뀐다.

생성된 mp3는 디스크에 캐시된다. 표현 하나당 평생 한 번만 생성된다.
"""
import hashlib
import io
import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
import soundfile as sf

from helper import load_text_to_speech, load_voice_style

ASSETS = os.environ.get("TTS_ASSETS", "/assets")
CACHE = os.environ.get("TTS_CACHE", "/cache")
PORT = int(os.environ.get("TTS_PORT", "8080"))

VOICES = {f"{g}{i}" for g in ("F", "M") for i in range(1, 6)}
DEFAULT_VOICE = "F1"
MAX_CHARS = 400
TOTAL_STEP = 8

# ══════════════ Microsoft Neural 음성 ══════════════
# 전송 경로가 둘이고 **소리는 완전히 같다** — 같은 Azure 음성 모델이기 때문이다.
#
#   AZURE_SPEECH_KEY 있음 → Azure REST (공식, SSML 로 강세·끊어읽기 재현 가능)
#   없음                 → edge-tts   (키 불필요, 비공식, SSML 불가 — rate 만)
#
# Patrick은 카드 등록을 피하려고 edge-tts(A안)를 골랐다. 나중에 키만 넣으면
# 목소리 변화 없이 Azure 로 승격된다 — 그래서 음성 이름을 공유한다.
AZURE_KEY = os.environ.get("AZURE_SPEECH_KEY", "").strip()
AZURE_REGION = os.environ.get("AZURE_SPEECH_REGION", "southeastasia").strip()

# Patrick이 2026-08-15 블라인드 청취에서 직접 채점한 8개만 넣는다.
# Emma가 유일한 ★5. 나머지는 ★4대. 들어보지 않은 음성은 넣지 않는다.
NEURAL_VOICES = {
    "Emma":    "en-US-EmmaNeural",               # ★5 — 기본값
    "Ava":     "en-US-AvaNeural",
    "AvaM":    "en-US-AvaMultilingualNeural",
    "Jenny":   "en-US-JennyNeural",
    "Andrew":  "en-US-AndrewNeural",
    "AndrewM": "en-US-AndrewMultilingualNeural",
    "Brian":   "en-US-BrianNeural",
    "BrianM":  "en-US-BrianMultilingualNeural",
}

# F0 무료 티어는 월 50만 자. 5만 자를 여유로 남긴다.
# 이 가드가 없으면 루프 버그 하나로 한 달치를 태우고 그 뒤 조용히 실패한다.
AZURE_MONTHLY_CHARS = 450_000
_usage_path = os.path.join(CACHE, "azure_usage.json")
_usage_lock = threading.Lock()

# 철자로 읽어야 하는 약어. 앱 index.html 의 SPELL_OUT 과 같은 목록이어야 한다.
SPELL_OUT = {"CUSA", "CRBC", "CRLC", "OR", "BIR", "VAT", "SSS", "AEP",
             "LOI", "NTE", "PO", "STF", "DPR", "BFP", "NTC", "FSIC"}

# CORS — 앱 출처만 허용. curl 은 못 막지만 브라우저 오용은 막는다.
ALLOWED_ORIGINS = {
    "https://jameskim01115-hub.github.io",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
}

# 생성(캐시 미스)만 제한한다. 캐시 히트는 무제한 — CPU를 안 쓴다.
RATE_MAX = 80          # IP당 (Supertonic — VPS CPU를 쓰므로 낮게)
RATE_MAX_AZURE = 400   # IP당 (Azure — 네트워크 호출이라 CPU 부담 없음. 진짜 상한은 월 문자 수)
RATE_WINDOW = 3600     # 초

os.makedirs(CACHE, exist_ok=True)

_lock = threading.Lock()          # ONNX 세션 직렬화
_rate = {}                        # ip -> deque[timestamp]
_rate_lock = threading.Lock()
_styles = {}

print("모델 로딩 중…", flush=True)
_tts = load_text_to_speech(os.path.join(ASSETS, "onnx"), False)
_sample_rate = _tts.sample_rate
print(f"모델 로딩 완료 (sample_rate={_sample_rate})", flush=True)


def style_for(voice):
    if voice not in _styles:
        _styles[voice] = load_voice_style([os.path.join(ASSETS, "voice_styles", f"{voice}.json")])
    return _styles[voice]


def clean(text):
    """앱이 보내는 리듬 마크업을 읽기용 평문으로 되돌린다.

    **대문자 강세도 반드시 여기서 벗긴다.** 안 그러면 TTS 가 약어로 보고 철자를 읽는다
    (`UNWIND` → 「유엔윈드」). 예전에는 앱이 `plain()` 으로 미리 소문자화해서 보냈지만,
    「발음」 탭이 SSML 을 쓰려고 **원문을 그대로** 보내기 시작하면서 이 처리가 비었다 —
    2026-08-15 에 `STAND` 가 대문자로 통과하는 걸 서버 로그에서 발견했다.

    이미 소문자화된 입력에는 아무 영향이 없어 기존 캐시 키도 그대로다(멱등).
    """
    t = unstress_caps(text)
    t = t.replace("**", "")
    t = re.sub(r"[→↘↓↗]", " ", t)
    t = re.sub(r"\s+/\s+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:MAX_CHARS]


def unstress_caps(text):
    """대문자 강세 표기를 소문자로 되돌린다. 앱 index.html 의 unstressCaps 와 같은 규칙.

    TTS 는 대문자 덩어리를 약어로 보고 철자를 읽는다 — `UNWIND` 가 「유엔윈드」로 나왔다.
    우리 표기에서 대문자는 피크 강세일 뿐이므로 벗겨야 한다. `SPELL_OUT` 만이 예외다.
    """
    def in_bold(m):
        pre, inner, post = m.group(1), m.group(2), m.group(3)
        if re.fullmatch(r"[A-Z][A-Z' ]*", inner) and not (not pre and not post and inner in SPELL_OUT):
            return f"{pre}**{inner.lower()}**{post}"
        return m.group(0)

    t = re.sub(r"(\w*)\*\*(.+?)\*\*(\w*)", in_bold, text)
    # 볼드 밖 대문자도 약어가 아니면 단어로 읽어야 한다 (AQUALINK 같은 회사명).
    return re.sub(r"[A-Za-z']*[A-Z]{2,}[A-Za-z']*",
                  lambda m: m.group(0) if m.group(0) in SPELL_OUT else m.group(0).lower(), t)


# 청크 자리표시자. 사용자 텍스트에 들어올 수 없고 XML 이스케이프가 만들어내지도 않는 문자.
BR = "\x00"


def _xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_ssml(marked, azure_voice, speed):
    """Patrick 의 리듬 표기를 SSML 로 옮긴다.

    `plain()` 이 강세·끊어읽기를 전부 지워서 TTS 가 밋밋하게 읽던 문제를 여기서 되돌린다 —
    화면에서 보는 리듬과 귀로 듣는 소리를 일치시키는 것이 이 함수의 존재 이유다.

    | 표기 | SSML |
    |---|---|
    | `**대문자**` (피크) | `<emphasis level="strong">` |
    | `**소문자**` (일반 강세) | `<emphasis level="moderate">` |
    | `/` (청크) | `<break time="180ms"/>` |
    | `↘` `↓` (하강) | 마침표 — 문장 경계가 살아야 억양이 내려간다 |
    | `→` `↗` | 삭제 (억양 유지, 소리에는 영향 없음) |
    """
    peaks = []            # 원문의 볼드가 피크였는지 기억해 둔다 (소문자화 전에)
    for m in re.finditer(r"\*\*(.+?)\*\*", marked):
        peaks.append(bool(re.fullmatch(r"[A-Z][A-Z' ]*", m.group(1))))

    t = unstress_caps(marked.replace(BR, ""))
    t = re.sub(r"[↘↓]", ".", t)
    t = re.sub(r"[→↗]", " ", t)
    # 청크 `/` 는 태그를 만들기 **전에** 자리표시자로 바꾼다.
    # 나중에 치환하면 `</emphasis>` 의 슬래시까지 먹어 XML 이 깨진다 (실제로 겪음).
    t = re.sub(r"\s*/\s*", BR, t)

    out, idx, pos = [], 0, 0
    for m in re.finditer(r"\*\*(.+?)\*\*", t):
        out.append(_xml_escape(t[pos:m.start()]))
        level = "strong" if (idx < len(peaks) and peaks[idx]) else "moderate"
        out.append(f'<emphasis level="{level}">{_xml_escape(m.group(1))}</emphasis>')
        idx, pos = idx + 1, m.end()
    out.append(_xml_escape(t[pos:]))

    body = "".join(out)
    # 짝이 안 맞는 `**` 는 남는다 — 자유 입력창에서 닫는 걸 잊으면 별표가 그대로 읽힌다.
    body = body.replace("**", "")
    body = re.sub(r"\.\s*\.", ".", body)          # ↘ 뒤에 마침표가 이미 있던 경우
    body = re.sub(r"[ \t]+", " ", body).strip()
    body = body.replace(BR, '<break time="180ms"/>')

    pct = int(round((speed - 1.0) * 100))
    return (f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
            f"<voice name='{azure_voice}'>"
            f"<prosody rate='{pct:+d}%'>{body}</prosody></voice></speak>")


def azure_usage(add=0):
    """이번 달 사용 문자 수. add>0 이면 더하고 나서 반환한다."""
    month = time.strftime("%Y-%m")
    with _usage_lock:
        try:
            with open(_usage_path) as f:
                u = json.load(f)
        except Exception:
            u = {}
        if u.get("month") != month:
            u = {"month": month, "chars": 0}
        if add:
            u["chars"] = u.get("chars", 0) + add
            tmp = _usage_path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(u, f)
            os.replace(tmp, _usage_path)
        return u.get("chars", 0)


def azure_synth(text, voice, speed, use_ssml):
    """Azure Neural 음성으로 mp3 바이트를 만든다. 캐시는 상위 synth() 가 담당한다."""
    if not AZURE_KEY:
        raise RuntimeError("AZURE_SPEECH_KEY not set")

    azure_voice = NEURAL_VOICES[voice]
    if use_ssml:
        payload = build_ssml(text, azure_voice, speed)
        billed = len(re.sub(r"<[^>]+>", "", payload))
    else:
        pct = int(round((speed - 1.0) * 100))
        payload = (f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
                   f"<voice name='{azure_voice}'>"
                   f"<prosody rate='{pct:+d}%'>{_xml_escape(text)}</prosody></voice></speak>")
        billed = len(text)

    used = azure_usage()
    if used + billed > AZURE_MONTHLY_CHARS:
        raise RuntimeError(f"azure monthly quota guard: {used}/{AZURE_MONTHLY_CHARS}")

    req = urllib.request.Request(
        f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=payload.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": AZURE_KEY,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "english-tracker-tts",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    azure_usage(add=billed)
    return data


def edge_synth(text, voice, speed):
    """edge-tts 로 mp3 바이트를 만든다 — Azure 키 없이 같은 Neural 음성을 받는다.

    Microsoft 가 Edge 브라우저가 만들지 않는 SSML 을 차단하므로 **커스텀 SSML 은 못 쓴다.**
    조절 가능한 건 rate·volume·pitch 뿐이라 강세·끊어읽기는 재현되지 않는다 —
    그게 필요해지면 AZURE_SPEECH_KEY 를 넣어 Azure 경로로 승격하면 된다(목소리는 동일).
    """
    import asyncio

    import edge_tts   # 지연 임포트 — 없어도 Supertonic 경로는 계속 살아야 한다

    pct = int(round((speed - 1.0) * 100))

    async def run():
        comm = edge_tts.Communicate(text, NEURAL_VOICES[voice], rate=f"{pct:+d}%")
        buf = bytearray()
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                buf += chunk["data"]
        return bytes(buf)

    # ThreadingHTTPServer 라 요청마다 스레드가 다르다 — 스레드별로 새 루프를 판다.
    data = asyncio.run(run())
    if not data:
        raise RuntimeError("edge-tts returned empty audio")
    return data


def neural_synth(text, voice, speed, use_ssml):
    """Microsoft Neural 음성. 키가 있으면 Azure 공식 경로, 없으면 edge-tts."""
    if AZURE_KEY:
        return azure_synth(text, voice, speed, use_ssml)
    return edge_synth(text, voice, speed)


def is_internal(ip):
    """VPS 내부(프리워밍·동기화 크론)는 제한하지 않는다."""
    return (ip.startswith("127.") or ip.startswith("10.") or ip.startswith("192.168.")
            or ip == "::1" or any(ip.startswith(f"172.{n}.") for n in range(16, 32)))


def rate_ok(ip, azure=False):
    if is_internal(ip):
        return True
    now = time.time()
    limit = RATE_MAX_AZURE if azure else RATE_MAX
    bucket = f"{ip}|azure" if azure else ip
    with _rate_lock:
        q = _rate.setdefault(bucket, deque())
        while q and now - q[0] > RATE_WINDOW:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True


def cache_key(text, voice, speed, use_ssml):
    """캐시 키. 음성 이름이 엔진을 구분하므로(F1..M5 vs Emma..) 엔진을 따로 넣지 않아도 안 겹친다.
    다만 같은 음성·같은 문장이라도 SSML 유무로 소리가 다르므로 그건 키에 넣는다."""
    tag = f"{voice}|{speed}|{'ssml|' if use_ssml else ''}{text}"
    return hashlib.sha1(tag.encode("utf-8")).hexdigest()


def synth(text, voice, speed, use_ssml=False):
    """mp3 바이트 반환. 캐시가 있으면 그대로 준다."""
    path = os.path.join(CACHE, f"{cache_key(text, voice, speed, use_ssml)}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            return f.read(), True

    if voice in NEURAL_VOICES:
        # 네트워크 호출이라 ONNX 락을 잡지 않는다 — 잡으면 동시 요청이 줄줄이 밀린다.
        data = neural_synth(text, voice, speed, use_ssml)
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
        return data, False

    with _lock:
        # 락 안에서 다시 확인 — 동시 요청이 같은 문장을 두 번 만들지 않게
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "rb") as f:
                return f.read(), True
        wav, duration = _tts(text, "en", style_for(voice), TOTAL_STEP, speed)

    audio = np.asarray(wav)
    if audio.ndim > 1:
        audio = audio[0]
    # duration 이 실제 발화 길이 — 뒤에 붙는 패딩을 잘라낸다
    dur = float(np.asarray(duration).reshape(-1)[0])
    end = min(len(audio), int(dur * _sample_rate))
    if end > 0:
        audio = audio[:end]

    buf = io.BytesIO()
    sf.write(buf, audio, _sample_rate, format="MP3")
    data = buf.getvalue()

    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)   # 부분 파일이 캐시로 남지 않게
    return data, False


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "supertonic-relay"

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} {fmt % args}", flush=True)

    def _cors(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def _send(self, code, body, ctype="application/json; charset=utf-8", cache=False):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if cache:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)

        if u.path == "/health":
            n = len([f for f in os.listdir(CACHE) if f.endswith(".mp3")])
            self._send(200, json.dumps({
                "ok": True, "cached": n,
                "voices": sorted(VOICES),
                "neural": {
                    "transport": "azure" if AZURE_KEY else "edge-tts",
                    "ssml": bool(AZURE_KEY),
                    "region": AZURE_REGION if AZURE_KEY else None,
                    "voices": sorted(NEURAL_VOICES),
                    "chars_this_month": azure_usage() if AZURE_KEY else None,
                    "monthly_cap": AZURE_MONTHLY_CHARS if AZURE_KEY else None,
                },
            }))
            return

        if u.path != "/tts":
            self._send(404, json.dumps({"error": "not found"}))
            return

        voice = q.get("v", [DEFAULT_VOICE])[0]
        is_neural = voice in NEURAL_VOICES
        if not is_neural and voice not in VOICES:
            voice = DEFAULT_VOICE

        # ssml=1 은 **Azure 키가 있을 때만** 켜진다.
        # Supertonic 은 SSML 을 못 읽고, edge-tts 는 커스텀 SSML 이 차단돼 있다.
        # 키 없이 켜면 `**`·`/` 가 그대로 소리로 읽힌다 — 「별표 별표 스탠드」.
        use_ssml = is_neural and bool(AZURE_KEY) and q.get("ssml", ["0"])[0] == "1"
        raw = q.get("t", [""])[0]
        # SSML 모드에서만 리듬 표기를 살린다. 그 외에는 전부 평문으로 벗긴다.
        text = raw[:MAX_CHARS].strip() if use_ssml else clean(raw)
        if not text:
            self._send(400, json.dumps({"error": "t (text) required"}))
            return

        try:
            speed = max(0.7, min(1.3, float(q.get("s", ["1.0"])[0])))
        except ValueError:
            speed = 1.0
        speed = round(speed, 2)

        # 캐시에 이미 있으면 레이트 리밋을 적용하지 않는다
        cached = os.path.exists(os.path.join(CACHE, f"{cache_key(text, voice, speed, use_ssml)}.mp3"))
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        # Azure 는 VPS CPU 를 안 쓰므로 생성 제한이 훨씬 느슨해도 된다.
        # 발음 탭은 자유 입력이라 요청이 전부 캐시 미스다 — 80/시간이면 몇 분 만에 막힌다.
        if not cached and not rate_ok(ip, azure=is_neural):
            self._send(429, json.dumps({"error": "rate limited"}))
            return

        try:
            t0 = time.time()
            data, hit = synth(text, voice, speed, use_ssml)
            print(f"{'HIT ' if hit else 'GEN '} {voice}{'/ssml' if use_ssml else ''} "
                  f"{time.time()-t0:.2f}s {len(data)}B "
                  f"ip={ip}{'(internal)' if is_internal(ip) else ''} "
                  f"{text[:50]!r}", flush=True)
            self._send(200, data, "audio/mpeg", cache=True)
        except Exception as e:
            print(f"ERROR: {voice} {e}", flush=True)
            self._send(500, json.dumps({"error": "synthesis failed"}))


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"listening on :{PORT}", flush=True)
    srv.serve_forever()
