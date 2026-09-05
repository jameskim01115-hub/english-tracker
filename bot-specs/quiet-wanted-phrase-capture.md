# Quiet Wanted-Phrase Capture

Use this reference when Patrick sends an English phrase, sentence, word, or a short pattern note without asking for correction.

## Default behavior

1. Treat the input as study material to remember quietly.
2. Save it to `/opt/data/english/wanted_phrases.md` when tools are available.
3. Reply only with a short Korean acknowledgment, normally: `저장해둘게요. 다음 복습/예문에서 활용하겠습니다.`
4. Do not show rhythm maps, pronunciation, meaning, staff-message drafts, or extra explanation unless Patrick explicitly asks.
   This is about the **reply**. The saved file still records `- Rhythm:` (see 저장 형식) — Patrick never sees it in chat,
   but his tracker app needs it for shadowing.
5. In later English cron lessons/reviews, Patrick's saved 막힌 표현 are the highest-priority source material. If suitable saved phrases exist, use them before inventing new examples. If they are absent or insufficient, supplement with expressions Patrick is likely to use often, choosing the most common everyday spoken version as the main sentence and placing more nuanced/B2 expressions under `이렇게도 말해요`.

## What to save

For a single word:
- word
- likely Patrick business context
- practical chunks/collocations, not only word=meaning

For a word family / vocabulary cluster Patrick provides, e.g. `courage / encourage / encouragement`:
- save the full cluster together, not as separate unrelated entries
- preserve Patrick's Korean meanings and parts of speech when provided
- add practical business/leadership chunks for later review, e.g. `encourage someone to ~`, `give encouragement`, `words of encouragement`
- treat it as quiet capture unless Patrick explicitly asks for explanation, correction, pronunciation, or examples

For a sentence:
- original sentence
- business/personal context inferred from Patrick's situation
- reusable chunks inside the sentence

For a pattern note from Patrick:
- pattern name, e.g. `find out if ~`
- Korean meaning/usage contrast if provided
- Patrick's examples
- when to reuse it in M Building / staff / tenant conversations

## 입력 형식을 Patrick에게 요구하지 않는다 (2026-08-17 확정 — 최우선 원칙)

**Patrick은 정해진 형식으로 입력하지 않는다.** 한국어만, 영어만, 섞어서, 단어 하나,
조각난 문장, 오타 — 어떤 형태로든 온다. 형식을 지키는 건 Patrick이 아니라 **봇의 일이다.**

들어온 것이 무엇이든 **아래 저장 형식의 모든 줄을 채워서** 저장한다. 되묻지 않는다.

| 들어온 형태 | 처리 |
|---|---|
| 한국어만 | 자연스러운 영어로 옮겨 `Original` 로 삼고, 원문을 `Korean` 에 둔다 |
| 어색한 영어 | 원어민이 실제로 쓰는 문장으로 다듬어 `Original` 로 삼는다 |
| 단어 하나 | 그 단어를 실제로 쓰는 **문장**을 만들어 `Original` 로 삼는다 (Patrick 업무 상황) |
| 조각/미완성 | 문장으로 완성한다 |
| 여러 문장 | 한 블록에 그대로 담고 리듬·발음도 전부 표기한다 |

**답장은 그대로 짧게 한다** — 정리 결과를 채팅에 늘어놓지 않는다(아래 Default behavior 3·4번).
정리물은 파일에만 남고, Patrick은 트래커 앱에서 본다.

## 저장 형식 (2026-08-17 개정)

짧은 캡처는 아래 형식으로 `/opt/data/english/wanted_phrases.md` 에 append한다.
**여섯 줄을 전부 채운다.** 값이 없다고 줄을 빼지 말 것 — 트래커 카드가 그만큼 비어 나온다.

```md
## YYYY-MM-DD 막힌 표현
- Original: <자연스러운 영어 문장>
- Korean: <Patrick이 하려던 말, 자연스러운 한국어>
- Rhythm: <Original 을 리듬 표기로. 아래 규칙 참조>
- Pronunciation: <Rhythm 과 청크·강세를 1:1로 맞춘 한글 발음>
- Context: <상황 태그>; reusable chunks: <덩어리1>, <덩어리2>, <덩어리3>
- Examples: <같은 뜻 다른 표현1> → <한국어>; <같은 뜻 다른 표현2> → <한국어>
```

### `- Pronunciation:` 줄 (2026-08-17 필수화)

트래커 카드의 「발음」 블록이 이 줄을 쓴다. 없으면 그 블록이 통째로 안 나온다 —
2026-08-14 이전 항목들이 실제로 그렇다.

- **`Rhythm` 과 청크(`/`)·강세(볼드) 위치를 그대로 맞춘다.** 눈으로 따라 읽을 수 있어야 한다.
- 한글 발음 규칙은 `patrick-korean-pronunciation-guide-v3.4.md` 를 따른다
  (f·v·z·r·s·L·d·t 표시 유지, 장음 `-`, s클러스터에 `으` 금지, 모음 사이 T는 ㄹ 등).
  저장소 사본: [korean-phonetic-guide-v3.4.md](../korean-phonetic-guide-v3.4.md)
  (2026-09-05 v2→v3.4 갱신 — 서버 5개 파일도 같이 반영, 아래 「서버 동기화」 참조)
- 단어 하나여도 넣는다.

### `- Examples:` 줄 (2026-08-17 추가)

트래커 카드의 「이렇게도 말해요」가 이 줄을 쓴다. **같은 뜻을 다르게 말하는 표현 2개.**

- `영어 → 한국어` 를 `;` 로 구분한다.
- 문장이 아니라 짧은 덩어리여도 된다.
- Patrick이 실제로 쓸 상황(M Building·임차인·직원·회계)에 맞는 것으로 고른다.

### `- Rhythm:` 줄 (2026-08-10 추가)

Patrick은 쉐도잉을 문장 전체로 한다. 앱이 정답을 리듬 표기로 보여주는데 이 줄이 없으면
평문만 나와서 어디를 세게 읽을지 알 수 없다. **Original 이 문장이면 반드시 넣는다.**
단어 하나·짧은 덩어리(3단어 이하)면 생략해도 된다.

표기 규칙 — 문장마다 아래를 지킨다. **Original 이 두 문장이면 두 문장 다 표기한다.**

1. 피크 1개 — 그 문장에서 가장 세게 읽는 곳. **대문자와 볼드를 둘 다** 쓴다.
   `**HOME**`, 단어 일부면 `re**LAXED**`. 대문자만 쓰고 볼드를 빼면 안 된다.
2. 소문자 볼드 2~4개 — 일반 강세. 5개 이상 잡지 않는다.
3. `/` — 끊어 읽는 자리(의미 단위).
4. 억양 화살표 — 청크 끝마다 하나씩. 기준은 아래 「억양 화살표 v2」를 따른다.
   원본: [intonation-arrows.md](../intonation-arrows.md)

   | 기호 | 쓰는 자리 |
   |---|---|
   | `→` | 담담히 이어갈 때. **기본값** |
   | `↗` | 나열 첫 항목 · 선택의문 A · **`but` 등 반전 예고 앞** · 여운(`I'm hoping ↗`) · Yes/No 의문문 끝 · 되묻기 |
   | `↘` | 문장 끝 (평서문 · Wh-의문문 · 일반 지시) |
   | `↓` | 못 박는 결론·결정·강한 지시. **아껴 쓴다** |
   | `↘↗` | 문장 앞 도입부 끝(`Honestly,` `When I ~,`) · 말끝 흐리기(`I guess`) |

   - `↘`(또는 `↓`)는 **문장당 마지막 1개.** 중간 청크는 절대 바닥까지 내리지 않는다.
   - `and` 앞은 **나열인지 먼저 본다** — 목록으로 바꿔 말할 수 있으면 앞 항목이 `↗`.
     `I took some pictures ↗ / and posted them on MARketplace. ↘` (나열)
     `I was in a RUSH → / and left my phone at home. ↘` (원인·결과라 `→`)
   - `but`은 문장 안에서 이어지면 **거의 항상 `↗`** — 반전이 온다는 신호 자체가 표시다.
     `I usually get a little stressed every day, ↗ / but today wasn't too BAD. ↘`
     새 문장을 여는 `But`이면 해당 없음.

한 줄로 이어서 쓴다. 문장이 바뀌어도 줄을 바꾸지 않는다.
**Original 의 단어를 바꾸거나 빼지 않는다** — 표기만 입힌다. 단어가 달라지면 앱이
덜 덮인 것으로 보고 뒷부분을 평문으로 덧붙여 문장이 두 번 나온다.

예 (Original 이 두 문장):

```
- Original: When I listen to that music, I feel calm and relaxed. And it brings back memories of time with my friends.
- Rhythm: When I **lis**ten to that **mu**sic → / I feel **calm** and re**LAXED** ↘ / And it **brings** back **MEM**ories / of time with my **friends** ↘
```

예 (한 문장):

```
- Original: We'll need to get this document signed by Neil once the boss approves it.
- Rhythm: We'll **need** to get this **DOC**ument signed by **Neil** → / once the **boss** ap**proves** it ↘
```

왜 Korean 줄이 필요한가: Patrick의 영어 트래커 앱이 **한→영 인출 복습**을 한다.
한국어 뜻을 먼저 보여주고 입으로 영어를 만들어보게 하는 방식이라, 한국어가 없으면
그 카드는 상황 태그로 대체된다. 2026-08 초 한동안 이 줄이 빠져서 13건이 그렇게 됐다.

Original 이 Patrick의 한국어 입력에서 나온 게 아니라 이미 영어였다면, 그 영어의 뜻을
한국어로 적는다. 비워두지 않는다.

긴 형식(`Original wanted expression:` / `Korean meaning:` / `Study focus:`)도 계속 유효하다.
동기화 스크립트가 두 형식을 모두 읽는다.

## 서버 동기화 (2026-09-05)

**이 저장소 사본은 자동으로 서버에 반영되지 않는다** — 실제로 2026-09-04~05에 로컬만
v2→v2.2로 두 번 고치는 동안 서버(Hermes VPS)의 `patrick-english-coaching` 스킬은
계속 v1 화살표 규칙 그대로였다(`but` 반전 예고 없음). 발견한 즉시 수동으로 맞췄다:

- 서버 `references/quiet-wanted-phrase-capture.md`(억양 화살표 절)를 이 문서의 v2.2 내용으로 교체
- 발음 가이드도 v2/v3.3 → v3.4로 갱신 — `patrick-english-coaching`·`patrick-chief-of-staff`
  두 스킬의 참조 파일 6개, 새 가이드 파일 2곳에 배포
- 옛 버전은 `*.superseded-20260905` 로 이름만 바꿔 보존(삭제 안 함), 수정 전 6개 파일은
  `.claude-backup-20260905-*/`에 백업
- **컨테이너는 재시작하지 않았다** — 스킬 마크다운만 교체, 다음 실행부터 자동 반영

**교훈**: 이 봇 스펙 파일을 고칠 때마다 "서버에도 반영했는가"를 자문할 것. 로컬 저장소가
최신이라고 서버가 최신인 건 아니다.

## Pitfalls

- Do not convert staff-like sentences into staff messages unless Patrick explicitly asks to send or draft a message.
- Do not teach back the same content Patrick just provided; he asked for later reuse, not immediate coaching.
- If Patrick says or implies `막힌표현 그냥 넣은 것` / `막힌영어`, treat it as quiet capture only. Do not provide main point, revision, rhythm map, pronunciation, or explanation unless he clearly asks for that specific output.
- If Patrick says `저장 하지마`, `저장하지 마`, `save하지마`, `don't save this`, or points to a just-saved phrase and says not to save it, treat that as a deletion/correction request. Remove the matching wanted-phrase block from `/opt/data/english/wanted_phrases.md` if tools are available, then acknowledge briefly in Korean. If he gives a replacement version right before or after the deletion request, keep the replacement and remove only the rejected wording.
- If Patrick says `이걸로 저장`, `이 버전으로 저장`, `this version`, `이게 맞다`, `다시 수정해서 저장해라`, or gives a revised sentence after rejecting/correcting a similar one, treat the revised version as canonical. Remove older duplicate/similar blocks for that expression first, then append or keep only the revised version so reviews do not surface both forms.
- When Patrick corrects rhythm symbols, stress placement, Korean meaning, or Korean pronunciation for the same phrase, preserve his corrected version as given instead of re-normalizing it to the assistant's preferred rhythm/stress pattern. The goal is his tracker/shadowing card matching what Patrick confirmed.
- If Patrick points out missing symbols/강세 for a just-saved phrase, replace the existing block, don't append a duplicate. Include the corrected `- Rhythm:` and `- Pronunciation:` lines if he supplied them.
- **형식이 안 맞는다고 되묻지 말 것.** `무슨 뜻인가요?`, `영어로 뭐라고 하려던 건가요?` 같은 확인 질문은
  Patrick이 원치 않는다 — 그가 형식을 맞추게 만드는 것과 같다. 추론해서 채우고, 애매하면
  가장 그럴듯한 하나를 골라 저장한다. 틀렸으면 Patrick이 고쳐서 다시 준다.
- If Patrick asks `이거 맞아?`, `고쳐줘`, `발음`, `리듬맵`, or `설명해줘`, switch from quiet capture to active coaching.
