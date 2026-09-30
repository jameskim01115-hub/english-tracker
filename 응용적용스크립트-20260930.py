# -*- coding: utf-8 -*-
"""응용 문장(useCases) 백필 — useCases 칸만 PATCH 한다.
stage·nextReview·studied·expression 등은 updateMask 에 넣지 않으므로 그대로 남는다."""
import json, urllib.request, importlib, sys, time

PROJECT   = "english-tracker-cea9f"
API_KEY   = "AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
REFERER   = "https://jameskim01115-hub.github.io/english-tracker/"
BASE      = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/english_expressions"

def req(url, data=None, method="GET", token=None):
    h = {"Content-Type": "application/json", "Referer": REFERER}
    if token: h["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=30) as f:
        return json.loads(f.read().decode())

tok = req(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",
          {"returnSecureToken": True}, "POST")["idToken"]
print("auth ok")

ALL = {}
for tag in ["u1","u2","u3","u4","u5","u6","u7"]:
    ALL.update(importlib.import_module(f"cases_{tag}").CASES)
print("대상 카드:", len(ALL), "| 문장:", sum(len(v) for v in ALL.values()))

ok = fail = 0
for i,(did, cases) in enumerate(ALL.items(), 1):
    payload = json.dumps([{"en":en,"ko":ko} for en,ko in cases], ensure_ascii=False)
    url = f"{BASE}/{did}?updateMask.fieldPaths=useCases&key={API_KEY}"
    try:
        req(url, {"fields": {"useCases": {"stringValue": payload}}}, "PATCH", tok)
        ok += 1
    except Exception as e:
        fail += 1; print("FAIL", did, e)
    if i % 40 == 0: print(f"  ...{i}/{len(ALL)}"); time.sleep(0.3)
print(f"적용 완료: ok={ok} fail={fail}")
