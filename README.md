---
project: English Tracker (웹)
status: 진행중
priority: 3
owner: Patrick
started: 2026-08-07
tech: [HTML, CSS, JavaScript, Firebase]
servers: [GitHub Pages]
---

# English Tracker

Patrick 개인 영어 학습 습관 추적기. 6개 일일 루틴 체크, 스트릭, 간격 반복 복습(1·3·7·14·30·60일), 표현 은행.

## 구성

| 파일 | 용도 |
|---|---|
| `index.html` | 앱 전체 (단일 파일) |
| `firestore.rules` | Firestore 보안 규칙 — 콘솔에 붙여넣어 적용 |
| `migrate.mjs` | 구 프로젝트 → 신규 프로젝트 데이터 이전 스크립트 |
| `backup/` | 이전 전 Firestore 원본 백업 47건 (git 제외) |

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

## Hermes 봇 연동 (확인 필요)

표현 46건이 전부 Hermes 봇을 통해 들어왔다(`source: hermes-delivered` 33건, `hermes-wanted` 13건). 즉 봇이 Firestore에 직접 쓰고 있다.

**신규 프로젝트로 옮기면 봇 쪽 설정도 같이 바꿔야 한다.** 봇이 계속 구 프로젝트에 쓰면 이 앱에는 새 표현이 안 올라온다. 봇의 Firestore 연동 코드는 이 워크스페이스에 없어 위치를 확인하지 못했다.

봇 인증 방식에 따라 대응이 갈린다.

| 봇 연동 방식 | 필요한 조치 |
|---|---|
| Firebase Admin SDK (서비스 계정) | 규칙을 우회하므로 프로젝트 설정만 교체하면 됨 |
| REST + apiKey | 익명 로그인을 추가해야 함. 아니면 규칙에서 거부됨 |

## 신규 프로젝트 설정 절차

1. Firebase 콘솔에서 새 프로젝트 생성 (M Building 프로젝트와 별개)
2. Firestore Database 생성 — **프로덕션 모드**로 시작
3. Authentication → **익명** 사용 설정 (이메일/비밀번호는 필요 없음)
4. 프로젝트 설정 → 웹 앱 등록 → SDK 구성값을 `index.html`의 `FIREBASE_CONFIG`에 입력
5. `node migrate.mjs ./backup` 실행
6. `firestore.rules` 내용을 콘솔 Rules 탭에 붙여넣고 게시
7. Hermes 봇의 Firestore 설정을 신규 프로젝트로 교체

## 배포

GitHub Pages (`main` 브랜치 루트) → https://jameskim01115-hub.github.io/english-tracker/

M Building 대시보드는 Vercel을 쓰지만 이 앱은 Pages에 있다. 두 배포는 서로 무관하며, 이 앱 작업이 M Building 대시보드에 영향을 주지 않는다.
