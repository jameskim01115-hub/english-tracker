# -*- coding: utf-8 -*-
"""맨 앞 필러·연결어가 질문과 맞는지 점검 (자동 판정은 후보만 뽑는다 — 눈으로 확인할 것).
사용: python3 filler_q_check.py export.json"""
import json, re, sys, collections
docs = json.load(open(sys.argv[1], encoding="utf-8"))["documents"]
def S(x,k):
    v=x.get("fields",{}).get(k); return v.get("stringValue","") if v and "stringValue" in v else ""
def clean(s): return re.sub(r"\s+"," ",re.sub(r"\*\*|[→↗↘↓]|\s/\s|\|"," ",s)).strip()
WH = re.compile(r"^(What|How|Where|When|Why|Who|Which|So,? (what|where|how|when|why|who))\b", re.I)
lead = collections.Counter(); out = {"Yeah+wh":[], "Actually":[], "Oh,and/And/Anyway":[], "지시무시":[], "Q깨짐":[]}
for x in docs:
    if S(x,"source")!="chatgpt-review": continue
    did=x["name"].split("/")[-1]; q=clean(S(x,"question")); e=S(x,"expression"); qko=S(x,"questionKo")
    m=re.match(r"^(Yeah|Honestly|Actually|Well|So|Oh|The thing is|You know|Look|I mean|Okay so|Okay|Right|No|Hi|Hmm|Like|Basically|To be honest|Anyway|And)\b",e)
    lead[m.group(1) if m else "(없음)"]+=1
    if e.startswith("Yeah") and WH.match(q): out["Yeah+wh"].append((did,q[:50],e[:40]))
    if e.startswith("Actually"): out["Actually"].append((did,q[:50],e[:40]))
    if re.match(r"^(Oh, and|And|Anyway|Also|Then)\b",e): out["Oh,and/And/Anyway"].append((did,q[:50],e[:40]))
    if re.match(r"^(Start with|Say it|Begin with)",q) and m and m.group(1) not in ("I",): out["지시무시"].append((did,q[:50],e[:40]))
    if S(x,"question") and (len(re.sub(r"[^A-Za-z]","",q))<6 or re.search(r"[ㄱ-ㅎ]",qko)): out["Q깨짐"].append((did,q[:30],qko[:30]))
print("맨 앞 필러 분포:",lead.most_common())
for k,v in out.items():
    print(f"\n[{k}] {len(v)}건")
    for t in v: print("  ",t)
