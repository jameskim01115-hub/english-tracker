# -*- coding: utf-8 -*-
# 연결어 보강 배치 1 적용 (2026-09-30) — 17장.
# updateMask 로 expression / rhythm / ko / pron 만 PATCH 한다.
# stage · nextReview · studied · studiedAt 는 마스크에 없으므로 그대로 남는다.
import json, urllib.request, sys

KEY = "AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
REFERER = "https://jameskim01115-hub.github.io/"
PROJ = "english-tracker-cea9f"
BASE = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/english_expressions/" % PROJ

# (id, expression, rhythm, ko, pron)  — pron 이 None 이면 그 칸은 건드리지 않는다
B1 = [
("q8UIG5wpNfirekxaHfA2",
 "Well, it was raining all day, so I needed to rest and listen to some music. And honestly, it really helped me calm down.",
 "**Well**, ↘↗ / it was **RAIN**ing all **day** → / so I **needed** to **rest** ↗ / and **listen** to some music ↘ And **hon**estly, ↘↗ / it really **helped** me **CALM** down ↘",
 "음, 하루 종일 비가 와서 좀 쉬면서 음악을 들어야 했어요. 그리고 솔직히 그게 마음을 정말 진정시켜 줬어요.",
 None),

("iI9jQ77VvBLKYHGiaDe8",
 "The thing is, I had to fix some issues and help staff with their tasks, so it was hard to focus on my own work.",
 "The **thing** is, ↘↗ / I had to **fix** some **ISSUES** ↗ / and help **staff** with their tasks → / so it was **hard** to focus on my own work ↘",
 "문제는, 몇 가지 문제도 해결해야 했고 직원들 업무도 도와줘야 해서, 제 업무에 집중하기가 어려웠어요.",
 None),

("fJLsd6PkMMurQ0kpAIGS",
 "So today, we had a technical meeting with Aqualink, and on top of that, we prepared for the handover 'cause they'll start construction soon.",
 "**So** ↘↗ / today, we had a **TECH**nical meeting with Aqualink ↗ / and on **top** of that, ↘↗ / we pre**PARED** for the handover → / 'cause they'll start con**STRUC**tion soon ↘",
 "그러니까 오늘 Aqualink와 기술 미팅을 했고, 거기에다가 곧 공사를 시작할 예정이라 인계 준비도 했어요.",
 None),

("vUK3i0sexPVjGd1aqYJj",
 "Actually, I'd like to go to a Japanese restaurant tomorrow. I mean, I'm a big fan of noodles, so I'd love some udon.",
 "**Ac**tually, ↘↗ / I'd like to **GO** to a Japanese restaurant tomorrow → / I **mean**, ↘↗ / I'm a big **FAN** of noodles → / so I'd **LOVE** some udon ↘",
 "사실 내일 일식당에 가고 싶어요. 그러니까, 제가 면 요리를 정말 좋아해서 우동이 정말 먹고 싶어요.",
 None),

("E9qqbqc7qEDay217teLf",
 "Right, I understand your concern. At the same time, this is already the best rate we can offer, but we can offer you a rent-free period instead.",
 "**Right**, ↘↗ / I understand your con**CERN** → At the same **TIME** ↘↗ / this is already the best **RATE** we can offer ↗ / but we can offer you a rent-free period in**STEAD** ↘",
 "맞습니다, 말씀하시는 부분은 이해합니다. 다만 현재 임대료가 저희가 드릴 수 있는 최선의 조건이고, 대신 렌트프리 기간을 제공해 드릴 수 있습니다.",
 None),

("ajK2NWN5tCSzlH5MjG2G",
 "The thing is, the water pressure's really weak. When you run the water in the bathroom, there's barely any pressure. So we gotta fix it before the tenants move in.",
 "The **thing** is, ↘↗ / the water pressure's **REAL**ly weak. ↘ / When you run the water in the bathroom ↘↗ / there's barely any **PRES**sure. ↘ / So we gotta fix it → / before the tenants **MOVE** in. ↓",
 "문제는, 수압이 너무 약해요. 화장실에서 물을 틀면 압력이 거의 없어요. 그래서 임차인 입주 전에 고쳐야 합니다.",
 "더 **씽** 이z, / 더 워러r 프레셔rz **뤼**얼리 위-ㅋ / 웬 유 런 더 워러린 더 배쓰룸 / 데어rz 베어r리 애니 **프레**셔r / 쏘우 위 가라 픽씻 / 비포r 더 테넌츠 **무**-빈"),

("TEOtaPlzkYuDMWJ42hDE",
 "Well, I usually don't do much on weekends. I mean, I just relax and watch some Netflix, and sometimes I go for a run.",
 "**Well**, ↘↗ / I usually **don't** do much → / on **week**ends. ↘ I **mean**, ↘↗ / I just re**lax** ↗ / and watch some **Net**flix, ↗ / and sometimes I go → / for a **RUN**. ↘",
 "음, 주말에는 보통 별로 안 해요. 그러니까, 그냥 쉬면서 넷플릭스를 보고, 가끔은 달리기를 하러 가요.",
 "**웰**, / 아이 유주얼리 **도운ㅌ** 두 머치 / 온 **위켄**즈. 아이 **민**, / 아이 저슽 **릴랙스** / 앤 왓치 섬 **넽플릭스**, / 앤 섬타임즈 아이 고우 / 포r 어 **런**."),

("cfsMFwqcLiQbEQJmbunD",
 "So I heard Da Nang has a lot of Korean restaurants and cafés. Actually, some people call it a little Korea.",
 "**So** ↘↗ / I **heard** Da Nang has a **lot** of Ko**re**an restaurants and ca**fés**. ↘ **Ac**tually, ↘↗ / some people **call** it a **lit**tle Ko**RE**a. ↘",
 "그게, 다낭에는 한국 식당이랑 카페가 많다고 들었어요. 사실, 어떤 사람들은 거기를 리틀 코리아라고 부르더라고요.",
 "**쏘**우 / 아이 **허-rd** 다낭 해z 얼**라**러v 커**뤼**-언 뤠s추란츠 앤드 캐**f에**이z. **액**츄얼리, / 썸 피뽈 **커어**릿 얼**리**를 커**뤼**-어."),

("fREn43wph2kZaV4HcM1j",
 "Yeah, I liked it there. As you know, Bangkok has a lot of tourist spots. And I really liked the Thai massage and Thai food.",
 "Yeah, ↘↗ / I **liked** it there. ↘ As you **know**, **Bang**kok has a **LOT** of tourist spots. ↘ And I really **liked** the Thai mas**sage** ↗ / and **THAI** food. ↘",
 "네, 거기 좋았어요. 아시다시피 방콕에는 관광지가 많잖아요. 그리고 타이 마사지랑 태국 음식이 정말 좋았어요.",
 "예, / 아이 **라익ㅌ** 잇 데어r. 애쥬 **노우**, **방**칵 해z **얼라러v** 투어리sㅌ s빳츠. 앤드 아이 뤼얼리 **라익ㅌ** 더 타이 마**싸**-지 / 앤드 **타이** f우-d."),

("hcrHtDuyXjsUIid3vxjY",
 "You know, I'm a big fan of noodles, so I'd love to try some pho or rice noodles. Actually, when I watched YouTube, I saw a lot of famous noodle dishes at local restaurants.",
 "You **know**, ↘↗ / I'm a **big** fan of **noo**dles, → so I'd **love** to try some **pho** ↗ / or **rice** noodles. ↘ **Ac**tually, ↘↗ when I **watched** YouTube, ↘↗ I saw a lot of **fa**mous **NOO**dle dishes → / at **lo**cal restaurants. ↘",
 "있잖아요, 제가 면 요리를 정말 좋아해서 쌀국수나 쌀면을 꼭 먹어보고 싶어요. 사실, YouTube를 봤을 때 현지 식당의 유명한 면 요리를 많이 봤거든요.",
 "유 **노**우, / 아임 어 **빅** f앤 어v **누**-를z, 쏘우 아이d **러v** 투 추롸이 썸 **f어** / 어r **롸이s** 누-를z. **액**츄얼리, 웬 아이 **와취ㅌ** 유-투-b, 아이 써어 얼라러v **f에이**머스 **누**-를 디쉬z / 앳 **로우**커ㄹ 뤠s추란츠."),

("Q5VMoPBjwD8zNUzHHU9Y",
 "So at that restaurant, you can pick the meat, veggies, and spice level. And I actually asked the staff how the meat is cooked.",
 "**So** ↘↗ / at that **res**taurant ↘↗ / you can **pick** the meat, **veg**gies, and spice **LEV**el ↘ And I **act**ually **asked** the **STAFF** → / how the meat is **cooked** ↘",
 "그러니까 그 식당에서는 고기, 채소, 매운맛 단계를 고를 수 있어요. 그리고 저는 사실 직원에게 고기가 어떻게 조리되는지 물어봤어요.",
 None),

("dAgnvhngLw1qUWax27g6",
 "Honestly, it wasn't easy 'cause there were a lot of steps. And I had to fix it again and again. I finally got it, though.",
 "**Hon**estly, ↘↗ / it **was**n't **EA**sy → / 'cause there were a lot of **steps** ↘ And I had to **fix** it a**GAIN** and again ↘ I **fi**nally **GOT** it, though ↘",
 "솔직히 쉽지 않았어요. 여러 단계를 거쳐야 했거든요. 그리고 몇 번이고 다시 수정해야 했어요. 결국 해내긴 했지만요.",
 None),

("6DK3hXuc30rZvmZ08OoY",
 "Yeah, it's going pretty well, but we ran into a few problems. On top of that, the contractor kept pushing back the schedule, so I had to sort it out myself.",
 "Yeah, ↘↗ / it's going pretty well ↗ / but we ran into a few **PROB**lems. ↘ On **top** of that, ↘↗ / the contractor kept pushing back the **SCHED**ule → / so I had to sort it out my**SELF**. ↘",
 "네, 꽤 잘 진행되고 있는데, 문제가 몇 개 생겼어요. 거기에다가 시공사가 일정을 계속 미뤄서 제가 직접 해결해야 했어요.",
 "예, / 잇츠 고잉 프리리 웰 / 벗 위 래닌투 어 퓨- **프라**블럼z / 온 **탑** 어v 댓, / 더 컨트랙터r 켑ㅌ 푸싱 백 더 **스케**쥴 / 쏘우 아이 핻투 쏘r릿 아웃 마이**쎌**f"),

("EYsUmKlqT5DMU9qRE3Sl",
 "Well, I don't have a plan yet, but I'm thinking about taking a tour. So I'll look for a travel company or search for something online.",
 "**Well**, ↘↗ / I don't have a **plan** yet, ↗ but I'm **think**ing about **tak**ing a tour. ↘ So I'll **look** for a **tra**vel company ↗ / or **search** for something **ON**line. ↘",
 "음, 아직 계획은 없는데 투어를 할까 생각 중이에요. 그래서 여행사를 알아보거나 온라인으로 검색해볼게요.",
 "**웰**, / 아이 도운ㅌ 해v 어 **플랜** 옛ㅌ, 벗 아임 **씽**킹 어바웃 **테이**킹 어 투어r. 쏘우 아으L **룩** f어러 **추뤠**v어ㄹ 컴퍼니 / 어r **써-r취** f어r 썸씽 **안**라인."),

("8yI3FsFgHg1W2KfznQLS",
 "The thing is, after the handover, I'd like some rest, but I've already signed contracts and I have a lot of work to do.",
 "The **thing** is, ↘↗ / after the **hand**over, ↘↗ / I'd **like** some rest, ↗ but I've al**rea**dy signed **con**tracts ↗ and I have a **LOT** of work to do. ↘",
 "문제는, 인계가 끝나면 좀 쉬고 싶은데, 이미 계약을 여러 건 체결해서 할 일이 많아요.",
 "더 **씽** 이z, / 애f터r 더 **핸**도우v어r, / 아이d **라익** 섬 레sㅌ, / 벝 아이v 얼**레**리 싸인d **컨**트뤡츠 / 앤드 아이 해v 어 **랕** 어v 워-rㅋ 투 두-."),

("Qou8L4dcjTxHtOzlBPYP",
 "Yeah, today we prepared for the handover. So we had a meeting with Aqualink to go over some issues and their requests, and this week we gotta make a few decisions.",
 "Yeah, ↘↗ / to**day** ↘↗ / we pre**pared** → / for the **hand**over. ↘ So we had a **meet**ing → / with **A**qualink → to go **o**ver some **is**sues ↗ / and their re**quests**, → and this **week** → / we **got**ta make a few de**CI**sions. ↓",
 "네, 오늘은 인계 준비를 했어요. 그래서 Aqualink와 미팅을 해서 몇 가지 이슈와 요청 사항을 검토했고, 이번 주에 몇 가지를 결정해야 해요.",
 "예, / 투**데**이 / 위 프리**페어rd** / f어r 더 **핸**도우v어r. 쏘우 위 해더 **미-**링 / 위드 **아**콰링ㅋ / 투 고우 **오**우v어r 섬 **이**슈z / 앤드 데어r 리**퀘s**츠, / 앤드 디s **위-ㅋ** / 위 **가**라 메이커 f유- 디**씨**전z."),

("zG0XqhNrOjLFijtbZao1",
 "Well, I usually run alone, 'cause if I run with others, I end up following their pace. I'd rather keep my own, though.",
 "**Well**, ↘↗ / I usually **run** a**lone**, → '**cause** if I run with **o**thers, ↘↗ I end up **fo**llowing their **pace**. ↘ I'd **RA**ther keep my **own**, though ↘",
 "음, 저는 보통 혼자 뛰어요. 다른 사람이랑 뛰면 결국 그 사람 페이스를 따라가게 되거든요. 제 페이스를 지키는 게 낫긴 해요.",
 "**웰**, / 아이 유주얼리 **뤈** 어**로운**, / **커z** 이f 아이 뤈 위드 **어**더rz, / 아이 엔덥 **f아**로잉 데어r **페이s**. / 아이d **뢔**더r 킾 마이 **오운**, 도우."),
]


def token():
    req = urllib.request.Request(
        "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + KEY,
        data=json.dumps({"returnSecureToken": True}).encode(),
        headers={"Content-Type": "application/json", "Referer": REFERER})
    return json.load(urllib.request.urlopen(req))["idToken"]


def patch(tok, doc_id, fields):
    mask = "".join("&updateMask.fieldPaths=" + k for k in fields)
    url = BASE + doc_id + "?" + mask[1:]
    body = {"fields": {k: {"stringValue": v} for k, v in fields.items()}}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="PATCH",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + tok, "Referer": REFERER})
    return json.load(urllib.request.urlopen(req))


if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    tok = token()
    print(("[DRY RUN] " if dry else "[APPLY] ") + "배치 1 — %d장" % len(B1))
    ok = 0
    for doc_id, expr, rh, ko, pron in B1:
        fields = {"expression": expr, "rhythm": rh, "ko": ko}
        if pron is not None:
            fields["pron"] = pron
        if dry:
            print("  %s  %s" % (doc_id, " ".join(sorted(fields))))
            continue
        try:
            patch(tok, doc_id, fields)
            ok += 1
            print("  ok  %s  (%s)" % (doc_id, " ".join(sorted(fields))))
        except Exception as e:
            print("  FAIL %s  %s" % (doc_id, e))
    if not dry:
        print("\n적용 %d / %d" % (ok, len(B1)))
