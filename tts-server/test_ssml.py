"""build_ssml 검증 — server.py 에서 순수 함수만 뽑아 돌린다 (ONNX 모델 없이).

가장 중요한 검사는 XML 파싱이다. 눈으로 보는 검사는 `</emphasis>` 가 깨진 걸 놓쳤다.
"""
import ast
import re
import sys
import xml.etree.ElementTree as ET

src = open("server.py").read()
tree = ast.parse(src)
WANT_FN = {"unstress_caps", "_xml_escape", "build_ssml", "clean"}
WANT_CONST = {"SPELL_OUT", "BR", "MAX_CHARS"}
parts = []
for n in tree.body:
    if isinstance(n, ast.FunctionDef) and n.name in WANT_FN:
        parts.append(ast.get_source_segment(src, n))
    elif isinstance(n, ast.Assign) and any(getattr(t, "id", None) in WANT_CONST for t in n.targets):
        parts.append(ast.get_source_segment(src, n))
ns = {"re": re}
exec("\n\n".join(parts), ns)
build_ssml, unstress, BR = ns["build_ssml"], ns["unstress_caps"], ns["BR"]

CASES = [
    ("Honestly, → / I just can't **STAND** → / **ungrateful** people. ↘", "피크+일반+청크+하강"),
    ("They **always** take / **everything** for **GRANted**. ↘", "여러 강세"),
    ("The **CUSA** fee is due.", "SPELL_OUT 약어는 대문자 유지"),
    ("I need to de**POS**it it.", "단어 조각"),
    ("Let's **MOVE FORWARD WITH** it. ↘", "여러 단어 피크"),
    ("Tom & Jerry <fun> \"quotes\" 'apos'", "XML 이스케이프"),
    ("Plain sentence with no markup.", "표기 없음"),
    ("", "빈 문자열"),
    ("/ / / leading slashes", "슬래시 연속"),
    ("**unclosed bold", "짝 안 맞는 볼드"),
    (f"null{BR}injected", "자리표시자 주입 시도"),
]

fails = []
for text, label in CASES:
    out = build_ssml(text, "en-US-EmmaNeural", 0.9)
    print(f"\n[{label}]\n  in : {text!r}")
    try:
        root = ET.fromstring(out)                       # ← 핵심 검사
    except ET.ParseError as e:
        print(f"  ❌ XML 파싱 실패: {e}\n  raw: {out}")
        fails.append(label)
        continue
    body = out.split("<prosody", 1)[1].split(">", 1)[1].rsplit("</prosody>", 1)[0]
    print(f"  out: {body}")

    spoken = "".join(root.itertext())
    if "**" in body:
        print("  ❌ ** 잔존"); fails.append(label)
    if re.search(r"[/↘↓→↗]", spoken):
        print("  ❌ 표기 기호가 읽히는 텍스트에 남음"); fails.append(label)
    if BR in out:
        print("  ❌ 자리표시자 잔존"); fails.append(label)
    # emphasis 태그 개수 = 원문 볼드 쌍 개수
    want = len(re.findall(r"\*\*(.+?)\*\*", text))
    # speak 에 xmlns 가 있어 자식 태그도 네임스페이스가 붙는다 — 접미사로 센다.
    got = sum(1 for el in root.iter() if el.tag.rsplit("}", 1)[-1] == "emphasis")
    if want != got:
        print(f"  ❌ emphasis {got}개, 기대 {want}개"); fails.append(label)

print("\n=== 속도 매핑 ===")
rate_re = re.compile(r"rate='([^']+)'")
for sp in (0.7, 0.8, 0.9, 1.0, 1.1):
    got = rate_re.search(build_ssml("hi", "v", sp)).group(1)
    exp = "%+d%%" % round((sp - 1) * 100)
    mark = "✅" if got == exp else "❌"
    print(f"  {mark} {sp} -> {got}")
    if got != exp:
        fails.append(f"speed {sp}")

print("\n=== 대문자 처리 ===")
for t, exp in [("**STAND**", "**stand**"), ("**CUSA**", "**CUSA**"), ("AQUALINK", "aqualink"),
               ("de**POS**it", "de**pos**it"), ("**SAME HERE**", "**same here**")]:
    got = unstress(t)
    mark = "✅" if got == exp else "❌"
    print(f"  {mark} {t!r:18} -> {got!r}")
    if got != exp:
        fails.append(f"caps {t}")

# clean() — SSML 을 안 쓰는 경로(현재 기본). 대문자를 반드시 벗겨야 한다.
# 안 벗기면 TTS 가 약어로 보고 철자를 읽는다 (UNWIND → 유엔윈드).
print("\n=== clean() — 평문 경로 ===")
clean = ns["clean"]
CLEAN_CASES = [
    ("I just can't **STAND** / ungrateful people. ↘", "I just can't stand ungrateful people."),
    ("The **CUSA** fee is due.", "The CUSA fee is due."),          # SPELL_OUT 은 유지
    ("AQUALINK called.", "aqualink called."),
    ("already lowercase text", "already lowercase text"),          # 멱등 — 기존 캐시 키 보존
    ("de**POS**it it", "deposit it"),
]
for src_t, exp in CLEAN_CASES:
    got = clean(src_t)
    mark = "✅" if got == exp else "❌"
    print(f"  {mark} {src_t!r}\n      -> {got!r}")
    if got != exp:
        print(f"      기대: {exp!r}")
        fails.append(f"clean {src_t[:20]}")
# 대문자가 하나라도 남으면(SPELL_OUT 제외) 철자로 읽힌다
import re as _re
leftover = _re.findall(r"[A-Za-z']*[A-Z]{2,}[A-Za-z']*", clean("**STAND** and **GRANTED** ↘"))
bad = [w for w in leftover if w not in ns["SPELL_OUT"]]
print(f"  {'✅' if not bad else '❌'} 대문자 잔존: {bad or '없음'}")
if bad:
    fails.append("clean caps leftover")

print("\n" + ("❌ 실패: " + ", ".join(fails) if fails else "✅ 전부 통과"))
sys.exit(1 if fails else 0)
