#!/usr/bin/env python3
"""Supertonic 3 TTS 릴레이 — english-tracker 전용.

왜 있는가: iOS Safari가 다운로드한 Apple 프리미엄 음성을 웹페이지에 노출하지 않아
아이폰에서는 기계음(Samantha)밖에 못 쓴다. 서버가 음성을 만들어 mp3로 내려주면
맥·아이폰·아이패드에서 같은 품질이 나온다.

GET /tts?t=<text>&v=<F1..M5>&s=<speed>  -> audio/mpeg
GET /health                            -> ok

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

# CORS — 앱 출처만 허용. curl 은 못 막지만 브라우저 오용은 막는다.
ALLOWED_ORIGINS = {
    "https://jameskim01115-hub.github.io",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
}

# 생성(캐시 미스)만 제한한다. 캐시 히트는 무제한 — CPU를 안 쓴다.
RATE_MAX = 80          # IP당
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
    """앱이 보내는 리듬 마크업을 읽기용 평문으로 되돌린다."""
    t = text.replace("**", "")
    t = re.sub(r"[→↘↓↗]", " ", t)
    t = re.sub(r"\s+/\s+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:MAX_CHARS]


def is_internal(ip):
    """VPS 내부(프리워밍·동기화 크론)는 제한하지 않는다."""
    return (ip.startswith("127.") or ip.startswith("10.") or ip.startswith("192.168.")
            or ip == "::1" or any(ip.startswith(f"172.{n}.") for n in range(16, 32)))


def rate_ok(ip):
    if is_internal(ip):
        return True
    now = time.time()
    with _rate_lock:
        q = _rate.setdefault(ip, deque())
        while q and now - q[0] > RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_MAX:
            return False
        q.append(now)
        return True


def synth(text, voice, speed):
    """mp3 바이트 반환. 캐시가 있으면 그대로 준다."""
    key = hashlib.sha1(f"{voice}|{speed}|{text}".encode("utf-8")).hexdigest()
    path = os.path.join(CACHE, f"{key}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            return f.read(), True

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
            self._send(200, json.dumps({"ok": True, "cached": n, "voices": sorted(VOICES)}))
            return

        if u.path != "/tts":
            self._send(404, json.dumps({"error": "not found"}))
            return

        text = clean(q.get("t", [""])[0])
        if not text:
            self._send(400, json.dumps({"error": "t (text) required"}))
            return
        voice = q.get("v", [DEFAULT_VOICE])[0]
        if voice not in VOICES:
            voice = DEFAULT_VOICE
        try:
            speed = max(0.7, min(1.3, float(q.get("s", ["1.0"])[0])))
        except ValueError:
            speed = 1.0
        speed = round(speed, 2)

        # 캐시에 이미 있으면 레이트 리밋을 적용하지 않는다
        key = hashlib.sha1(f"{voice}|{speed}|{text}".encode("utf-8")).hexdigest()
        cached = os.path.exists(os.path.join(CACHE, f"{key}.mp3"))
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        if not cached and not rate_ok(ip):
            self._send(429, json.dumps({"error": "rate limited"}))
            return

        try:
            t0 = time.time()
            data, hit = synth(text, voice, speed)
            print(f"{'HIT ' if hit else 'GEN '} {voice} {time.time()-t0:.2f}s "
                  f"{len(data)}B ip={ip}{'(internal)' if is_internal(ip) else ''} "
                  f"{text[:50]!r}", flush=True)
            self._send(200, data, "audio/mpeg", cache=True)
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            self._send(500, json.dumps({"error": "synthesis failed"}))


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"listening on :{PORT}", flush=True)
    srv.serve_forever()
