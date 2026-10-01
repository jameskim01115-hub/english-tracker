# -*- coding: utf-8 -*-
import json,re,urllib.request
API_KEY="AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
REFERER="https://jameskim01115-hub.github.io/english-tracker/"
BASE="https://firestore.googleapis.com/v1/projects/english-tracker-cea9f/databases/(default)/documents/english_expressions"
def req(u,d=None,m="GET",t=None):
    h={"Content-Type":"application/json","Referer":REFERER}
    if t: h["Authorization"]="Bearer "+t
    r=urllib.request.Request(u,data=json.dumps(d).encode() if d is not None else None,headers=h,method=m)
    with urllib.request.urlopen(r,timeout=40) as f: return json.loads(f.read().decode())
tok=req(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",{"returnSecureToken":True},"POST")["idToken"]
docs=[];tk=None
while True:
    r=req(BASE+"?pageSize=300"+(f"&pageToken={tk}" if tk else ""),None,"GET",tok)
    docs+=r.get("documents",[]); tk=r.get("nextPageToken")
    if not tk: break
json.dump({"documents":docs},open("expr_oct1_now.json","w"),ensure_ascii=False)
def S(x,k):
    v=x.get("fields",{}).get(k); return v.get("stringValue","") if v and "stringValue" in v else ""
rows=[]
for x in docs:
    if S(x,"source")!="chatgpt-review": continue
    q=re.sub(r"\s+"," ",re.sub(r"\*\*|[→↗↘↓]|\s/\s|\|"," ",S(x,"question"))).strip()
    rows.append({"id":x["name"].split("/")[-1],"q":q,"e":S(x,"expression"),"ko":S(x,"ko")})
json.dump(rows,open("review_rows2.json","w"),ensure_ascii=False,indent=1)
cand={}
for r in rows:
    e=r["e"]; l=e.lower(); why=[]
    for f in ["honestly","actually","i mean","you know","basically","the thing is","look,"]:
        n=len(re.findall(r"\b"+re.escape(f),l))
        if n>=2: why.append("%s x%d"%(f,n))
    n_so=len(re.findall(r"\bso\b",l))
    if n_so>=2: why.append("so x%d"%n_so)
    if len(re.findall(r"\band\b",l))>=3: why.append("and x3+")
    sents=re.split(r"(?<=[.?!])\s+",e)
    if sum(1 for s in sents[1:] if re.match(r"^(And|But|So|Also|Then|Plus)\b",s))>=2: why.append("문장시작 접속어 2+")
    if re.search(r"\bbecause\b|'cause",l) and re.search(r"\bso\b",l): why.append("because+so")
    if re.search(r"\b(and|but|so),?\s+(and|but|so)\b",l): why.append("접속어 연속")
    if why: cand[r["id"]]=why
print("후보",len(cand),"/",len(rows))
for r in rows:
    if r["id"] in cand:
        print("\n%s  %s\n  Q: %s\n  A: %s"%(r["id"],cand[r["id"]],r["q"][:80],r["e"]))
