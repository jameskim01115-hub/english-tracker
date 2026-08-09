# English Tracker — 작업 규칙

> Patrick 개인 영어 학습 추적기. 이 폴더에서 작업할 때 아래를 지킨다.

## 구조 한눈에

```
Hermes 크론잡 (VPS)
  └─ wanted_phrases.md / b2_vocab_log.md 에 append
       └─ hermes-sync.py (VPS 크론, 매시 :20)
            └─ Firestore: english-tracker-cea9f
                 └─ index.html (GitHub Pages)
```

앱은 단일 파일 `index.html`이다. 빌드 과정이 없다.

## 화면 구조 — 하단 탭 4개

| 탭 | 내용 |
|---|---|
| 오늘 | **달력(이번 주, 접힘)** · 습관 5칸 · 배울 표현(5개) · 설정 |
| 복습 | 오늘 복습 큐 |
| 게임 | 5종 라운드 퀴즈 |
| 표현 | 전체 목록 + 검색 + 필터 + 직접 추가 + 회화 노트 가져오기 + **누적 · 단계별 현황** |

Patrick 요청으로 정해진 것들이라 임의로 되돌리지 말 것:

- **달력은 오늘 탭 맨 위에 있어야 한다.** 기록 전용 탭은 없앴고 누적·설정은 오늘 탭 하단으로 합쳤다.
- **습관 5개는 컴팩트한 아이콘 5칸**(`.r-item` / `.r-lb`)이다. 예전 세로 카드 목록은 자리를 너무 먹는다.
  체크할 때의 파편 효과·진동은 성취감 장치라 유지한다 (효과음은 Patrick 요청으로 제거됨).
- **망각 곡선 설명 표를 앱에 넣지 않는다.** 한 번 넣었다가 불필요하다고 뺐다. 규칙은 이 문서에만 둔다.
- **달력은 기본이 이번 주 한 줄**(`calExpanded = false`). 탭하면 그 달 전체가 펼쳐진다.
  전체 달력이 첫 화면을 다 먹으면 정작 할 일이 안 보인다 (접힘 197px / 펼침 352px).
- **동기부여 한 줄(명언)을 다시 넣지 말 것.** 넣었다가 첫 화면이 길다고 제거했다. `QUOTES` 배열도 지웠다.
- **「배울 표현」 기본 노출은 5개**(`newShown = 5`). 15개를 다 펼쳐놓으면 부담만 되고
  아래의 누적·설정에 도달하기 어렵다. 「더 보기」로 10개씩 늘린다.
- 접힌 카드의 긴 문장은 4줄까지만 보인다(`-webkit-line-clamp`). 49단어짜리 문장 하나가
  카드로 화면을 다 먹던 것을 막는 것. 카드를 열면 전체가 보인다.
- 이 조정으로 오늘 탭 높이가 2,539px → 1,526px 로 줄었다. **다시 늘리지 말 것.**

## 학습 흐름 — `studied` 플래그가 관문이다

봇이 배달한 표현은 **바로 복습 큐에 들어가지 않는다.** 「오늘」 탭에서 「학습 완료」를 눌러야
`studied: true`가 붙고 그때부터 복습 주기가 돈다. 안 본 표현이 복습을 막던 문제를 막기 위한 것이다.

- 레거시 판정: `studied === true || stage > 0` (필드 없는 옛 문서 호환)
- **「학습 완료」는 「오늘」 탭과 「표현」 탭 양쪽에 있다.** 목록을 보다가 바로 복습에 넣을 수 있어야
  오늘 탭으로 되돌아갈 이유가 없다. 소스(봇 배달·막힌 표현·회화 교정)와 무관하게
  **미학습이면 「학습 완료」**, 졸업이면 「복습 큐에 다시 넣기」가 나온다.
  「삭제」는 그 아래 작은 보조 링크다 — 주 동작이 아니다.
- 「지난 것 넘기기」 버튼 = 오늘 이전 미학습 표현 일괄 처리 (`db.batch()`).
  **전부 내일로 몰지 말 것** — `BACKLOG_SPREAD`(5일)에 나눠 배치한다. 31개를 한 번에 내일로 보내면
  다음 날 복습이 31개가 된다. 확인 문구에 "카드를 하나씩 보지 않고 바로 태우는 방식"임을 명시해 둔다 —
  정상 흐름은 카드별 「학습 완료」이고 이 버튼은 밀린 것 처리용이다.

## 복습 규칙

`INTERVALS = [1, 3, 7, 14, 30, 60]`. stage = 성공한 복습 횟수. stage N 달성 → `INTERVALS[N]`일 뒤 재등장.
stage 6 = 졸업(`nextReview = "9999-12-31"`).

| 버튼 | 동작 |
|---|---|
| 알아 | stage +1 |
| 애매 | stage 유지 · 내일 |
| 몰라 | **stage 0으로 완전 리셋** · 내일 |

기본 방향은 **한→영(인출)**. `revDir` 상태, `localStorage.et_dir`에 저장.
**한→영은 복습 탭에만 적용한다** — 「오늘」 탭의 처음 보는 표현은 영→한으로 익히고 넘어온다 (Patrick 확인함).
복습 큐가 비면 「그래도 연습하기」 버튼이 나온다 (`renderPractice`, mode `practice`) —
카드만 넘겨보는 모드라 단계·복습일을 건드리지 않는다.
한글 뜻이 없는 「막힌 표현」은 상황 태그(`p.tags`)를 프롬프트로 쓴다.

## 카드 규격 — 순서를 바꾸지 말 것

뒷면 블록은 **항상 같은 순서**다. 데이터가 없는 블록만 빠지고 순서·라벨은 고정한다.
「기준이 애매하다」는 피드백에서 나온 규칙이라 임의로 늘리거나 섞지 말 것.

```
일반          뜻 → 예문(리듬) → 이럴 때 → 덩어리로 외우기 → 진도 → 액션
회화 교정      질문 → 뜻 → 내가 썼던 것 → 덩어리 → 왜 틀렸나(접힘) → 진도 → 액션
```

회화 교정은 정답을 앞면(한→영) 또는 정답 블록에 Rhythm Map 표기로 한 번만 보여준다.
예문 블록을 따로 두지 않는다 — 같은 문장이 두 번 나오면 중복이다. 상세는 아래 「회화 복습 노트」 절.

- `context` 필드는 소스마다 의미가 다르다. `parseContext()`가 갈라준다.
  - `hermes-delivered` → 예문 (리듬 마크업 포함 가능)
  - `hermes-wanted` → `"<상황 태그>; reusable chunks: a, b, c."`
- **리듬 마크업**: `**강세**`, `→ ↘ ↓ ↗` 억양, `" / "` 끊어 읽기. `rhythmHtml()`이 렌더한다.
  이전엔 `**`가 그대로 노출됐다.
- **핵심 표현 밑줄**: 5단어 이상 문장에서 chunks 중 **하나만** 밑줄(`keyRange()`).
  여러 개 치면 문장 전체가 덮여 의미가 없다. 봇 chunks는 문장 순서대로라 **먼저 나온 것**을 고른다.
  문장 단어 수 − 2 를 넘는 청크는 제외.
- **힌트**: 첫 글자 골격(`L__ m_ …`) 방식은 Patrick이 거부했다. 실제 영어 조각을 단계로 준다 —
  ① 핵심 표현(=밑줄과 동일) ② 문장 앞 절반. 4단어 이하는 1단계뿐.
- **「내 문장」 입력을 다시 넣지 말 것.** 한 번 넣었다가 Patrick이 부담된다고 해서 뺐다 (표현마다 작문은 시간이 너무 걸린다).
## TTS — 서버 음성이 기본이다

**기본은 VPS의 Supertonic 3 릴레이**다. 상세: `tts-server/README.md`.
이유: iOS Safari가 다운로드한 Apple 프리미엄 음성을 웹에 노출하지 않아 아이폰에서 기계음밖에
못 쓰던 문제를 해결하려는 것. 기기와 무관하게 같은 품질이 나온다.

```
https://tts.srv1722311.hstgr.cloud/tts?t=<텍스트>&v=F2&s=0.9
```

- `TTS_SPEED = 0.9`, 기본 음성 `srv:F2`. **`hermes-sync.py`의 `TTS_VOICES`·`TTS_SPEED`와 값이 같아야 한다** —
  다르면 캐시 키가 어긋나 미리 만든 음성을 못 쓰고 매번 새로 생성한다.
- Patrick이 고른 목소리는 **F2(여성)·M1(남성)** 둘. 미리 생성도 두 개 다 돌린다 —
  앱에서 바꿔도 기다림이 없게 하려는 것. 목소리를 바꾸려면 `DEFAULT_SRV_VOICE`와
  `hermes-sync.py`의 `TTS_VOICES`를 같이 고치고 프리워밍을 다시 돌릴 것.
- 서버가 죽거나 오프라인이면 `speakServer()`가 `speakDevice()`로 자동 폴백한다. 소리는 항상 난다.
- 설정 선택값(`localStorage.et_voice`)은 `srv:F2` 형태(서버) 또는 voiceURI(기기) 둘 중 하나다.

**기기 음성 폴백 쪽 규칙** (설정에서 직접 고를 때만 쓰임)

- 음성 이름은 OS 언어로 번역돼 온다. 한국어 맥은 `"Ava(프리미엄)"`. 영어 `premium`만 찾으면 못 알아본다 —
  `PREMIUM_RE`·`ENHANCED_RE`·`GOOD_VOICE_RE`에 한글 표기를 넣어뒀으니 지우지 말 것.
- `Samantha`·`Alex`를 우선하도록 짰던 초기 버전이 기계음의 원인이었다. **이름으로 하드코딩하지 말 것.**
- `enVoices()`가 프리미엄/고급/Natural · Google · 미국 영어만 남긴다.
  Daniel(영국)·Karen(호주)·Moira(아일랜드)·Rishi(인도)·Tessa(남아공)는 구형 compact라 뺐다.
- **iOS에는 프리미엄 음성 다운로드를 권하지 말 것.** 받아도 웹에 안 나온다 (Patrick이 실제로 받았다가 헛수고했다).
  길게 설명하던 iOS 안내문은 Patrick 요청으로 제거했다 — 서버 음성이 기본이라 불필요한 노이즈였다.
  지금은 기기 음성에 좋은 게 없을 때만 "서버 음성을 고르면 자연스러워집니다" 한 줄만 띄운다.

**효과음·말하기 속도 설정을 다시 넣지 말 것.** Patrick이 불필요하다고 해서 뺐다.
습관 체크의 파편 효과와 진동은 성취감 장치라 유지한다.

## 회화 복습 노트 가져오기 (ChatGPT Live)

Patrick은 매일 ChatGPT Live로 회화 연습을 하고, 끝나면 복습 노트를 만든다.
**교정된 문장은 본인이 실제로 틀린 것이라 봇이 배달하는 일반 표현보다 학습 가치가 높다.**

표현 탭 → 「💬 회화 복습 노트 가져오기」 → 통째로 붙여넣기 → 미리보기 → 선택 저장.

**텔레그램 봇을 거치지 않는다.** 노트가 4,000자를 넘어 텔레그램 4,096자 한도에 걸리고,
동기화가 매시라 최대 1시간 지연되며, 형식이 고정돼 있어 AI 파싱이 필요 없다.

`parseReviewNote()`가 항목 머리글(`1.1`, `2.1` …)로 자르고 아래 라벨로 필드를 뽑는다.
**라벨 이름이 바뀌면 파싱이 깨진다** — 그래서 저장 전 미리보기를 반드시 거치게 해 뒀다.

```
오늘의 질문 / Patrick's Original Answer / 어색한 부분 / 틀린 문법
Natural Corrected Answer / Rhythm Map / Key Corrections
```

| 노트 | 필드 |
|---|---|
| 오늘의 질문 (영문/한글) | `question` / `questionKo` — **한→영 앞면 프롬프트** |
| Natural Corrected Answer | `expression`(영문) · `ko`(한글) |
| Patrick's Original Answer | `wrong` |
| 어색한 부분 + Key Corrections 해설 | `why` |
| Rhythm Map | `rhythm` |
| Key Corrections 의 `덩어리 = 뜻` 행 | `chunks` (`|` 구분) |

- **질문이 앞면이다.** 실제 대화처럼 질문을 보고 답을 만들어야 한다 (Patrick 요청).
- **정답은 Rhythm Map 표기로만 보여준다.** 평문을 따로 또 띄우면 중복이고 카드가 길어진다.
  쉐도잉에 쓰는 건 리듬 쪽이다. `answerHtml()` 참조.
- **기호 범례(`굵게 = 강세 · | = 끊어 읽기 …`)를 다시 넣지 말 것.** Patrick이 이미 알고 있어
  매 카드에 반복될 이유가 없다. 「밑줄이 핵심입니다」 안내도 같은 이유로 뺐다.
- ChatGPT 노트는 `**굵게**` 대신 **대문자로 강세**를 쓴다 (`HOME`, `reVIEW`). `capsToStress()`가
  변환한다. 봇 예문은 `**`와 대문자를 같이 쓰므로 `**`가 있으면 손대지 않는다 — 안 그러면 중첩으로 깨진다.
- 리듬 스타일(`b.st`·`i.ar`·`i.br`)은 **선택자를 좁히지 말 것.** 예문·정답·게임 피드백 어디서든 같게 보여야 한다.
- 가져와도 바로 복습 큐에 안 들어간다. 기존 `studied` 관문을 그대로 타서 「배울 표현」에 쌓인다 —
  하루 6개씩 자동 편입되면 복습이 감당 안 된다.
- 중복 문장은 미리보기에서 자동으로 체크 해제된다.
- 저장 직후 `prewarmTTS()`가 F2·M1 음성을 미리 받아둔다 (실패해도 무시).

## 게임 탭

`GAME_LEN = 10`문항. 표현마다 가능한 유형 중 하나를 뽑는다 (`buildRound`).

| 유형 | 조건 |
|---|---|
| `meaning` 뜻 고르기 · `expr` 영어 고르기 · `listen` 듣고 고르기 | `meaning` 필요 |
| `cloze` 빈칸 채우기 | 예문 안에 표현이 그대로 들어 있어야 함 |
| `order` 문장 조립 | 2~8단어. 긴 문장은 `keyRange()`로 뽑은 **핵심 표현만** 조립 |

`order`는 어순 훈련이라 `kinds`에 두 번 넣어 비중을 두 배로 둔다.
4지선다 오답 보기는 **길이가 비슷한 것**에서 뽑는다 — 길이만 봐도 답이 보이면 문제가 안 된다.

**출제 가중치** (`weightOf`): 미학습 ×2.5, 게임 오답 1회당 ×3, 낮은 단계일수록 높게, 졸업 ×0.2.

**SRS와의 경계 (중요).** 게임 정답은 복습 일정을 **앞당기지 않는다.** 게임으로 SRS를 우회하면
간격 반복이 무너진다. `right` 카운트만 올린다. 오답일 때만 `wrong` +1 하고,
이미 학습한 표현이면 `nextReview`를 내일로 당긴다. 미학습 표현의 일정은 건드리지 않는다.

기록은 게임이 끝날 때 `db.batch()`로 한 번에 쓴다. 최고 기록은 `localStorage.et_best`.

## 무엇을 불러올 것인가 (중요 — 2026-08-08)

예전엔 열 때마다 `limit(500)`으로 전부 읽었다. 하루 14건(봇 8.2 실측 + 회화 교정 6)씩 쌓이므로
**약 한 달이면 상한에 닿고, 그 순간부터 오래된 표현이 에러 없이 조용히 화면에서 사라진다.**
읽기 횟수도 같이 늘어(하루 10번 열면 5,000회) 무료 한도의 10%를 먹는다.

지금은 평소에 **「지금 필요한 것」만** 읽는다.

| 쿼리 | 범위 |
|---|---|
| `where("nextReview","<=", today+7).orderBy("nextReview").limit(400)` | 복습 대기·임박 + 미학습(동기화가 nextReview를 과거로 넣는다) |
| `orderBy("learnedDate","desc").limit(120)` | 최근 것 — 오늘 화면용 |

- **졸업(`nextReview = "9999-12-31"`)과 먼 미래 복습은 자동으로 빠진다.** 문자열 비교라 정확히 걸린다.
  삭제하지 않아도 앱이 느려지지 않는 이유다 — **졸업 표현을 지우자는 제안은 이래서 불필요하다.**
- 둘 다 **단일 필드 정렬**이라 복합 색인이 필요 없다. Firestore 콘솔 작업이 필요 없다는 뜻.
- 전체 목록은 **「표현」 탭을 열 때 세션당 한 번만** 읽는다 (`ensureAllLoaded`).
  **로딩으로 목록을 가리지 말 것.** 이미 들고 있는 것으로 먼저 보여주고 뒤에서 채운다 —
  헤더에 `· 동기화 중…`만 뜬다. 한 번 가렸다가 회선이 느릴 때 "불러오는 중"만 계속 돈다는
  지적을 받았다 (2026-08-09).
- **Firestore `get()` 에는 타임아웃이 없다.** 회선이 나쁘면 무한정 매달린다.
  `withTimeout()` 으로 직접 끊는다 — 초기 로드 20초, 전체 목록 15초.
  초기 로드가 8초를 넘기면 "연결이 느립니다" 안내로 바꾼다(`showSlow`).
- 로드에 실패했고 캐시도 없으면 **실패했다고 표시한다.** 그냥 `renderAll()` 하면
  "배울 표현을 전부 처리했습니다"가 떠서 다 끝난 것처럼 보인다.
- 그래서 **누적 통계와 단계별 현황은 「표현」 탭에 둔다.** 코어 로드만으론 수치가 틀리기 때문이다.
  전체 로드 전에는 누적이 `—`로 표시된다. 이 둘을 오늘·복습 탭으로 되돌리지 말 것.

용량은 애초에 문제가 아니었다 — 문서당 836바이트, 5년 26,000개라도 24MB(무료 1GB의 2.5%).
**병목은 저장이 아니라 읽기 횟수였다.**

## 로컬 캐시 — 인증을 기다리지 않는다

익명 로그인(~1s) + Firestore 왕복(~0.6s)이 모바일 회선에서 몇 초로 늘어나 "불러오는 중"만 보였다.
`bootFromCache()`가 `localStorage`(`et_cache_v1`)로 **7ms 만에 먼저 그리고**, 서버 데이터가 오면 갈아끼운다.

- 캐시 크기 17KB 수준. 저장 실패는 무시한다 — 없어도 앱은 동작한다.
- 동기화 중에는 헤더 날짜 뒤에 `· 동기화 중…`이 붙는다.
- **인증 전 쓰기는 `canWrite()`가 막는다.** 캐시 화면만 보고 누른 조작이 조용히 사라지면 안 된다.
  쓰기 진입점(루틴 체크·학습 완료·채점·일괄 처리·직접 추가)에 전부 걸려 있다.
- 상태가 바뀌면 `saveCache()`로 갱신한다.

## 날짜 계산은 UTC로 한다 (중요)

`new Date(iso + "T00:00:00")` + `toISOString()` 조합은 마닐라(UTC+8)에서 **하루씩 밀린다.**
예전 `addDays()`가 이 버그를 갖고 있어 복습 예정일과 스트릭이 하루 어긋나 있었다.
`isoToUTC()`를 거쳐 `setUTCDate()`로만 계산할 것.

## 한국어 원문 (`ko` 필드) — 해결됨 2026-08-08

한→영 복습은 `e.ko`를 프롬프트로 쓴다. 없으면 상황 태그로 대체한다.

- 봇 출력이 두 형식이다. 7월 긴 형식엔 `Korean meaning:`이 있었는데 8월 축약 형식에서 빠졌다.
  `hermes-sync.py`의 `parse_wanted()`가 **두 형식을 모두** 읽고 `ko`를 뽑는다 (19 → 33블록).
- 봇 캡처 스펙에 `- Korean:` 줄을 필수로 못박았다:
  `/docker/hermes-agent-7jge/data/skills/productivity/patrick-english-coaching/references/quiet-wanted-phrase-capture.md`
  (chief-of-staff 쪽 examples 파일 2개도 같이 수정, 전부 `.bak-*` 백업 있음)
- 기존 13건은 `ko`를 직접 채웠다 (updateMask로 `ko`만 PATCH — 학습 기록 보존 확인).

주의: 동기화는 doc id로 멱등이라 **기존 문서는 갱신되지 않는다.** 봇 형식이 또 바뀌어 기존 문서를
고쳐야 하면 별도 PATCH 경로가 필요하다.

## 절대 규칙

**M Building Firebase 프로젝트(`m-building-fbe46`)를 여기에 연결하지 않는다.** 2026-08-07에 두 앱이 프로젝트를 공유해 M Building 임차인 데이터가 공개 노출된 사고가 있었다. `index.html`과 `hermes-sync.py` 양쪽에 가드가 있으니 우회하지 말 것.

**이 프로젝트에 민감한 데이터를 넣지 않는다.** 화면 로그인이 없고 익명 인증만 걸려 있어, 앱 소스를 읽고 흉내내는 접근은 막지 못한다. 영어 학습 기록 수준만 담는다.

**로그인 화면을 추가하지 않는다.** Patrick이 개인 도구에 로그인 붙이는 것을 명시적으로 거절했다. 주소로 바로 들어가 쓰는 흐름을 유지한다.

## 배포 — 서브모듈이다

이 폴더는 별도 git 저장소(`jameskim01115-hub/english-tracker`)다. **부모 저장소에서 커밋해도 반영되지 않는다.**

```bash
cd 02_projects/english-tracker
git add -A && git commit -m "..." && git push origin main
```

push하면 GitHub Pages가 자동 빌드한다. 1~2분 걸린다.

**배포할 때마다 `index.html`의 `BUILD` 값을 바꿀 것.** 앱이 서버의 index.html을 캐시 없이 받아
자기 `BUILD`와 비교하고, 다르면 상단에 「새 버전이 있습니다」 배너를 띄운다 (탭하면 쿼리를 붙여 새로고침).
안 바꾸면 배너가 안 뜨고 Patrick이 옛 화면을 계속 보게 된다.

**캐시 주의:** Pages가 `cache-control: max-age=600`을 보내고 **iOS Safari는 그보다 더 오래 들고 있다.**
⌘⇧R이 없는 아이폰에서는 탭을 닫았다 열어도 안 바뀔 때가 있다 — 그때는 주소에 `?v=2` 같은 쿼리를 붙인다.
확인할 때는 `?cb=$RANDOM`을 붙여 curl한다. 캐시된 화면을 보고 "배포 실패"로 오판하지 말 것.
2026-08-08에 이 오판이 두 번 반복돼 BUILD 감지를 넣었다.

배포 확인:

```bash
curl -s "https://jameskim01115-hub.github.io/english-tracker/?cb=$RANDOM" | grep -c "찾는문자열"
```

## hermes-sync.py 는 VPS로 따로 배포해야 한다

git push만으로는 서버에 반영되지 않는다. 수정했으면 반드시:

```bash
scp hermes-sync.py hermes:/root/english-sync/sync_english_to_firestore.py
ssh hermes "/usr/bin/python3 /root/english-sync/sync_english_to_firestore.py"
```

- 서버: SSH alias `hermes` (Hostinger VPS)
- 크론: `20 * * * *` — 매시 20분
- 로그: `/root/english-sync/sync.log`
- Hermes 데이터: `/docker/hermes-agent-7jge/data/english/`

**동기화는 크론잡이 아니라 파일을 읽는다.** 영어 크론을 수정하거나 새로 만들어도 `wanted_phrases.md`·`b2_vocab_log.md`에 계속 append하기만 하면 자동 반영된다. 크론잡마다 Firestore 코드를 넣지 말 것.

## 로컬 테스트

Firestore 설정이 든 상태로 열면 실제 데이터에 붙는다. 읽기는 안전하지만 쓰기 동작(루틴 체크, 복습 처리)은 실제 기록을 바꾼다. UI만 확인할 때는 더미 설정으로 사본을 만들어 띄운다.

`.claude/launch.json`에 `english-tracker` 항목이 등록돼 있다 (포트 4173).

## Firestore

- 프로젝트: `english-tracker-cea9f`
- 컬렉션: `english_days`, `english_expressions` 두 개뿐. 규칙이 나머지를 전부 거부한다.
- 새 컬렉션을 쓰려면 `firestore.rules`에 추가하고 콘솔에서 게시해야 한다. **게시는 Patrick만 할 수 있다** (콘솔 접근 필요).
- 규칙 게시 시 콘솔 URL은 `/firestore/databases/-default-/security/rules`. `/rules`로 가면 개요로 튕긴다.
- 「게시」 버튼은 편집기 내용을 바꿔야 나타난다. 붙여넣기 전에는 없는 게 정상이다.

## 데이터 백업

`backup/`은 gitignore 대상이라 로컬에만 있다. 스키마를 바꾸거나 대량 수정하기 전에 갱신할 것.

```bash
NEW="AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
T=$(curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=$NEW" \
  -H "Content-Type: application/json" -d '{"returnSecureToken":true}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['idToken'])")
curl -s "https://firestore.googleapis.com/v1/projects/english-tracker-cea9f/databases/(default)/documents/english_expressions?pageSize=300" \
  -H "Authorization: Bearer $T" -o backup/export_english_expressions.json
```

## 봇 표기

텔레그램 핸들은 `@PatrickHermesAI_bot`이다. 앱 UI에는 봇 이름을 쓰지 않고 핸들만 표기한다 — `HERMES.md`는 어시스턴트 이름을 "낭만파"라고 하는데 Patrick은 그 이름을 쓰지 않는다고 했다. 확정 전까지 이름 표기를 넣지 말 것.
