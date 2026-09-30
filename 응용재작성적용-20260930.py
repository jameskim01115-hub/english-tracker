# -*- coding: utf-8 -*-
"""응용 문장 재작성 — useCases 칸만 PATCH. 3문장이 전부 카드의 고정 표현을 쓰도록 맞춘 것."""
import json, urllib.request, importlib, time, sys
sys.path.insert(0,'.')
API_KEY="AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
REFERER="https://jameskim01115-hub.github.io/english-tracker/"
BASE="https://firestore.googleapis.com/v1/projects/english-tracker-cea9f/databases/(default)/documents/english_expressions"
def req(u,d=None,m="GET",t=None):
    h={"Content-Type":"application/json","Referer":REFERER}
    if t: h["Authorization"]="Bearer "+t
    r=urllib.request.Request(u,data=json.dumps(d).encode() if d is not None else None,headers=h,method=m)
    with urllib.request.urlopen(r,timeout=30) as f: return json.loads(f.read().decode())
tok=req(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",{"returnSecureToken":True},"POST")["idToken"]
ALL={}
for t in ['f1','f2','f3','f4','f5','f6']: ALL.update(importlib.import_module(f"cases_{t}").CASES)
print("대상",len(ALL),"| 문장",sum(len(v) for v in ALL.values()))
ok=fail=0
for i,(did,cs) in enumerate(ALL.items(),1):
    p=json.dumps([{"en":e,"ko":k} for e,k in cs],ensure_ascii=False)
    try:
        req(f"{BASE}/{did}?updateMask.fieldPaths=useCases&key={API_KEY}",
            {"fields":{"useCases":{"stringValue":p}}},"PATCH",tok); ok+=1
    except Exception as e:
        fail+=1; print("FAIL",did,e)
    if i%40==0: print(f"  ...{i}/{len(ALL)}"); time.sleep(0.3)
print(f"적용 완료: ok={ok} fail={fail}")
