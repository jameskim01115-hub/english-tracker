---
project: English Tracker (웹)
status: 진행중
priority: 3
owner: Patrick
started: 2026-08-07
tech: [HTML, CSS, JavaScript, Firebase, Supertonic 3, ONNX]
servers: [GitHub Pages, Hostinger-187.77.153.220]
---

# English Tracker

Patrick 개인 영어 학습 습관 추적기. 하단 탭 4개(오늘·복습·게임·표현).
달력 + 습관 5칸 체크 + 스트릭, 간격 반복 복습(1·3·7·14·30·60일), 표현 게임, 표현 라이브러리.

복습은 **한→영(인출) 기본**이다. 한글 뜻이나 상황을 먼저 보고 입으로 말해본 뒤 정답과 비교한다.
긴 문장은 핵심 표현 하나만 밑줄로 표시해 통문장 암기 부담을 없앴다.
게임 탭은 아직 안 외운 것과 전에 틀린 것을 우선 출제한다.
🔊 음성은 VPS의 Supertonic 3가 만든 mp3를 쓴다 — iOS Safari가 프리미엄 음성을 웹에 주지 않아
아이폰에서 기계음밖에 못 쓰던 문제를 우회한 것이다. 서버가 안 되면 기기 음성으로 폴백한다.
카드 뒷면 블록 순서와 학습 흐름은 `CLAUDE.md`에 규격으로 고정돼 있다.

## 구성

| 파일 | 용도 |
|---|---|
| `index.html` | 앱 전체 (단일 파일) |
| `firestore.rules` | Firestore 보안 규칙 — 콘솔에 붙여넣어 적용 |
| `migrate.mjs` | 구 프로젝트 → 신규 프로젝트 데이터 이전 스크립트 |
| `tts-server/` | Supertonic 3 음성 서버 (VPS 배포용 사본) — [README](tts-server/README.md) |
| `backup/` | Firestore 원본 백업 (git 제외) |

## Firebase 프로젝트 (중요)

**이 앱은 M Building 대시보드와 Firebase 프로젝트를 절대 공유하지 않는다.**

2026-08-07 이전에는 M Building과 동일한 `m-building-fbe46` 프로젝트를 썼다. 이 저장소가 public이라 해당 프로젝트의 apiKey가 공개 노출됐고, 그 프로젝트의 Firestore는 인증 없이 읽기·쓰기가 모두 열려 있어 M Building 운영 데이터까지 외부에서 접근 가능한 상태였다. 그래서 전용 프로젝트로 분리했다.

`index.html`에는 재발을 막는 가드가 두 개 있다.

- `FIREBASE_CONFIG.projectId`가 placeholder면 앱이 뜨지 않고 안내 문구만 표시한다.
- `projectId`가 `m-building-fbe46`이면 즉시 예외를 던지고 중단한다.

## 인증 — 화면에 로그인은 없다

Patrick 혼자 쓰는 개인 도구라 주소로 들어가면 바로 열린다. 대신 앱이 로드될 때 **익명 계정으로 조용히 로그인**하고, `firestore.rules`가 그 세션만 통과시킨다.

- **막는 것**: 유출된 apiKey를 긁어 인증 없이 Firestore를 훑고 지우는 자동 스캐너. 구 프로젝트에는 이 방어선이 없었다.
- **막지 못하는 것**: 앱 소스를 읽고 익명 로그인을 직접 흉내내는 사람. 영어 학습 기록이라 그 수준은 감수한다.
- **따라서**: 민감한 데이터를 이 프로젝트에 넣지 말 것.

## 봇 연동 — 동작 중

봇은 Firestore에 직접 쓰지 않는다. VPS 파일에 append하고 크론이 옮긴다.

```
Hermes 크론 → /docker/hermes-agent-7jge/data/english/{wanted_phrases,b2_vocab_log}.md
            → sync_english_to_firestore.py (매시 :20)
            → Firestore english-tracker-cea9f
```

로컬 사본은 `hermes-sync.py`. 수정하면 VPS로 따로 배포해야 한다 (`CLAUDE.md` 참조).
동기화는 doc id(sha1)로 멱등이라 앱에서 쌓은 학습 기록을 덮어쓰지 않는다.

## 분리 완료 (2026-08-07)

전용 프로젝트 **`english-tracker-cea9f`** 로 이전 완료. M Building 프로젝트와 아무것도 공유하지 않는다.

- Firestore 생성(프로덕션 모드) · 익명 인증 · 규칙 게시 완료
- 데이터 47건 이전, 인증 없는 외부 접근 차단 확인
- 라이브 HTML에서 구 M Building apiKey 0건 확인

M Building 규칙(`02_projects/m-building/firestore.rules`)에 english_* 임시 개방 두 줄이
남아 있으면 삭제할 것.

## 배포

GitHub Pages (`main` 브랜치 루트) → https://jameskim01115-hub.github.io/english-tracker/

M Building 대시보드는 Vercel을 쓰지만 이 앱은 Pages에 있다. 두 배포는 서로 무관하며, 이 앱 작업이 M Building 대시보드에 영향을 주지 않는다.
