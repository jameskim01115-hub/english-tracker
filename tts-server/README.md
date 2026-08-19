# TTS 릴레이 (Supertonic 3 + Microsoft Neural)

앱의 🔊가 쓰는 음성 서버. Hostinger VPS(`ssh hermes`)에서 Docker로 돈다.

## 엔진 2개 — 음성 이름으로 갈린다

| 음성 이름 | 엔진 | 쓰는 곳 |
|---|---|---|
| `F1`~`F5`, `M1`~`M5` | Supertonic 3 (로컬 ONNX) | 기존 카드 재생·프리워밍 캐시 |
| `Emma` `Ava` `AvaM` `Jenny` `Andrew` `AndrewM` `Brian` `BrianM` | Microsoft Neural | 「발음」 탭 |

Microsoft Neural 은 **전송 경로가 둘이고 소리는 완전히 같다.**

- `AZURE_SPEECH_KEY` **없음** → `edge-tts` (현재 상태). 키·카드 불필요. 비공식 경로.
  **커스텀 SSML 불가** — Microsoft 가 Edge 가 만들지 않는 SSML 을 차단한다. rate 만 조절된다.
- `AZURE_SPEECH_KEY` **있음** → Azure REST 공식. `ssml=1` 로 강세·끊어읽기 재현이 켜진다
  (`build_ssml()`). 월 45만 자에서 자동 차단(F0 무료 한도 50만 대비 여유).

승격하려면 키만 넣으면 된다 — 음성 이름이 같아서 **소리 변화 없이** 넘어간다.

```bash
ssh hermes "cd /root/tts/app && printf 'AZURE_SPEECH_KEY=...\nAZURE_SPEECH_REGION=southeastasia\n' >> .env && docker compose up -d"
```

### ⚠️ edge-tts 버전을 낮게 고정하지 말 것

요청에 실리는 `Sec-MS-GEC-Version`(Edge 버전 문자열)이 낡으면 Microsoft 가 **403** 을 준다.
2026-08-15 에 `edge-tts==7.0.2` 로 박았다가 Neural 음성 8개가 전부 죽었다 —
Supertonic 은 멀쩡해서 부분 장애로 보였다. `>=7.2.8` 로 하한만 두고 최신을 받는다.
**갑자기 403 이 나면 시계·IP 를 의심하기 전에 이 버전부터 올려볼 것** (그때 시계는 1초 오차였다).

### Patrick 이 고른 음성 (2026-08-15 블라인드 청취)

24개 음성을 가려놓고 채점한 결과 **Emma 가 유일한 ★5**. Kokoro af_aoede ★4, Supertonic F4 ★4.
자료: `03_output/tts-비교-20260814/`. **들어보지 않은 음성을 목록에 추가하지 말 것.**

## 왜 있나

iOS Safari는 **다운로드한 Apple 프리미엄 음성을 웹페이지에 제공하지 않는다.** 아이폰·아이패드에서는
Samantha 같은 구형 compact 음성밖에 못 써서 기계음이 났다. 서버가 mp3를 만들어 내려주면
맥·아이폰·아이패드에서 같은 품질이 나온다.

맥에서는 Ava(프리미엄)를 쓸 수 있지만, 기기마다 소리가 달라지는 것보다 하나로 통일하는 편이 낫다.
앱 기본값이 서버 음성이고, 설정에서 기기 음성으로 바꿀 수 있다.

## 주소

```
https://tts.srv1722311.hstgr.cloud/tts?t=<텍스트>&v=<F1..M5>&s=<속도>
https://tts.srv1722311.hstgr.cloud/health
```

Traefik + Let's Encrypt가 인증서를 자동 발급한다. `*.srv1722311.hstgr.cloud`는 Hostinger가
와일드카드로 주는 도메인이라 따로 살 필요가 없다.

## 앱과 반드시 맞춰야 하는 값

`index.html`의 `TTS_SPEED`, 기본 음성(`DEFAULT_SRV_VOICE`)과
`hermes-sync.py`의 `TTS_VOICES`/`TTS_SPEED`가 **같아야 한다.** 다르면 캐시 키가 어긋나
미리 만들어둔 음성을 못 쓰고 매번 새로 생성한다.

현재: 기본 음성 `F2`, 미리 생성 `F2`+`M1`, 속도 **`0.9`**.
속도는 1.05(Supertonic 기본) → 1.0 → 0.9로 두 번 내렸다. Patrick이 1.0도 빠르다고 함.
같은 문장 기준 3.50s(1.0) → 3.89s(0.9).

## 캐시

`/root/tts/cache/<sha1(voice|speed|text)>.mp3`. 표현 하나당 평생 한 번만 생성된다.
83문장 x 2음성 기준 약 6MB. 생성 ~1초, 캐시 히트 ~0.2초, mp3 한 건 15~50KB.

`hermes-sync.py`가 새 표현을 만들 때마다 미리 생성해두므로, 앱에서 처음 눌러도 기다리지 않는다.

## 배포

```bash
scp server.py Dockerfile docker-compose.yml helper.py hermes:/root/tts/app/
ssh hermes "cd /root/tts/app && docker compose up -d --build"
```

`helper.py`는 Supertonic 저장소(`02_projects/video-automation/supertonic/py/helper.py`)의 사본이다.
그쪽이 업데이트되면 여기도 갱신할 것.

## 모델

`/root/tts/assets/` (383MB). Hugging Face `Supertone/supertonic-3`에서 받는다.

**`-3`이 붙은 저장소여야 한다.** `Supertone/supertonic`은 구버전이고 한국어를 지원하지 않는다
(상세: `.claude/rules/gotchas.md`). 재설치할 일이 있으면:

```bash
ssh hermes 'B=https://huggingface.co/Supertone/supertonic-3/resolve/main
mkdir -p /root/tts/assets/onnx /root/tts/assets/voice_styles
for f in duration_predictor.onnx text_encoder.onnx tts.json unicode_indexer.json \
         vector_estimator.onnx vocoder.onnx; do
  curl -sL -o /root/tts/assets/onnx/$f "$B/onnx/$f"; done
for v in F1 F2 F3 F4 F5 M1 M2 M3 M4 M5; do
  curl -sL -o /root/tts/assets/voice_styles/$v.json "$B/voice_styles/$v.json"; done'
```

## 프리워밍

Firestore의 표현·예문 음성을 한꺼번에 만들어 둔다. 컨테이너 안에서 돌려야 한다 —
호스트에서 `127.0.0.1:8080`은 열려 있지만, 레이트 리밋 면제는 내부 IP 기준이라 둘 다 무방하다.

```bash
ssh hermes "docker cp /root/tts/prewarm.py english-tts:/tmp/ && \
            docker exec english-tts python /tmp/prewarm.py F2,M1 0.9"
```

속도나 기본 음성을 바꾸면 캐시가 전부 무효가 되므로 다시 돌릴 것.

## 보안

- 공개 엔드포인트다. 인증은 없다 — 앱 소스가 public이라 키를 넣어도 그대로 노출된다.
- CORS는 앱 출처만 허용한다(브라우저 오용 차단). curl은 못 막는다.
- 레이트 리밋: 외부 IP당 시간당 80건 **생성**. 캐시 히트는 무제한(CPU를 안 씀).
  VPS 내부(프리워밍·크론)는 면제.
- 입력 400자 제한.
- 최악의 경우 피해는 CPU 낭비뿐이다. 과금되는 외부 API를 쓰지 않는 이유이기도 하다.

## Kokoro-82M (2026-08-19 추가) — 남성 음성 전담

`Puck`(am_puck) · `Echo`(am_echo). **Patrick 블라인드 청취 3라운드로 고른 것만** 넣는다.

- **torch 가 아니라 `kokoro-onnx`** 를 쓴다 — Supertonic 이 이미 쓰는 onnxruntime 을 공유해 이미지가 안 커진다.
- 모델 파일은 이미지에 넣지 않고 호스트에서 마운트한다: `/root/tts/kokoro` → `/kokoro` (353MB)
  ```
  kokoro-v1.0.onnx   325MB
  voices-v1.0.bin     28MB
  ```
  받는 곳: `github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/`
- **espeak-ng 가 필수다.** 없으면 남성 음성만 통째로 죽는다(Dockerfile 에 있음).
- **지연 로딩**이라 모델이 없어도 서버는 뜨고 Emma·Supertonic 은 정상 동작한다.
  첫 요청이 모델 로딩을 포함해 ~2.8초, 이후 캐시 미스가 ~1.7초.
- ONNX 세션 하나를 공유하므로 `_kokoro_lock` 으로 직렬화한다.

확인:
```bash
curl -s https://tts.srv1722311.hstgr.cloud/health | python3 -m json.tool   # kokoro.models 가 true 여야 한다
curl -s -o /tmp/t.mp3 -w "%{http_code} %{size_download}\n" "https://tts.srv1722311.hstgr.cloud/tts?t=hello&v=Puck&s=0.9"
```
