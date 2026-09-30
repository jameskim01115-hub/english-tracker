# -*- coding: utf-8 -*-
import json, urllib.request, importlib
PROJECT="english-tracker-cea9f"
API_KEY="AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
REFERER="https://jameskim01115-hub.github.io/english-tracker/"
BASE=f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/english_expressions"
def req(url,data=None,method="GET",token=None):
    h={"Content-Type":"application/json","Referer":REFERER}
    if token: h["Authorization"]="Bearer "+token
    r=urllib.request.Request(url,data=json.dumps(data).encode() if data is not None else None,headers=h,method=method)
    with urllib.request.urlopen(r,timeout=40) as f: return json.loads(f.read().decode())
tok=req(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",{"returnSecureToken":True},"POST")["idToken"]
docs=[];tokn=None
while True:
    u=BASE+"?pageSize=300"+(f"&pageToken={tokn}" if tokn else "")
    r=req(u,token=tok); docs+=r.get("documents",[]); tokn=r.get("nextPageToken")
    if not tokn: break
json.dump({"documents":docs},open("expr_u_after.json","w"),ensure_ascii=False)
print("받은 문서:",len(docs))

before={d["name"].split("/")[-1]:d.get("fields",{}) for d in json.load(open("expr_b.json"))["documents"]}
after ={d["name"].split("/")[-1]:d.get("fields",{}) for d in docs}
ALL={}
for t in ["u1","u2","u3","u4","u5","u6","u7"]: ALL.update(importlib.import_module(f"cases_{t}").CASES)

mism=[];others={};missing=[]
for did,cases in ALL.items():
    if did not in after: missing.append(did); continue
    want=json.dumps([{"en":e,"ko":k} for e,k in cases],ensure_ascii=False)
    got=after[did].get("useCases",{}).get("stringValue")
    if got!=want: mism.append(did)
    b=before.get(did,{})
    for k in set(b)|set(after[did]):
        if k=="useCases": continue
        if b.get(k)!=after[did].get(k): others.setdefault(k,[]).append(did)
print("대상",len(ALL),"| useCases 불일치:",len(mism),"| 문서 없음:",len(missing))
if mism: print("  ",mism[:10])
print("기타 필드 변함:",{k:len(v) for k,v in others.items()} or "없음")
for k,v in others.items(): print("   ",k,v[:6])
# 비대상
non=[d for d in after if d not in ALL]
ch=[d for d in non if d in before and before[d]!=after[d]]
print("비대상",len(non),"중 변한 문서:",len(ch), ch[:8])
# 최종 커버리지
def nuse(f):
    s=f.get("useCases",{}).get("stringValue","")
    try: return len(json.loads(s)) if s else 0
    except: return 0
def stud(f):
    return f.get("studied",{}).get("booleanValue",False) or int(f.get("stage",{}).get("integerValue",0))>0
S=[f for f in after.values() if stud(f)]
print(f"\n학습완료 {len(S)}장 중 응용 문장 보유: {sum(1 for f in S if nuse(f))}장")
print(f"전체 {len(after)}장 중 보유: {sum(1 for f in after.values() if nuse(f))}장")
