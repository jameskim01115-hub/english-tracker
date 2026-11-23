"""외국어 음식 이름을 영어 TTS 가 제대로 읽도록 철자를 바꿔 보낸다 (2026-11-23).

TTS 는 `gyudon` 을 영어 철자 규칙대로 읽어 「자이우던」처럼 말한다 (espeak 실측:
gyudon → dʒˈaɪuːdɑːn, gnocchi → 「나카이」, bibimbap → 「바이빔뱁」). edge-tts 경로는 SSML
`<phoneme>` 을 쓸 수 없어서 **영어식 철자로 바꿔 보내는 방법**만 모든 엔진(Neural·Kokoro)에 통한다.

규칙 (espeak 로 발음기호를 확인하며 정했다)
- **붙여 쓴다.** `gyoo-dohn` 처럼 하이픈을 넣으면 음절마다 강세가 박혀 끊어 읽는다.
- 단단한 `g` 는 `ghee`·`gah`·`goh` 로 쓴다 — `gee`·`gi` 는 `dʒ`(제이) 소리가 난다.
- 새 단어는 `FOOD_RESPELL` 에 한 줄 추가하면 된다. 여러 단어 이름은 공백으로 쓴다(`bun cha`).
- 소리는 **귀로 확인**한다. 발음기호는 영어 엔진이 읽을 모양을 점검할 뿐 진짜 음질은 못 본다.
"""
import re

FOOD_RESPELL = {
    # 일본
    "gyudon": "gheeyoodohn", "katsudon": "kahtsoodohn",
    
    "tonkatsu": "tohnkahtsoo", "tonkotsu": "tohnkohtsoo", "okonomiyaki": "ohkohnohmeeyahkee",
    "takoyaki": "tahkohyahkee", "yakitori": "yahkeetohree", "yakiniku": "yahkeeneekoo",
    "onigiri": "ohneegeeree", "unagi": "oonahghee", "izakaya": "eezahkaya",
    "sukiyaki": "sookeeyahkee", "shabu shabu": "shahboo shahboo", "omakase": "ohmahkahseh",
    "matcha": "mahchah", "tamagoyaki": "tahmahgohyahkee", "gyoza": "gheeohzah",
    "karaage": "kahrahahgeh", "tsukemen": "tsookehmen",
    # 베트남
    "bun cha": "boon chah", "bún chả": "boon chah", "bun bo hue": "boon boh hweh",
    "pho": "fuh", "phở": "fuh", "banh mi": "bahn mee", "bánh mì": "bahn mee",
    "banh xeo": "bahn seow", "goi cuon": "goy koon", "com tam": "kuhm tahm",
    "nuoc mam": "nook mahm", "cha gio": "chah yoh", "bun rieu": "boon ryoo",
    # 한국
    "bulgogi": "boolgohghee", "bibimbap": "beebeembahp", "tteokbokki": "tukbohkee",
    "japchae": "chahpcheh", "samgyeopsal": "sahmgheeuhpsahl", "galbi": "gahlbee",
    "sundubu": "soondoobooh", "jjigae": "cheegeh", "naengmyeon": "nehngmyuhn",
    "kimbap": "kimbahp", "gimbap": "kimbahp", "soju": "sohjoo", "makgeolli": "mahkuhlee",
    "jajangmyeon": "chahchahngmyuhn", "mandu": "mahndoo", "dakgalbi": "dahkgahlbee",
    "kalguksu": "kahlgooksoo",
    # 필리핀
    "sinigang": "seenigahng", "kare kare": "kahreh kahreh", "lechon": "lehchohn",
    "pancit": "pahnsit", "lumpia": "loompyah", "halo halo": "hahloh hahloh",
    "sisig": "seesig", "bangus": "bahngoos", "balut": "bahloot", "bagoong": "bahgoh ong",
    "tocino": "tohseenoh", "longganisa": "lohnggahneesah", "pandesal": "pahndehsahl",
    "ube": "oobeh", "calamansi": "kahlahmahnsee", "bulalo": "boolahloh",
    "kinilaw": "keenilow", "dinuguan": "deenoogwahn", "tapsilog": "tahpseelohg",
    "sinangag": "seenahngahg", "kaldereta": "kahldehrehtah",
    # 태국·동남아
    "tom yum": "tohm yoom", "som tam": "sohm tahm", "pad kra pao": "pahd krah pow",
    "nasi lemak": "nahsee lehmahk", "rendang": "rendahng", "satay": "sahteh",
    # 이탈리아·스페인·멕시코
    "gnocchi": "nyohkee", "bruschetta": "brooskehtah", "prosciutto": "prohshootoh",
    "quesadilla": "kehsahdeeyah", "focaccia": "fohkahchah",
    "arancini": "ahrahncheenee", "pozole": "pohsohleh", 
    # 중동·인도·중국
    "shawarma": "shahwahrmah", "biryani": "beeryahnee", "paneer": "pahneer",
    "xiaolongbao": "shyowlohngbow", "xiao long bao": "shyow lohng bow",
    "char siu": "chahr syoo", "mapo tofu": "mahpoh tohfoo", "tagine": "tahzheen",
    "dolma": "dohlmah", "baklava": "bahklahvah",
}

# 긴 이름(여러 단어)이 먼저 걸리게 길이 순으로 정렬. 복수(`-s`)도 받는다.
_KEYS = sorted(FOOD_RESPELL, key=len, reverse=True)
_RE = re.compile(
    r"(?<![\w-])(" + "|".join(re.escape(k).replace(r"\ ", r"[\s\-]+") for k in _KEYS) + r")(s?)(?![\w])(?!-\w)",
    re.IGNORECASE,
)


def _norm(word):
    return re.sub(r"[\s\-]+", " ", word.lower())


def _case_like(src, repl):
    if len(src) > 1 and src.isupper():
        return repl.upper()
    if src[:1].isupper():
        return repl[:1].upper() + repl[1:]
    return repl


def has_food(text):
    return bool(_RE.search(text))


def respell_foods(text):
    """사전에 있는 외국어 음식 이름만 영어식 철자로 바꾼다. 없으면 입력 그대로."""
    def sub(m):
        repl = FOOD_RESPELL.get(_norm(m.group(1)))
        if repl is None:
            return m.group(0)
        return _case_like(m.group(1), repl) + m.group(2)
    return _RE.sub(sub, text)
