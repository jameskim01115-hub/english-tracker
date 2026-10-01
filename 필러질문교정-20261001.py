# -*- coding: utf-8 -*-
"""질문과 안 맞는 맨 앞 필러·연결어 교정 (2026-10-01). expression·rhythm·ko·pron(+질문 칸)만 PATCH."""
import json, sys
P = {}   # id -> {"ops":[(field,old,new)], "set":{}, "del":[]}
def card(did): return P.setdefault(did, {"ops": [], "set": {}, "del": []})
def lead(did, e, rh, ko, pr=None):
    c = card(did)
    c["ops"] += [("expression",)+e, ("rhythm",)+rh, ("ko",)+ko]
    if pr: c["ops"].append(("pron",)+pr)

# ── Yeah → No (부정 답) ─────────────────────────────
lead("0hwgGP42aGZX3YAPzOWI", ("Yeah, we haven't fixed","No, we haven't fixed"),
     ("Yeah, ↘↗ / we haven't **fixed**","No, ↘↗ / we haven't **fixed**"),
     ("네, 수압 문제는","아뇨, 수압 문제는"), ("예, / 위 해븐ㅌ","노우, / 위 해븐ㅌ"))
lead("XhcHVk0qTczTLU1qImMj", ("Yeah, no updates","No, no updates"),
     ("Yeah, ↘↗ / no up**dates**","No, ↘↗ / no up**dates**"),
     ("네, 지금은 그쪽에서","아뇨, 지금은 그쪽에서"), ("예, / 노우 업**데이**츠","노우, / 노우 업**데이**츠"))
lead("psiUBVJpm4mBkVcCGuAE", ("Actually, it's my first time","No, it's my first time"),
     ("**Ac**tually, / it's my **first** time","No, ↘↗ / it's my **first** time"),
     ("사실 이번이 처음이라","아뇨, 이번이 처음이라"), ("**액**츄얼리, / 잇츠 마이","노우, / 잇츠 마이"))
# ── 인사/상황에 맞게 ───────────────────────────────
lead("2Vq8yNvUYGfJD2pLOEny", ("Yeah, I have a cold","Hi, I have a cold"),
     ("Yeah, ↘↗ / I have a **cold**","**Hi**, ↘↗ / I have a **cold**"),
     ("네, 감기에","안녕하세요, 감기에"), ("예, / 아이 해v어","하이, / 아이 해v어"))
lead("8ciFAG2wHAArH8LzV5pP", ("Oh, and I sorted","Yeah, I sorted"),
     ("**Oh**, and → / I **SORT**ed","Yeah, ↘↗ / I **SORT**ed"),
     ("아, 그리고 새로 온","네, 새로 온"), ("**오**우, 앤d / 아이 **쏘r**리d","예, / 아이 **쏘r**리d"))
lead("KW161bNxa43m8u5vzzov", ("Yeah, you don't need","Actually, you don't need"),
     ("Yeah, ↘↗ / you **don't**","**Ac**tually, ↘↗ / you **don't**"),
     ("네, 따로 준비하실","사실 따로 준비하실"), ("예, / 유 **도운**ㅌ","**액**츄얼리, / 유 **도운**ㅌ"))
# ── Actually/Yeah/Okay/Look/And/Anyway → Well ─────────
W = "**Well**, ↘↗ / "
lead("A0FXQPuyUPFLcXXTMSX3", ("Actually, I had a viewing","Well, I had a viewing"),
     ("**Ac**tually, ↘↗ / I had a **view**ing",W+"I had a **view**ing"),
     ("사실 집 보러","음, 집 보러"), ("**액**츄얼리, / 아이 해러","**웰**, / 아이 해러"))
lead("GHbtkWdkyBWnlbv3kSOc", ("Yeah, I didn't do much","Well, I didn't do much"),
     ("Yeah, ↘↗ / I didn't do **much**",W+"I didn't do **much**"), ("네, 퇴근 후에는","음, 퇴근 후에는"))
lead("JScL8Qo9XhO3uOYmIfP7", ("And if we can't","Well, if we can't"),
     ("**And** ↘↗ / if we **can't**",W+"if we **can't**"),
     ("그리고 저희가 처리할 수 없으면","음, 저희가 처리할 수 없으면"), ("**앤**드 / 이f 위 **캔ㅌ**","**웰**, / 이f 위 **캔ㅌ**"))
lead("P0u2eMk8WIQU2vv53QqS", ("Yeah, if it's urgent","Well, if it's urgent"),
     ("Yeah, ↘↗ / if it's **UR**gent",W+"if it's **UR**gent"), ("네, 급한 일이면","음, 급한 일이면"))
lead("Qou8L4dcjTxHtOzlBPYP", ("Yeah, today we prepared","Well, today we prepared"),
     ("Yeah, ↘↗ / to**day**",W+"to**day**"), ("네, 오늘은 인계 준비를","음, 오늘은 인계 준비를"),
     ("예, / 투**데**이","**웰**, / 투**데**이"))
lead("R7XMTfjBZcuEWmLh5dUR", ("Yeah, I just relaxed","Well, I just relaxed"),
     ("Yeah, ↘↗ / I just re**LAXED**",W+"I just re**LAXED**"), ("네, 그냥 쉬면서","음, 그냥 쉬면서"))
lead("b4mxsd6ehE6cQUM76F9B", ("Yeah, Friday works for me","Well, Friday works for me"),
     ("Yeah, ↘↗ / **FRI**day **works** for me",W+"**FRI**day **works** for me"),
     ("네, 저는 금요일 괜찮아요.","음, 저는 금요일 괜찮아요."), ("예아, / **f롸이**데이","**웰**, / **f롸이**데이"))
lead("fmkrRjzi2Ju6DVOzO2bt", ("Look, we still haven't","Well, we still haven't"),
     ("**Look**, ↘↗ / we **STILL ha**ven't",W+"we **STILL ha**ven't"),
     ("저기, 수압 문제도","음, 수압 문제도"), ("**룩**, / 위 **s띨 해**v은ㅌ","**웰**, / 위 **s띨 해**v은ㅌ"))
lead("rpozgze8HC5cJXdlxcC2", ("Yeah, I told them","Well, I told them"),
     ("Yeah, ↘↗ / I **told** them",W+"I **told** them"),
     ("네, 더 이상 지연되면","음, 더 이상 지연되면"), ("예, / 아이 **토울d** 뎀","**웰**, / 아이 **토울d** 뎀"))
lead("vQZiq8CKhU1FZy2rufcF", ("Yeah, I just wanted to relax","Well, I just wanted to relax"),
     ("Yeah, ↘↗ / I just **want**ed",W+"I just **want**ed"), ("네, 퇴근 후에는 그냥","음, 퇴근 후에는 그냥"))
lead("rJPoqbSMpbmYGSRcCKrA", ("Actually, I already have","Well, I already have"),
     ("**Ac**tually, ↘↗ / I al**rea**dy",W+"I al**rea**dy"),
     ("사실 이미 해변 근처에","음, 이미 해변 근처에"), ("**액**츄얼리, / 아이 어**ㄹ뤠**디","**웰**, / 아이 어**ㄹ뤠**디"))
lead("y88WQXpZraQ7IsMaxMqU", ("Actually, I was listening","Well, I was listening"),
     ("**Ac**tually, ↘↗ / I was **listening**",W+"I was **listening**"), ("사실 90년대","음, 90년대"))
# ── Honestly ───────────────────────────────────────
H = "**Hon**estly, ↘↗ / "
lead("3fNe5EycChNW6Js58VZK", ("Actually, I was pretty","Honestly, I was pretty"),
     ("**Ac**tually, ↘↗ / I was",H+"I was"), ("사실 오늘은 꽤","솔직히 오늘은 꽤"),
     ("**액**츄얼리, / 아이 워z","**아**너s를리, / 아이 워z"))
lead("DPw6RMB9omQfn3AGyNeb", ("Yeah, I want it in","Honestly, I want it in"),
     ("Yeah, ↘↗ / I **want** it",H+"I **want** it"), ("네, 거실에 놔 주세요.","솔직히 거실에 놔 주세요."),
     ("예, / 아이 **워**닛","**아**너s를리, / 아이 **워**닛"))
lead("KxL50yEiyCxEN8CXIchh", ("Yeah, it was pretty slow","Honestly, it was pretty slow"),
     ("Yeah, ↘↗ / it was **PRET**ty",H+"it was **PRET**ty"), ("네, 오늘은 꽤 한가했어요.","솔직히 오늘은 꽤 한가했어요."),
     ("예, / 잇 워z","**아**너s를리, / 잇 워z"))
lead("gt3Mi9K5WhNpR1Jo6k68", ("Yeah, yesterday was Sunday","Honestly, yesterday was Sunday"),
     ("Yeah, ↘↗ / **YES**terday",H+"**YES**terday"), ("네, 어제는 일요일이었는데","솔직히 어제는 일요일이었는데"))
lead("vUK3i0sexPVjGd1aqYJj", ("Actually, I'd like to go to a Japanese","Honestly, I'd like to go to a Japanese"),
     ("**Ac**tually, ↘↗ / I'd like to **GO**",H+"I'd like to **GO**"), ("사실 내일 일식당에","솔직히 내일 일식당에"))
# ── 그 밖의 필러 ───────────────────────────────────
lead("BBJvKGMmKatFmGps9ueR", ("Yeah, three or four","Like, three or four"),
     ("Yeah, ↘↗ / **three**","**Like**, ↘↗ / **three**"), ("네, 일주일에 서너","음, 일주일에 서너"),
     ("예, / **쓰뤼**","**라**익, / **쓰뤼**"))
lead("GwJaTirrQGSESiGAEaXa", ("Yeah, I live in Bonifacio","Basically, I live in Bonifacio"),
     ("Yeah, ↘↗ / I **live** in","**Bas**ically, ↘↗ / I **live** in"), ("네, 저는 보니파시오에","쉽게 말하면 저는 보니파시오에"),
     ("예, / 아이 **리v** 인","**베**이씨끌리, / 아이 **리v** 인"))
lead("JxOx4DH7Gjx4vHGipTat", ("Yeah, I'm staying","So I'm staying"),
     ("Yeah, ↘↗ / I'm **stay**ing","**So** ↘↗ / I'm **stay**ing"), ("네, 4박 5일로","그러니까 4박 5일로"),
     ("예, / 아임 **s떼이**잉","**쏘**우 / 아임 **s떼이**잉"))
lead("ekcr4YzNs66icT67RSob", ("Yeah, it's rainy season","Oh, it's rainy season"),
     ("Yeah, ↘↗ / it's **rain**y season","**Oh**, ↘↗ / it's **rain**y season"), ("네, 필리핀은","아, 필리핀은"))
lead("ognn4EtrF4PICAUVfLxA", ("Yeah, I usually get an Americano.","Hmm, I usually get an Americano."),
     ("Yeah, ↘↗ / I usually **get**","**Hmm**, ↘↗ / I usually **get**"), ("네, 저는 보통","음, 저는 보통"),
     ("예, / 아이 유쥬얼리","**흠**, / 아이 유쥬얼리"))
lead("fIl6SQhjWxKzPUSXu1tA", ("Okay, I'll report it","So I'll report it"),
     ("O**kay**, ↘↗ / I'll re**port**","**So** ↘↗ / I'll re**port**"), ("네, 먼저 상사에게","그럼 먼저 상사에게"),
     ("오우**케**이, / 아일 뤼**포rㅌ**","**쏘**우 / 아일 뤼**포rㅌ**"))
lead("XpYmXcZKZwtpRA6bSwIk", ("Anyway, we hit","So we hit"),
     ("**A**nyway, ↘↗ / we **hit**","**So** ↘↗ / we **hit**"), ("아무튼 이번 주에","그러니까 이번 주에"),
     ("**에**니웨이, / 위 **힛**","**쏘**우 / 위 **힛**"))
lead("nurljxfrVgAAAIzeO4w6", ("Oh, and we had to prepare","Oh, we had to prepare"),
     ("**Oh**, and → / we **HAD**","**Oh**, ↘↗ / we **HAD**"), ("아, 그리고 임차인들에게","아, 임차인들에게"),
     ("**오**우, 앤d / 위 **해d**","**오**우, / 위 **해d**"))
lead("l21H8xQu3M9DIxihgBlq", ("Oh, and the elevator's","Oh, the elevator's"),
     ("**Oh**, and → / the e**le**vator's","**Oh**, ↘↗ / the e**le**vator's"), ("아, 그리고 엘리베이터가","아, 엘리베이터가"),
     ("**오**우, 앤d / 디 **엘**러v에이러rz","**오**우, / 디 **엘**러v에이러rz"))
lead("0zsQh9tNqhpn30tOIe17", ("Actually, I\u2019m a big fan","I mean, I\u2019m a big fan"),
     ("**Act**ually ↘↗ / ","I **mean**, ↘↗ / "), ("사실 저는 면 요리를 정말","그러니까 저는 면 요리를 정말"))
# ── 필러 삭제 / 연결어 ──────────────────────────────
lead("AwanvmeM2X6lyKcqnzAv", ("Honestly, I couldn't sleep","I couldn't sleep"),
     ("**Hon**estly, ↘↗ / I couldn't **sleep**","I couldn't **sleep**"),
     ("솔직히 어젯밤에 열이","어젯밤에 열이"), ("**아**너s리, / 아이 쿠든ㅌ","아이 쿠든ㅌ"))
c = card("ZWrs3m93LfEIQKseP9oF")
c["ops"] += [("expression",", or it keeps me sharp",", and it keeps me sharp"),
             ("rhythm","**helps me focus**, ↗ / or it","**helps me focus**, ↗ / and it"),
             ("pron","**헬ㅍs 미 f오우커s**, / 오r 잇","**헬ㅍs 미 f오우커s**, / 앤드 잇")]
# ── 질문 쪽이 틀린 카드 ─────────────────────────────
c = card("NZmHsqyYMzDAx6lyMp7J")
c["set"] = {"question":"What do you do for a living?","questionKo":"무슨 일 하세요?",
            "why":"work as + 직책은 「~로 일하다」로 가장 자연스럽다. I work as a general manager. "
                  "일하는 곳의 업종을 붙일 때는 for a Korean grocery store 처럼 for 를 쓴다."}
c["ops"] += [("expression","Yeah, I work as","Well, I work as"),
             ("rhythm","Yeah, ↘↗ / I work as",W+"I work as"),("ko","네, 저는 한국 식료품점에서","음, 저는 한국 식료품점에서")]
card("zG0XqhNrOjLFijtbZao1")["set"] = {"question":"Do you usually run alone, or with other people?",
                                       "questionKo":"보통 혼자 뛰어요, 아니면 다른 사람들이랑 뛰어요?"}
card("4ffYiBAKAtDVYCFSxmlL")["del"] = ["question","questionKo"]
card("FbedYNcy6UFqzCENXIJP")["set"] = {"questionKo":"이번 주 일하면서 제일 짜증 났던 일이 뭐였어요?"}
card("iYQ8PLzL2Fy2psemsii5")["set"] = {"questionKo":"그래서 실제로 직접 뭘 고쳐야 했어요?"}

def S(f,k):
    v=f.get(k,{}); return v.get("stringValue","")
def compute(docs):
    out={}
    for did,spec in P.items():
        f=docs[did]; new={}
        for fld,old,nw in spec["ops"]:
            cur=new.get(fld,S(f,fld))
            assert cur.count(old)==1, f"{did} {fld}: '{old}' x{cur.count(old)} in '{cur[:80]}'"
            new[fld]=cur.replace(old,nw)
        for k,v in spec["set"].items(): new[k]=v
        out[did]={"new":new,"del":spec["del"]}
    return out
if __name__=="__main__":
    print("카드 수:",len(P))
