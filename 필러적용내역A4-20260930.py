# -*- coding: utf-8 -*-
# 연결어 보강 배치 4 적용 (2026-09-30) — 24장 중 11장.
# 이 배치는 짧은 요청문이 많아 `sorry to bother you, but ~` · `'Cause ~` · `Oh, and ~` 로
# 이미 이어진 카드가 13장이다. 그건 손대지 않는다.
import sys, os, importlib.util

# token()/patch() 는 배치 1 파일에 있다. 파일명에 하이픈이 있어 일반 import 가 안 되므로
# 경로로 직접 읽어온다.
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "필러적용내역A1-20260930.py")
_s = importlib.util.spec_from_file_location("filler_a1", _p)
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)
token, patch = _m.token, _m.patch

B4 = [
("CE40N1aN2aVHb1EDR5DT",
 "Yeah, the corrected bill, please. Actually, I'm a little short on time, so could you bring it over as soon as you can?",
 "**Yeah**, ↘↗ / the cor**REC**ted **bill**, please. ↘ **Ac**tually, ↘↗ / I'm a **lit**tle **short** on time, → / so could you **bring** it **o**ver → / as **SOON** as you can? ↗",
 "네, 수정된 계산서로 부탁드려요. 사실 제가 시간이 좀 없어서, 최대한 빨리 가져다주실 수 있을까요?",
 "**예**, / 더 커**뤡**티d **비ㄹ**, 플리-z. **액**츄얼리, / 아임 어 **리**를 **쇼**-rㅌ 온 타임, / 쏘우 쿠쥬 **브링**니**로**우v어r / 애z **쑤**-ㄴ 애쥬 큰?"),

("CYy4q2hhkFrxIRTOZBNV",
 "Honestly, I was pretty busy today, so I just wanted to get some rest after work. When I got home, I organized some stuff around the house 'cause I'm getting ready to move. And I need to finish organizing everything this week, but I'm short on time 'cause I work every day.",
 "**Hon**estly, ↘↗ / I was **pret**ty **bus**y to**day** → / so I just **want**ed → / to get some **REST** → / after **work**. ↘ When I got **home**, ↘↗ / I **or**ganized some **stuff** → / around the **house** → / 'cause I'm → / getting **rea**dy to **MOVE**. ↘ And I need to **fin**ish **or**ganizing → / **ev**erything this **week**, ↗ / but I'm **short** on **TIME** → / 'cause I **work** every **day**. ↘",
 "솔직히 오늘 꽤 바빠서 퇴근하고 그냥 좀 쉬고 싶었어. 집에 와서는 이사 준비 중이라 집안 물건을 좀 정리했어. 그리고 이번 주에 정리를 다 끝내야 하는데 매일 일해서 시간이 부족해.",
 "**아**너s리, / 아이 워z **프뤼**리 **비**z이 투**데이** / 쏘우 아이 저sㅌ **워**니d / 투 겟 썸 **뤠sㅌ** / 애f터r **워**-r크. 웨나이 갓 **호움** / 아이 **오**-r거나이zd 썸 **s떠**f / 어라운더 **하우s** / 커z 아임 / 게링 **뤠**디 투 **무**-v. 앤드 아이 니-투 **f이**니쉬 **오**-r거나이z잉 / **에**v리씽 디s **위**-ㅋ / 벗 아임 **쇼**-r론 **타임** / 커z 아이 **워**-r크 에v리 **데이**."),

("pVhKqSKiHwKJmEs0M0TO",
 "Honestly, I'm worried the movers might damage some of my stuff. If they damage anything, I'll talk to the moving company. And the insurance should cover it 'cause it came with the contract.",
 "**Hon**estly, ↘↗ / I'm **wor**ried → / the **mov**ers might **DAM**age → / some of my **stuff**. ↘ If they **dam**age **an**ything, ↘↗ / I'll **talk** to the **MOV**ing company. ↘ And the in**sur**ance should **COV**er it → / 'cause it **came** → / with the **con**tract. ↘",
 "솔직히 이삿짐 업체 사람들이 내 물건 몇 개를 망가뜨릴까 봐 걱정돼. 뭔가 파손되면 이삿짐 업체에 얘기할 거야. 그리고 계약할 때 보험이 포함돼 있어서 보험으로 처리될 거야.",
 "**아**너s리, / 아임 **워**-r리d / 더 **무**-v어rz 마잇 **대**미j / 써머v 마이 **s떠**f. 이f 데이 **대**미j **에**니씽 / 아으L **터억** 투 더 **무**-v잉 컴퍼니. 앤드 디 인**슈**런슈d **커**v어r 잇 / 커z 잇 **케임** / 위더 **컨**추뤡ㅌ."),

("DPw6RMB9omQfn3AGyNeb",
 "Yeah, I want it in the living room. I mean, it's just more comfortable for me. But I'm kinda worried the signal might be weak in my bedroom. Could you check it after you're done?",
 "Yeah, ↘↗ / I **want** it → / in the **LIV**ing room. ↘ I **mean**, ↘↗ / it's just **more com**fortable → / for me. ↘ But I'm **kin**da **worr**ied ↗ / the **sig**nal might be **weak** → / in my **BED**room. ↘ **Could** you **check** it → / after you're **DONE**? ↗",
 "네, 거실에 놔 주세요. 그러니까, 그게 저한테 편해서요. 근데 침실 신호가 약할까 봐 좀 걱정이에요. 끝나고 한번 확인해 주실 수 있어요?",
 "예, / 아이 **워**닛 / 인 더 **리**v잉 룸. 아이 **민**, / 잇츠 저sㅌ **모**-r **컴**f터r블 / f어r 미. 벗 아임 **카**인더 **워**-리d / 더 **씩**늘 마잇 비 **위**-ㅋ / 인 마이 **베**d룸. **쿠**쥬 **체**킷 / 애f터r 유어r **던**?"),

("sd4jLrM4OjudyVqKYsCi",
 "Yeah, I'll connect my smart TV myself. But I also want to check the internet speed. Actually, do you know what speed my plan is supposed to give me?",
 "Yeah, ↘↗ / I'll con**nect** my **smart** TV → / my**SELF**. ↘ But I **al**so want to **check** → / the **int**ernet **SPEED**. ↘ **Ac**tually, ↘↗ / do you **know** → / what **speed** my **plan** → / is su**PPOSED** to give me? ↗",
 "네, 스마트 TV는 제가 직접 연결할게요. 근데 인터넷 속도도 확인하고 싶어요. 사실, 제 요금제가 원래 어느 정도 속도가 나와야 하는지 아세요?",
 "예, / 아으L 커**넥**ㅌ 마이 **s마**-rㅌ 티v이- / 마이**쎌**f. 벗 아이 **어**ㄹ쏘우 워너 **체**ㅋ / 디 **이**너r넷 **s삐**-d. **액**츄얼리, / 두 유 **노**우 / 왓 **s삐**-d 마이 **플랜** / 이z 써**포**우sㅌ투 기v 미?"),

("zkafXfHeRyUHmalubfji",
 "Honestly, two weeks is too long for me. The thing is, I work from home, so I need this working now. Is there any way to speed it up?",
 "**Hon**estly, ↘↗ / **two weeks** is → / too **LONG** for me. ↘ The **thing** is, ↘↗ / I **work** from **home**, → / so I need this **WORK**ing now. ↘ Is there **an**y **way** → / to **SPEED** it up? ↗",
 "솔직히 2주는 저한테 너무 길어요. 문제는, 집에서 일해서 지금 당장 되어야 해요. 좀 더 빨리 될 방법은 없을까요?",
 "**아**너s리, / **투- 위**-ks 이z / 투- **러엉** f어r 미. 더 **씽** 이z, / 아이 **워**-rk f럼 **호**움, / 쏘우 아이 니-d 디s **워**r킹 나우. 이z 데어r **에**니 **웨**이 / 투 **s삐**-리럽?"),

("XpYmXcZKZwtpRA6bSwIk",
 "Anyway, we hit a few construction delays this week. Basically, the contractor fell behind, so the handover got pushed to next week.",
 "**A**nyway, ↘↗ / we **hit** a few → / con**struc**tion de**LAYS** → / this **week**. ↘ **Bas**ically, ↘↗ / the **con**tractor fell be**hind**, → / so the **hand**over → / got **PUSHED** to next **week**. ↘",
 "아무튼 이번 주에 공사 지연이 좀 있었어. 쉽게 말하면, 시공업체 일정이 밀려서 인수인계가 다음 주로 연기됐어.",
 "**에**니웨이, / 위 **힛** 어 f유- / 컨**s추뤅**션 디**레이z** / 디s **위-ㅋ**. **베**이씨끌리, / 더 **칸**추뤡터r f엘 비**하인d**, / 쏘우 더 **핸**도우v어r / 갓 **푸쉬ㅌ** 투 넥sㅌ **위-ㅋ**."),

("W1hH09jkmp2onMleqHQg",
 "Yeah, how long do you think it'll take? I mean, I'm kind of short on time because I need to get to work right after the move.",
 "Yeah, how **long** → / do you **think** it'll **TAKE**? ↘ I **mean**, ↘↗ / I'm **kind** of **short** on **TIME** → / because I **need** to get to **work** → / right **af**ter the **move**. ↘",
 "네, 이거 얼마나 걸릴 것 같아요? 그러니까, 제가 시간이 좀 빠듯한 게, 이사 끝나자마자 일을 하러 가야 해요.",
 "예, 하우 **러엉** / 두 유 **씽**ㅋ 이럴 **테익**? 아이 **민**, / 아임 **카인**더 **쇼**-rㅌ 온 **타임** / 비커z아이 **니**-투 겟투 **워**-rk / 롸이**래**f터r 더 **무**-v."),

("fmkrRjzi2Ju6DVOzO2bt",
 "Look, we still haven't fixed the water pressure issue or replaced the glass yet. So I'm gonna push the contractor to confirm the schedule.",
 "**Look**, ↘↗ / we **STILL ha**ven't → / **fixed** the **wa**ter **pres**sure **is**sue ↗ / or re**placed** the **glass** yet. ↘ So I'm **gon**na **push** → / the **con**tractor → / to con**firm** the **SCHED**ule. ↘",
 "저기, 수압 문제도 아직 해결 못 했고, 유리 교체도 아직 안 됐어. 그래서 contractor한테 일정 확정하라고 강하게 요구할 거야.",
 "**룩**, / 위 **s띨 해**v은ㅌ / **f익**s더 **워**러r **프뤠**셔r **이**슈 / 오r 뤼**플레이**s더 **글래**s 옛. 쏘우 아임 **거**너 **푸쉬** / 더 **컨**추뤡터r / 투 컨**f어**-rm 더 **s께**쥴."),

("CoOnPYvYJyz0bDUBDmZA",
 "So my order's about forty minutes late. And I'd really appreciate it if you could check on it and let me know when it'll get here.",
 "**So** ↘↗ / my **or**der's a**bout** → / **FOR**ty **min**utes **late**. ↘ And I'd **real**ly ap**pre**ciate it → / if you could **check** on it ↗ / and **let** me **KNOW** → / when it'll **get** here. ↘",
 "저기, 주문한 게 40분 정도 늦었어요. 그리고 확인해 보시고 언제 도착하는지 알려 주시면 정말 감사하겠어요.",
 "**쏘**우 / 마이 **오**-r더rs 어**바**웃 / **f오**-r리 **미**닛츠 **레**잇. 앤드 아으d **륄**리 어**프뤼**-쉬에이릿 / 이f 유 쿠d **체**커닛 / 앤드 **렛** 미 **노우** / 웬 이를 **겟** 히어r."),

# 24 — 연결어는 이미 있고 요일 첫 글자가 소문자로 저장돼 있던 것만 바로잡는다
("b4mxsd6ehE6cQUM76F9B",
 "Yeah, Friday works for me. If Friday doesn't work on your end, Monday's fine too. Oh, and could you let me know what time you'll get here? 'Cause I gotta give the condo admin a heads up.",
 "Yeah, ↘↗ / **FRI**day **works** for me. ↘ If **Fri**day doesn't **work** → / on your **end**, ↘↗ / **MON**day's **fine** too. ↘ Oh, and could you → / let me **know** → / what **TIME** you'll get **here**? ↗ 'Cause I **got**ta **give** → / the **con**do **ad**min → / a **HEADS** up. ↘",
 "네, 저는 금요일 괜찮아요. 만약 금요일이 그쪽 사정으로 안 되면, 월요일도 괜찮아요. 아, 그리고 몇 시에 여기 도착하실지 알려 주실 수 있어요? 제가 콘도 관리실에 미리 알려 줘야 하거든요.",
 "예아, / **f롸이**데이 **워**-rks 퍼r 미. 이f **f롸이**데이 더즌ㅌ **워**-rk / 온 요r **엔**d, / **먼**데이s **f아인** 투-. 오우 앤드 쿠쥬 / 렛 미 **노우** / 왓 **타임** 유ㄹ 겟 **히어**r? 커s 아이 **가**라 **기**v / 더 **칸**도우 **애**d민 / 어 **헤즈**업."),
]

if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    tok = token()
    print(("[DRY RUN] " if dry else "[APPLY] ") + "배치 4 — %d장" % len(B4))
    ok = 0
    for doc_id, expr, rh, ko, pron in B4:
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
        print("\n적용 %d / %d" % (ok, len(B4)))
