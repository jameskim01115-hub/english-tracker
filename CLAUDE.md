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
