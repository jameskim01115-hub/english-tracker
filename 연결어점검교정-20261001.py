# -*- coding: utf-8 -*-
"""연결어 점검 후속 — expression 만 고친다 (대소문자 2 + so/but 앞 쉼표 5). rhythm·ko·pron 은 그대로."""
import json, urllib.request
OPS = {
 "I94OO0GSCk2rIKWa1jix": [("catch up on netflix.","catch up on Netflix."),("during the week so I don't","during the week, so I don't")],
 "ocdRZVkAPdndQcp6gHxN": [("improve my english.","improve my English.")],
 "A0FXQPuyUPFLcXXTMSX3": [("viewing scheduled so I had","viewing scheduled, so I had")],
 "FbedYNcy6UFqzCENXIJP": [("with the job but they left","with the job, but they left")],
 "TGsv6Ttd6i6qUIow8l8v": [("big fan of noodles so I'd love","big fan of noodles, so I'd love")],
 "ddf4eb9c6p8YxqLOUr7t": [("on a weekday but sometimes I feel lazy so I push","on a weekday, but sometimes I feel lazy, so I push")],
}
API_KEY="AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
REFERER="https://jameskim01115-hub.github.io/english-tracker/"
BASE="https://firestore.googleapis.com/v1/projects/english-tracker-cea9f/databases/(default)/documents/english_expressions"
def req(u,d=None,m="GET",t=None):
    h={"Content-Type":"application/json","Referer":REFERER}
    if t: h["Authorization"]="Bearer "+t
    r=urllib.request.Request(u,data=json.dumps(d).encode() if d is not None else None,headers=h,method=m)
    with urllib.request.urlopen(r,timeout=40) as f: return json.loads(f.read().decode())
if __name__=="__main__":
    tok=req(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",{"returnSecureToken":True},"POST")["idToken"]
    bk={}
    for did,ops in OPS.items():
        cur=req(f"{BASE}/{did}?key={API_KEY}",None,"GET",tok)["fields"]
        e=cur["expression"]["stringValue"]; bk[did]=e
        for old,new in ops:
            assert e.count(old)==1,(did,old); e=e.replace(old,new)
        req(f"{BASE}/{did}?updateMask.fieldPaths=expression&key={API_KEY}",{"fields":{"expression":{"stringValue":e}}},"PATCH",tok)
        after=req(f"{BASE}/{did}?key={API_KEY}",None,"GET",tok)["fields"]
        others=[k for k in set(cur)|set(after) if k!="expression" and cur.get(k)!=after.get(k)]
        print(did[:6],"일치:",after["expression"]["stringValue"]==e,"| 기타 변함:",others or "없음")
    json.dump(bk,open("backup_conn_before.json","w"),ensure_ascii=False,indent=1)
