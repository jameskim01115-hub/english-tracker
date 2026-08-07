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
| `backup/` | 이전 전 Firestore 원본 백업 (git 제외) |

## Firebase 프로젝트 (중요)

**이 앱은 M Building 대시보드와 Firebase 프로젝트를 절대 공유하지 않는다.**

2026-08-07 이전에는 M Building과 동일한 `m-building-fbe46` 프로젝트를 썼다. 이 저장소가 public이라 해당 프로젝트의 apiKey가 공개 노출됐고, 그 프로젝트의 Firestore는 인증 없이 읽기·쓰기가 모두 열려 있어 테넌트 전화번호·TIN·임대료까지 외부에서 접근 가능한 상태였다. 그래서 전용 프로젝트로 분리했다.

`index.html`에는 실수 재발을 막는 두 개의 가드가 있다.

- `FIREBASE_CONFIG.projectId`가 placeholder면 앱이 뜨지 않고 안내 문구만 표시한다.
- `projectId`가 `m-building-fbe46`이면 즉시 예외를 던지고 중단한다.

## 인증

Firebase Email/Password 인증. Patrick 계정 하나만 사용한다.

`firestore.rules`는 `request.auth != null`이 아니라 **특정 UID**로 접근을 좁힌다. apiKey는 공개 값이고 Email/Password 제공업체는 기본적으로 외부인의 회원가입을 허용하기 때문에, "로그인한 사람"으로 열어두면 누구나 계정을 만들어 들어올 수 있다.

세션은 `Persistence.LOCAL`이라 기기당 최초 1회만 로그인하면 된다.

## 신규 프로젝트 설정 절차

1. Firebase 콘솔에서 새 프로젝트 생성 (M Building 프로젝트와 별개)
2. Firestore Database 생성 — **프로덕션 모드**로 시작
3. Authentication → Email/Password 사용 설정 → Users에 Patrick 계정 추가
4. 프로젝트 설정 → 웹 앱 등록 → SDK 구성값을 `index.html`의 `FIREBASE_CONFIG`에 입력
5. `node migrate.mjs ./backup` 실행 → 출력된 UID 확인
6. `firestore.rules`의 `__PATRICK_UID__`를 5번 UID로 교체 → 콘솔 Rules 탭에 붙여넣고 게시

## 배포

GitHub Pages (`main` 브랜치 루트) → https://jameskim01115-hub.github.io/english-tracker/

M Building 대시보드는 Vercel을 쓰지만 이 앱은 Pages에 있다. 두 배포는 서로 무관하며, 이 앱 작업이 M Building 대시보드에 영향을 주지 않는다.
