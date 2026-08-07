#!/usr/bin/env python3
"""english_expressions 의 표현·예문 음성을 미리 생성해 캐시를 채운다.
VPS 내부에서 실행 — 레이트 리밋 면제. 크론 sync 뒤에 이어서 돌려도 된다."""
import json, re, sys, time, urllib.parse, urllib.request

API_KEY = "AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
PROJECT = "english-tracker-cea9f"
TTS = "http://127.0.0.1:8080/tts"
VOICES = (sys.argv[1] if len(sys.argv) > 1 else "F2,M1").split(",")
SPEED = sys.argv[2] if len(sys.argv) > 2 else "1.0"

def plain(s):
    s = s.replace("**", "")
    s = re.sub(r"[→↘↓↗]", " ", s)
    s = re.sub(r"\s+/\s+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def token():
    u = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    r = urllib.request.Request(u, data=b'{"returnSecureToken":true}',
                               headers={"Content-Type": "application/json"}, method="POST")
    return json.load(urllib.request.urlopen(r, timeout=20))["idToken"]

def docs(tok):
    u = (f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)"
         f"/documents/english_expressions?pageSize=300")
    r = urllib.request.Request(u, headers={"Authorization": f"Bearer {tok}"})
    return json.load(urllib.request.urlopen(r, timeout=30)).get("documents", [])

def g(f, k):
    return f.get(k, {}).get("stringValue", "")

CHUNK_RE = re.compile(r"reusable chunks?\s*:", re.I)

texts, seen = [], set()
for d in docs(token()):
    f = d["fields"]
    for t in (g(f, "expression"), "" if CHUNK_RE.search(g(f, "context")) else g(f, "context")):
        t = plain(t)
        if t and t not in seen:
            seen.add(t); texts.append(t)

print(f"대상 {len(texts)}건 x {len(VOICES)}음성 = {len(texts)*len(VOICES)}")
gen = hit = err = 0
for i, t in enumerate(texts, 1):
    for v in VOICES:
        url = f"{TTS}?t={urllib.parse.quote(t)}&v={v}&s={SPEED}"
        try:
            t0 = time.time()
            with urllib.request.urlopen(url, timeout=120) as r:
                n = len(r.read())
            el = time.time() - t0
            if el < 0.3: hit += 1
            else: gen += 1
            print(f"  [{i}/{len(texts)}] {v} {el:5.2f}s {n:6d}B  {t[:46]}")
        except Exception as e:
            err += 1
            print(f"  [{i}/{len(texts)}] {v} ERROR {e}  {t[:40]}", file=sys.stderr)
print(f"완료 — 생성 {gen} / 캐시 {hit} / 실패 {err}")
