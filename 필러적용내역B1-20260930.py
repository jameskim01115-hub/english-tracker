# -*- coding: utf-8 -*-
# B안 (13~19단어 구간) 적용 (2026-09-30) — 손볼 후보 41장 중 21장.
# 판정 내역과 손 안 댄 20장의 이유는 필러배치B1-20260930.md 참조.
# updateMask 로 expression / rhythm / ko / pron 만 PATCH. pron 이 원래 없던 카드는 만들지 않는다.
import sys, os, importlib.util

_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "필러적용내역A1-20260930.py")
_s = importlib.util.spec_from_file_location("filler_a1", _p)
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)
token, patch = _m.token, _m.patch

# ═══ ③ 맨 앞 갈래 흩기 — 이 구간에 Honestly 가 8장 몰려 있었다 (7장 교체, 1장 유지) ═══
B_HEAD = [
("piTRyfURzy69PwqP4Sdu",  # Honestly → I guess  (계획·예상은 부드럽게)
 "I guess I'll just come home and study English or practice conversation with you like today.",
 "I **guess** ↘↗ / I'll just come **HOME** ↗ / and study **ENG**lish ↗ / or practice conversation with you like to**DAY** ↘",
 "아마 그냥 집에 와서 영어 공부를 하거나 오늘처럼 너와 회화 연습을 할 것 같아요.", None),

("FbedYNcy6UFqzCENXIJP",  # Honestly → The thing is  (문제 설명)
 "The thing is, the contractor's almost done with the job but they left a lot of stuff unfinished.",
 "The **thing** is, ↘↗ / the con**tract**or's **al**most **done** → / with the **job** ↗ / but they **left** a **lot** of stuff → / un**FIN**ished. ↘",
 "문제는, 시공사가 공사를 거의 끝냈는데 마무리 안 된 게 많아요.",
 "더 **씽** 이z, / 더 컨**추뤡**터rz **어ㄹ모우s던** / 위더 **좝** / 벗 데이 **레f트** 어 **랏** 어v s떠f / 언**f이니**쉬ㅌ."),

("iMUDPDSjXdtL2WNlqhVy",  # Honestly → Well  (하루 얘기를 여는 자리)
 "Well, it was raining all day, so I wanted noodles, and after eating, I felt satisfied.",
 "**Well**, ↘↗ / it was **rain**ing all **DAY** → / so I **want**ed noodles → / and after **eat**ing ↘↗ / I felt **sat**isfied ↘",
 "음, 하루 종일 비가 와서 면 요리가 먹고 싶었고, 먹고 나니 만족스러웠어요.", None),

("kg1eWixtHuaDyvFDczfc",  # Honestly → To be honest  (같은 갈래, 227장에 0건이던 형태)
 "To be honest, sometimes when I speak English, I feel flat, like I don't have any emotion.",
 "To be **hon**est, ↘↗ / sometimes when I **speak** English ↘↗ / I feel **FLAT** → / like I don't have any e**mo**tion ↘",
 "솔직히 말하면 가끔 영어로 말할 때 감정이 전혀 없는 것처럼 밋밋하게 느껴져요.", None),

("3fNe5EycChNW6Js58VZK",  # Honestly → Actually
 "Actually, I was pretty busy today. I mean, I had a lot to do.",
 "**Ac**tually, ↘↗ / I was **pretty BUSY** today. ↘ I **mean**, ↘↗ / I had a **LOT** to do. ↘",
 "사실 오늘은 꽤 바빴어요. 그러니까, 할 일이 많았거든요.",
 "**액**츄얼리, / 아이 워z **프뤼리 비지** 터데이. 아이 **미**-ㄴ, / 아이 해러 **랏** 터 두."),

("7dxwP1aEm4ARQsDuqESs",  # Honestly → You know  (부드럽게 — 이 갈래가 12장뿐이었다)
 "You know, I felt relieved 'cause it had been bugging me while I studied English.",
 "You **know**, ↘↗ / I felt re**LIEVED** → / 'cause it had been **bug**ging me → / while I **stud**ied **Eng**lish ↘",
 "있잖아요, 영어 공부를 할 때 계속 신경 쓰이던 거라서 마음이 놓였어요.", None),

("q0zgYrjZyDNsIHJScfty",  # Honestly → So  (3fNe5E 와 문장이 거의 같아 둘 다 Honestly 면 중복이 확연하다)
 "So I was pretty busy today 'cause we were preparing for the Metrobank handover.",
 "**So** ↘↗ / I was **pret**ty **bu**sy to**day** → / 'cause we were pre**par**ing for → / the **Met**robank **HAND**over. ↘",
 "그래서 오늘 꽤 바빴어. Metrobank 인수인계를 준비하고 있었거든.",
 "**쏘**우 / 아이 워s **프뤼**리 **비**z이 터**데이** / 커z 위 워r 프뤼**페어**r링 퍼r / 더 **메**추로우뱅ㅋ **핸**도우v어r."),
]

# ═══ ② 필러·연결어가 전혀 없던 카드 ═══
B_NONE = [
("MIjidiow2nj69qS2uo8F",
 "I actually run a few marathons a year. And when I'm running with a big crowd, I feel really alive.",
 "I **ac**tually run a few **ma**rathons a **year**. ↘ And when I'm running with a **big crowd**, ↘↗ I feel really a**LIVE**. ↘",
 "사실 일 년에 마라톤을 몇 번 뛰어요. 그리고 많은 사람들과 같이 뛰면 정말 살아있다는 느낌이 들어요.",
 "아이 **액**츄얼리 뤈 어 f유 **매**뤄썬z 어 **이어r**. / 앤드 웬 아임 뤄닝 위드어 **빅 크롸우d**, / 아이 f이-ㄹ 뤼얼리 어**라이v**."),

("ZDv8gszmRGRakGh1S9sF",
 "Well, I was a bit tired 'cause I had to do a lot today.",
 "**Well**, ↘↗ / I was a bit **TIRED** → / 'cause I had to do a **lot** today ↘",
 "음, 오늘은 할 일이 많아서 좀 피곤했어요.", None),
]

# ═══ ① 문장이 나열돼 있던 카드 (26장 중 12장) ═══
B_LIST = [
("4ffYiBAKAtDVYCFSxmlL",
 "Can you check the as-built plan before our Aqualink meeting? I mean, I just wanna make sure everything is ready.",
 "Can you **check** → / the as-**built** plan → / before our Aqualink **MEET**ing ↗ I **mean**, ↘↗ / I just wanna → / make **SURE** → / everything is **read**y ↘",
 "Aqualink 미팅 전에 as-built plan 확인해줄래요? 그러니까, 그냥 모든 게 준비됐는지 확실히 확인하고 싶어요.",
 "캔뉴 **첵** / 디 애z-**빌ㅌ** 플랜 / 비f오-r 아워r Aqualink **미**-링 아이 **민**, / 아이 저sㅌ 워너 / 메익 **슈어r** / 에v리씽 이z **뤠**디"),

("6kp0jPoSxJPv6CKB436k",
 "Well, when I relax I usually watch Netflix or some Korean shows. And sometimes I catch up on a show.",
 "**Well**, ↘↗ / when I re**LAX** ↘↗ / I usually watch **NET**flix or some Korean shows ↘ And sometimes I catch **UP** on a show ↘",
 "음, 쉴 때는 보통 넷플릭스나 한국 프로그램을 봐요. 그리고 가끔 밀린 프로그램도 봐요.", None),

("GHbtkWdkyBWnlbv3kSOc",
 "Yeah, I didn't do much after work. I just relaxed and watched a Korean TV show, and honestly, I felt relieved.",
 "Yeah, ↘↗ / I didn't do **much** after **WORK**. ↘ I just re**laxed** and watched a Korean **TV** **show**, → / and **hon**estly, ↘↗ / I felt re**lieved** ↘",
 "네, 퇴근 후에는 별거 안 했어요. 그냥 쉬면서 한국 TV 프로그램을 봤는데, 솔직히 마음이 좀 놓였어요.", None),

("R7XMTfjBZcuEWmLh5dUR",
 "Yeah, I just relaxed and watched some YouTube for a while. I didn't really feel like doing anything serious, I guess.",
 "Yeah, ↘↗ / I just re**LAXED** ↗ / and watched some **YOU**Tube for a while ↘ I didn't really feel like doing anything **SE**rious, / I **guess** ↘↗",
 "네, 그냥 쉬면서 한동안 YouTube를 봤어요. 딱히 뭔가 제대로 하고 싶은 기분은 아니었던 것 같아요.", None),

("zvktJt7LjDkQVHpLyD63",
 "Honestly, if they delay again, I'll bring in another contractor. But I'm hoping we can wrap it up this week.",
 "**Hon**estly, ↘↗ / if they de**lay** a**gain**, ↘↗ / I'll bring **in** → / a**no**ther **CON**tractor. ↘ But I'm **hop**ing ↗ / we can **wrap** it **up** → / this **WEEK**. ↘",
 "솔직히 또 지연되면 다른 contractor를 투입할 거야. 그래도 이번 주 안에 마무리할 수 있으면 좋겠어.",
 "**아**너s리, / 이f 데이 디**레이** 어**겐**, / 아으L 브뤼**닌** / 어**너**더r **컨**추뤡터r. 벗 아임 **호우**핑 / 위 큰 **뤠**피**럽** / 디s **위**-ㅋ."),

("7WnsbbmKVzQiDWZNX0vr",
 "I just wanna sleep in and take it easy this weekend. 'Cause I don't really have any big plans.",
 "I just wanna **sleep** in ↗ / and take it **easy** → / this **WEEK**end ↘ 'Cause I don't **really** have → / any big **PLANS** ↘",
 "이번 주말에는 그냥 늦잠 자고 푹 쉬고 싶어. 딱히 큰 계획이 없거든.",
 "아이 저s 워너 **슬리**핀 / 앤드 테이키**리지** / 디s **위켄d** 커z 아이 도운ㅌ **뤼얼리** 해v / 애니 빅 **플랜z**"),

("yua2zSxRlFNfzMKai3lD",
 "So today, we had a problem with a staff member. Basically, our building manager Neil isn't really taking responsibility.",
 "**So** ↘↗ / to**day** ↘↗ / we had a **PROB**lem → / with a **staff** member ↘ **Bas**ically, ↘↗ / our **build**ing manager **NEIL** → / isn't really taking responsibility ↘",
 "그게, 오늘 직원 한 명과 관련해서 문제가 있었어요. 쉽게 말하면, 우리 빌딩 매니저 Neil이 자기 책임을 제대로 다하지 않고 있어요.", None),

("6YZiJXAwhwrh11ewv0Ib",
 "I just wanna keep it low-key tonight. So I'll probably watch some Netflix and get some noodles.",
 "I just wanna keep it **LOW**-key → / tonight ↘ So I'll **probably** watch some **Netflix** ↗ / and get some **NOO**dles ↘",
 "오늘 밤은 그냥 조용하고 편하게 보내고 싶어. 그래서 아마 Netflix 좀 보고 국수도 먹을 것 같아.",
 "아이 저s 워너 키핏 **로우**키 / 트나잇 쏘우 아으L **프라블리** 와치 썸 **넷플릭s** / 앤드 겟 썸 **누**-를z"),

("7GIXRkLuxoHYjsXzqKgE",
 "I was wondering if you could deliver them right now. 'Cause I've gotta prep for dinner tonight.",
 "I was **won**dering ↗ / if you could de**liv**er them / **RIGHT NOW**. ↘ 'Cause I've gotta **PREP** → / for **din**ner to**night**. ↘",
 "지금 바로 보내주실 수 있을까 해서요. 오늘 저녁 준비를 해야 하거든요.",
 "아이 워z **원**더륑 / 이f유 쿠d 딜**리**v어r 뎀 / **롸잇 나우**. 커z 아이v **가**라 **프뤱** / f어r **d이**너r 투**나잇**."),

("dmXoAbERWJqvegO5qbmt",
 "I wanna listen every day. I mean, it hasn't been easy, but I wanna make it a habit.",
 "I wanna **lis**ten every **DAY** ↘ / I **mean**, ↘↗ / it hasn’t been **ea**sy ↗ / but I wanna make it a **hab**it ↘",
 "매일 들으려고 해요. 그러니까, 쉽지는 않았지만 습관으로 만들고 싶어요.", None),

("gt3Mi9K5WhNpR1Jo6k68",
 "Yeah, yesterday was Sunday, but I didn't do much. So I just relaxed and watched some Netflix.",
 "Yeah, ↘↗ / **YES**terday was **Sunday** ↗ / but I didn't do **much** → / So I just re**laxed** and watched some **NET**flix ↘",
 "네, 어제는 일요일이었는데 별거 안 했어. 그래서 그냥 쉬면서 Netflix 좀 봤어.", None),

("n7TLdj4Yif2ETiWJkUSy",
 "Oh, it reminds me of high school. You know, we used to sing it together at noraebang.",
 "**Oh**, ↘↗ / it re**minds** me of high **SCHOOL** ↘ You **know**, ↘↗ / we **used** to **sing** it to**geth**er → / at **NORAEBANG** ↘",
 "아, 그 노래를 들으면 고등학교 시절이 생각나요. 있잖아요, 우리는 노래방에서 그 노래를 같이 부르곤 했어요.", None),
]

B1 = B_HEAD + B_NONE + B_LIST

if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    tok = token()
    print(("[DRY RUN] " if dry else "[APPLY] ") + "B안 배치 — %d장" % len(B1))
    ok = 0
    for doc_id, expr, rh, ko, pron in B1:
        fields = {"expression": expr, "rhythm": rh, "ko": ko}
        if pron is not None:
            fields["pron"] = pron
        if dry:
            print("  %s  %s" % (doc_id, " ".join(sorted(fields))))
            continue
        try:
            patch(tok, doc_id, fields); ok += 1
            print("  ok  %s" % doc_id)
        except Exception as e:
            print("  FAIL %s  %s" % (doc_id, e))
    if not dry:
        print("\n적용 %d / %d" % (ok, len(B1)))
