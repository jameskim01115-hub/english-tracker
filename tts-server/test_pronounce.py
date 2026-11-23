"""pronounce.py 검증 — `python3 test_pronounce.py`"""
from pronounce import FOOD_RESPELL, has_food, respell_foods

CASES = [
    ("I had gyudon for lunch.", "I had gheeyoodohn for lunch."),
    ("Let's get Bun Cha tonight", "Let's get Boon chah tonight"),
    ("Two bun-cha please", "Two boon chah please"),
    ("I love pho and banh mi.", "I love fuh and bahn mee."),
    ("We ordered gnocchis.", "We ordered nyohkees."),
    ("GYUDON is great", "GHEEYOODOHN is great"),
    ("I want an ice cream sundae.", "I want an ice cream sundae."),   # 영어 단어는 안 건드림
    ("The pho-tograph", "The pho-tograph"),                            # 단어 조각은 안 건드림
    ("No food here.", "No food here."),
    ("", ""),
]
fails = 0
for src, want in CASES:
    got = respell_foods(src)
    ok = got == want
    fails += not ok
    print(("OK  " if ok else "FAIL"), repr(src), "->", repr(got))
assert has_food("gyudon") and not has_food("hello")
for k, v in FOOD_RESPELL.items():           # 대체 철자에 하이픈·공백 규칙 점검
    assert "-" not in v, k
print("fails:", fails)
raise SystemExit(1 if fails else 0)
