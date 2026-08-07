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
| 오늘 | **달력(최상단)** · 습관 5칸 · 명언 · 배울 표현 · 누적 · 설정 |
| 복습 | 오늘 복습 큐 · 단계별 현황 |
| 게임 | 5종 라운드 퀴즈 |
| 표현 | 전체 목록 + 검색 + 필터 6종 + 직접 추가 |

Patrick 요청으로 정해진 것들이라 임의로 되돌리지 말 것:

- **달력은 오늘 탭 맨 위에 있어야 한다.** 기록 전용 탭은 없앴고 누적·설정은 오늘 탭 하단으로 합쳤다.
- **습관 5개는 컴팩트한 아이콘 5칸**(`.r-item` / `.r-lb`)이다. 예전 세로 카드 목록은 자리를 너무 먹는다.
  체크할 때의 파편 효과·소리·진동은 성취감 장치라 유지한다.
- **망각 곡선 설명 표를 앱에 넣지 않는다.** 한 번 넣었다가 불필요하다고 뺐다. 규칙은 이 문서에만 둔다.

## 학습 흐름 — `studied` 플래그가 관문이다

봇이 배달한 표현은 **바로 복습 큐에 들어가지 않는다.** 「오늘」 탭에서 「학습 완료」를 눌러야
`studied: true`가 붙고 그때부터 복습 주기가 돈다. 안 본 표현이 복습을 막던 문제를 막기 위한 것이다.

- 레거시 판정: `studied === true || stage > 0` (필드 없는 옛 문서 호환)
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
뜻 → 예문(리듬) → 이럴 때 → 덩어리로 외우기 → 진도 → 액션
```

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
## TTS

Web Speech API(브라우저·OS 내장). 표현·예문·덩어리에 🔊. Patrick 기기는 맥북·아이폰·아이패드 전부 Apple.

**음성 이름은 OS 언어로 번역돼 온다.** Patrick 기기는 한국어라 `"Ava(프리미엄)"`, `"Zoe(고급)"` 형태다.
영어 `premium`·`enhanced`만 찾으면 프리미엄 음성을 못 알아본다 — 실제로 그 버그가 있었다.
`PREMIUM_RE`·`ENHANCED_RE`·`GOOD_VOICE_RE`에 한글 표기를 함께 넣어뒀으니 지우지 말 것.

**음성 선택 규칙 (중요).** `voiceScore()`가 Premium > Enhanced > Natural > Google > 기타 순으로 점수를 매긴다.
`Samantha`·`Alex`를 우선하도록 짰던 초기 버전이 기계음의 원인이었다 — **이 둘은 구형 compact 음성이다.
다시 이름으로 하드코딩하지 말 것.** `NOVELTY_VOICE`로 Zarvox·Bahh·Grandma 같은 장난 음성은 목록에서 제외한다.

`enVoices()`는 한 번 더 걸러 **프리미엄/고급/Natural · Google 계열 · 미국 영어만** 남긴다.
Daniel(영국)·Karen(호주)·Moira(아일랜드)·Rishi(인도)·Tessa(남아공)는 전부 구형 compact라
목록에 두면 고를 이유 없는 기계음만 늘어난다 (Patrick 지적). 저장된 음성이 목록에서 빠지면
`pickVoice()`가 최고 점수 음성으로 자동 복구한다.

설정에 음성 선택기(`#voiceSel`)와 현재 음성 품질 표시(`#voiceCur`)가 있다.
선택은 `localStorage.et_voice`(voiceURI)에 저장된다.
기기마다 설치된 음성이 다르므로 이름이 아니라 voiceURI로 저장한다.

**iOS는 프리미엄 음성을 웹에 주지 않는다 (확인된 사실, 2026-08-07).**
아이폰에서 Ava(프리미엄)를 다운로드해도 `speechSynthesis.getVoices()`에 나타나지 않는다 —
Safari는 기본 품질 음성만 웹에 노출하고, 받은 프리미엄 음성은 VoiceOver·화면 읽어주기 전용이다.
그래서 `#voiceNote`는 `isIOS()`로 분기해 아이폰에는 "받아도 소용없다"고 알린다.
**이 분기를 지우고 Mac 안내를 아이폰에도 띄우지 말 것** — Patrick이 실제로 받았다가 헛수고했다.

Mac은 정상이다. 2026-08-07 집 맥북에 Ava(프리미엄) 설치 → 감지·자동 선택 확인함.

아이폰에서도 좋은 음성을 쓰려면 **미리 만든 오디오 파일을 재생하는 수밖에 없다** (아래 Supertonic 항목).

**Supertonic 3는 검토 후 보류.** (`02_projects/video-automation/supertonic/`)
모델 합계 398MB라 브라우저 실행 불가 — `vector_estimator.onnx` 하나가 256MB로 GitHub 파일당 100MB 제한을 넘어
Pages에 올릴 수조차 없다. 게다가 이 앱은 영어만 읽는데 Supertonic의 강점은 한국어다.
굳이 한다면 VPS에서 미리 mp3를 만들어 저장소에 커밋하는 방식뿐이다.

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

## 날짜 계산은 UTC로 한다 (중요)

`new Date(iso + "T00:00:00")` + `toISOString()` 조합은 마닐라(UTC+8)에서 **하루씩 밀린다.**
예전 `addDays()`가 이 버그를 갖고 있어 복습 예정일과 스트릭이 하루 어긋나 있었다.
`isoToUTC()`를 거쳐 `setUTCDate()`로만 계산할 것.

## 남은 과제 — 봇 쪽

「막힌 표현」 13건에 **한국어 원문이 없다**(`meaning`이 빈 문자열). 그래서 한→영 복습에서
상황 태그로 대체하고 있다. `wanted_phrases.md`에 Patrick이 입력한 한국어가 남아 있다면
`hermes-sync.py`가 `ko` 필드로 실어 보내야 한다. 앱은 `e.ko`를 이미 우선 프롬프트로 쓴다.

주의: 동기화는 doc id로 멱등이라 **기존 문서는 갱신되지 않는다.** 백필하려면 별도 업데이트 경로가 필요하다.

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

**캐시 주의:** Pages가 `cache-control: max-age=600`을 보낸다. 배포 직후 브라우저에 옛 버전이 최대 10분간 남는다. 확인할 때는 `?cb=$RANDOM`을 붙여 curl하거나 브라우저에서 ⌘⇧R로 강제 새로고침한다. 캐시된 화면을 보고 "배포 실패"로 오판하지 말 것.

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
