# -*- coding: utf-8 -*-
# 연결어 보강 배치 3 적용 (2026-09-30) — 24장 중 15장.
# 손 안 댄 9장과 그 이유는 필러배치A3-20260930.md 에 적어 두었다.
# updateMask 로 expression / rhythm / ko / pron 만 PATCH.
import sys, os, importlib.util

# token()/patch() 는 배치 1 파일에 있다. 파일명에 하이픈이 있어 일반 import 가 안 되므로
# 경로로 직접 읽어온다.
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "필러적용내역A1-20260930.py")
_s = importlib.util.spec_from_file_location("filler_a1", _p)
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)
token, patch = _m.token, _m.patch

B3 = [
("OZOkit8ZwKkRLNnILVFl",
 "Hi, can you check my order under Patrick? So I ordered ramen, but I think you actually sent the wrong items.",
 "Hi, ↘↗ / can you **check** my **or**der / under **PA**trick? ↗ So I **or**dered **ra**men, ↗ / but I think you **act**ually **sent** → / the **WRONG** items. ↘",
 "안녕하세요, Patrick 이름으로 된 주문 좀 확인해 주시겠어요? 그러니까 라면을 주문했는데 사실 다른 물건이 온 것 같아요.",
 "하이, / 캔뉴 **첵** 마이 **오**-r더r / 언더r **패**추뤽? 쏘우 아이 **오**-r더rd **롸**-먼, / 벗 아이 씽큐 **액**츄얼리 **쎈**ㅌ / 더 **뤄어** 나이럼z."),

("PelMkfhAEV5TiGQWq3eX",
 "Oh, I need to let you know something. The thing is, we've got an inspection scheduled for the FSIC, so what time works for you?",
 "**Oh**, ↘↗ / I **need** to let you **KNOW** something. ↘ The **thing** is, ↘↗ / we've got an in**spec**tion **sched**uled → / for the FSIC, → / so what **TIME** works for you? ↘",
 "아, 알려드릴 게 있어요. 문제는, FSIC 점검이 잡혀 있는데, 몇 시가 괜찮으세요?",
 "**오**우, / 아이 니-투 레츄 노우 썸씽. 더 **씽** 이z, / 위v 가런 인s**펙**션 **s께**쥴d / f어r 더 에f에s아이씨, / 쏘우 왓 **타임** 워rks f어r 유?"),

("zxGfRSbEoQ1GbgrWCeKR",
 "Honestly, I think your staff needs to be more careful when they pack the items. I mean, they should double-check everything against the order receipt.",
 "**Hon**estly, ↘↗ / I think your **staff** → / needs to be more **CARE**ful → / when they **pack** the **items**. ↘ I **mean**, ↘↗ / they should **dou**ble-**check ev**erything → / against the **or**der re**CEIPT**. ↘",
 "솔직히 포장할 때 직원분들이 좀 더 주의해야 할 것 같아요. 그러니까, 주문서와 전부 대조해서 확인해야 하고요.",
 "**아**너s리, / 아이 씽큐어r **s때f** / 니-즈투 비 모-r **케어r**f얼 / 웬 데이 **팩** 디 **아이**럼z. 아이 **민**, / 데이 슈d **더**버L **첵 에**v뤼씽 / 어겐s더 **오**-r더r 뤼**씨**-ㅌ."),

("FHNYauiOp8SBnKRaEZba",
 "Yeah, I hear you, but we're short on time. Look, the handover to Metro Bank is coming, so we need it done by this weekend.",
 "Yeah, ↘↗ / I **hear** you, ↗ / but we're **SHORT** on time. ↘ **Look**, ↘↗ / the **hand**over to **Met**ro Bank is coming, → / so we need it **DONE** / by this **week**end. ↘",
 "네, 무슨 말씀인지 압니다만, 시간이 빠듯합니다. 저기, 메트로뱅크 인도가 다가오고 있어서 이번 주말까지는 끝내야 합니다.",
 "예, / 아이 **히**어r 유, / 벗 위어r **쇼**-r돈 타임. **룩**, / 더 **핸**도우v어r 투 **메**추로우 뱅ㅋ 이z 커밍, / 쏘우 위 니-릿 **던** / 바이 디s **위-**켄d."),

("jIZSEIAlD6MZsyr68hXw",
 "Oh, sorry about that. So I'll send maintenance up to check it first, then I'll get back to you once we know what the problem is.",
 "**Oh**, ↘↗ / **SOR**ry about that. ↘ So I'll send **main**tenance up → / to **check** it first, ↗ / then I'll get **back** to you → / once we **know** → / what the **PROB**lem is. ↘",
 "아, 죄송합니다. 그래서 먼저 유지보수 직원을 올려보내 확인하고, 문제가 뭔지 알게 되면 다시 연락드리겠습니다.",
 "**오**우, / **써**뤼 어바웃 댓. 쏘우 아으L 쎈d **메**인트넌s 업 / 투 **첵**킷 f어rsㅌ, / 덴 아으L 겟 **백** 투 유 / 원s 위 **노우** / 왓 더 **프롸**블럼 이z."),

("lhDUwfaW5iPSQuQUvxcX",
 "Honestly, I'd set up an app for complaints. That way, when tenants have a problem, they just log it and we handle it from there. Because right now they call us at all hours.",
 "**Hon**estly, ↘↗ / I'd **set** up an **APP** for complaints. ↘ **That** way, ↘↗ / when **ten**ants have a **prob**lem, ↘↗ / they just **log** it ↗ / and we **han**dle it from **THERE**. ↘ Because right **now** → / they call us at **ALL** hours. ↘",
 "솔직히 저라면 불만 접수용 앱을 만들겠습니다. 그러면 임차인이 문제가 생겼을 때 그냥 등록만 하고, 저희가 거기서부터 처리하면 됩니다. 왜냐하면 지금은 시도 때도 없이 전화가 옵니다.",
 "**아**너s리, / 아으d **쎄**럽 언 **앱** f어r 컴플레인츠. **댓** 웨이, / 웬 **테**넌츠 해v 어 **프롸**블럼, / 데이 저sㅌ **러**깃 / 앤드 위 **핸**들릿 f뤔 **데**어r. 비커z 롸잇 **나우** / 데이 커어ㄹ 어s 앳 **어어ㄹ** 아워rz."),

# 7, 8 — 연결어는 이미 있고 문장 첫 글자가 소문자로 저장돼 있던 것만 바로잡는다
("UgZAivcLzTZBHSj1pySq",
 "Sure, my number is zero nine one six, zero one three one, and my address is Two Serendra, Bonifacio. If you need my email too, I can give you that.",
 "Sure, ↗ / my **number** is zero nine one six, zero one three one, → / and my address is Two Serendra, Boni**FA**cio. ↘ If you need my **email** too, ↘↗ / I can give you **THAT**. ↘",
 "네, 제 번호는 0916 0131이고 주소는 Two Serendra, Bonifacio입니다. 이메일도 필요하시면 그것도 알려드릴게요.",
 "슈어, / 마이 **넘**버리즈 지어로우 나인 원 씩s, 지어로우 원 쓰리 원, / 앤 마이 애드뤠씨z 투 쎄뤤드뤄, 보니**f아**시오. 이f 유 니-d 마이 **이메**이우 투, / 아이 큰 기v 유 **댓**."),

("a2SMUAPQrtGb692g92FQ",
 "Yeah, it's a yellow carry-on, around twenty inches, with a red tag on the handle. Just to double-check, do you need the brand too?",
 "Yeah, / it's a **yellow** carry-on, → / around **twenty** inches, → / with a red **TAG** on the handle. ↘ Just to **double**-check, → / do you need the brand **TOO**? ↗",
 "네, 노란색 기내용 가방이고 약 20인치예요. 손잡이에 빨간색 태그가 있어요. 확인차 여쭤보는데, 브랜드도 필요하세요?",
 "예아, / 잇츠 어 **옐**로우 캐뤼온, / 어라운드 **트웬**티 인치z, / 위더 레d **태그** 온 더 핸들. 저sㅌ 투 **더블**첵, / 두유 니-d 더 브랜드 **투**?"),

("PPBuPEv6h53E9rQh1eCr",
 "Yeah, sorry about that. So I'll have our maintenance team check it right away, and we'll get it fixed as soon as possible.",
 "Yeah, ↘↗ / **SOR**ry about that. ↘ So I'll have our **main**tenance team → / **CHECK** it right away → / and we'll get it **fixed** as soon as possible. ↘",
 "네, 죄송합니다. 그래서 바로 저희 maintenance team에게 확인시키고, 최대한 빨리 수리하겠습니다.",
 "예, / **싸**뤼 어바웃 댓. 쏘우 아으L 해v 아워r **메인**터넌s 팀 / **체**킷 라잇 어웨이 / 앤드 위ㄹ 게릿 **f익**sㅌ 애z 쑤-너z 파써블."),

("kqubEzqRzJKcJhdehVsp",
 "So I checked the water pressure in the bathroom, and it's still really low. Anyway, I asked Ascent when they could fix it, and they said they'll come tomorrow.",
 "**So** ↘↗ / I **checked** the **wa**ter **pres**sure → / in the **bath**room → / and it's still really **LOW**. ↘ **A**nyway, ↘↗ / I **asked** As**cent** → / when they could **fix** it → / and they said they'll **come** to**MOR**row. ↘",
 "그래서 욕실 수압을 확인했는데 아직도 많이 약합니다. 아무튼 Ascent에 언제 고칠 수 있는지 물었고, 내일 오겠다고 했습니다.",
 "**쏘**우 / 아이 **첵**ㅌ 더 **워**러r **프뤠**셔r / 인 더 **배ㅆ**룸 / 앤드 잇츠 스틸 륄리 **로우**. **에**니웨이, / 아이 **애**s크ㅌ 애s**쎈**ㅌ / 웬 데이 쿠d **f익**씻 / 앤드 데이 쎄d 데이ㄹ **컴** 터**마**로우."),

("zJY3Cn2tqitnHF5kD7T7",
 "Honestly, I'm a bit worried about tomorrow's handover. The thing is, we still haven't fixed the water pressure issue and Ascent hasn't really taken care of it.",
 "**Hon**estly, ↘↗ / I'm a bit **wor**ried → / about tomorrow's **HAND**over. ↘ The **thing** is, ↘↗ / we **still** haven't **fixed** → / the **wa**ter **pres**sure issue ↗ / and As**cent** hasn't really **TAK**en care of it. ↘",
 "솔직히 내일 인수인계가 좀 걱정돼요. 문제는, 아직 수압 문제를 해결하지 못했고, Ascent도 제대로 처리하지 않았어요.",
 "**아**니슬리, / 아임 어 빗 **워**r이d / 어바웃 터마로우z **핸**도우v어r. 더 **씽** 이z, / 위 **스틸** 해v은ㅌ **f익**sㅌ / 더 **워**러r **프뤠**셔r 이슈 / 앤드 애s**쎈**ㅌ 해z은ㅌ 륄리 **테이**큰 케어러v잇."),

("7fWPEc1W2OmypmvlhZ4z",
 "Honestly, it was pretty much cold when it arrived, and it's too cold to eat. So could you replace it or send me a fresh one?",
 "**Hon**estly, ↘↗ / it was **pret**ty much **cold** → / when it ar**rived**, ↗ / and it's too **COLD** to **eat**. ↘ So could you re**place** it ↗ / or **send** me a **FRESH** one? ↘",
 "솔직히 도착했을 때 거의 다 식어 있었고 너무 차가워서 먹기 힘들어요. 그래서 새것으로 교환해 주시거나 새 음식으로 다시 보내주실 수 있나요?",
 "**아**너s리, / 잇 워z **프뤼**리 머치 **코울**d / 웨닛 어**롸이**vd / 앤드 잇츠 투- **코울**d 투 **이**-ㅌ. 쏘우 쿠쥬 뤼**플레이**s 잇 / 어r **쎈**d 미 어 **프뤠쉬** 원?"),

("bcEdoBDLVteTLIL9NxtX",
 "I ordered a café latte, but I actually got an Americano instead. So could you send the latte or let me know what my options are?",
 "I **or**dered a ca**fé lat**te, ↗ / but I **act**ually **got** an Ameri**ca**no in**STEAD**. ↘ So could you **send** the **lat**te ↗ / or let me **know** → / what my **OP**tions are? ↘",
 "카페라떼를 주문했는데, 사실 Americano가 대신 왔어요. 그래서 라떼를 다시 보내주시거나 제가 선택할 수 있는 방법이 뭔지 알려주시겠어요?",
 "아이 **오**-r더rd 어 캐f**에이 라**테이 / 벗 아이 **액**츄얼리 **가**런 어메뤼**카**노우 인s**떼**d. 쏘우 쿠쥬 **쎈**d 더 **라**테이 / 어r 렛 미 **노우** / 왓 마이 **압**션z 아r?"),

("wLSAXlSaIAilBPcJkWjk",
 "Yeah, I understand. But could you let me know how much longer it'll take? We're preparing for a handover, so we gotta get this fixed as soon as possible.",
 "Yeah, ↘↗ / I under**STAND**. ↘ But could you let me **know** → / how much **LONG**er it'll **take**? ↗ We're pre**par**ing → / for a **hand**over, → / so we **got**ta get this **FIXED** as **soon** as **pos**sible. ↘",
 "네, 이해합니다. 그런데 얼마나 더 걸릴지 알려주실 수 있나요? 지금 인수인계를 준비 중이라서 이 문제를 최대한 빨리 해결해야 합니다.",
 "예, / 아이 언더r**s땐**d. 벗 쿠쥬 렛 미 **노우** / 하우 머치 **러엉**어r 이럴 **테익**? 위어r 프뤼**페어**링 / f어러 **핸**도우v어r / 쏘우 위 **가**라 겟 디s **f익**sㅌ 어z **쑤**-ㄴ 어z **파**써버L."),

("O5rm6ylds742aXzEOMkz",
 "John, do you have a minute? So I've noticed you've been coming in late the last few days. Look, our start time is nine, and I need everyone here at the same time. Is something going on?",
 "**John**, ↘↗ / do you have a **MI**nute? ↗ So I've **no**ticed → / you've been **co**ming in **LATE** → / the last few **days**. ↘ **Look**, ↘↗ / our **start** time is **nine**, ↗ / and I need **eve**ryone here → / at the **SAME** time. ↘ Is **some**thing going **ON**? ↗",
 "존, 잠깐 시간 돼요? 그러니까 지난 며칠 동안 늦게 출근하는 걸 봤어요. 저기, 우리 출근 시간은 9시고, 다들 같은 시간에 여기 나와 있어야 합니다. 무슨 일 있어요?",
 "**잔**, / 두유 해버 **미**닛? 쏘우 아이v **노**우티sㅌ / 유v 빈 **커**미닌 **레**잇 / 더 라sㅌ f유- **데**이z. **룩**, / 아워r **s따**-rt 타임 이z **나**인, / 앤드 아이 니-d **에**v리원 히어r / 앳 더 **쎄**임 타임. 이z **썸**씽 고우이**논**?"),
]

if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    tok = token()
    print(("[DRY RUN] " if dry else "[APPLY] ") + "배치 3 — %d장" % len(B3))
    ok = 0
    for doc_id, expr, rh, ko, pron in B3:
        fields = {"expression": expr, "rhythm": rh, "ko": ko, "pron": pron}
        if dry:
            print("  %s" % doc_id)
            continue
        try:
            patch(tok, doc_id, fields); ok += 1
            print("  ok  %s" % doc_id)
        except Exception as e:
            print("  FAIL %s  %s" % (doc_id, e))
    if not dry:
        print("\n적용 %d / %d" % (ok, len(B3)))
