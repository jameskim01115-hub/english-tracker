# TTS 릴레이 (Supertonic 3)

앱의 🔊가 쓰는 음성 서버. Hostinger VPS(`ssh hermes`)에서 Docker로 돈다.

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
`hermes-sync.py`의 `TTS_VOICE`/`TTS_SPEED`가 **같아야 한다.** 다르면 캐시 키가 어긋나
미리 만들어둔 음성을 못 쓰고 매번 새로 생성한다.

현재: 기본 음성 `F2`, 미리 생성 `F2`+`M1`, 속도 `1.0`. (Patrick이 고른 두 목소리)

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
            docker exec english-tts python /tmp/prewarm.py F2,M1 1.0"
```

속도나 기본 음성을 바꾸면 캐시가 전부 무효가 되므로 다시 돌릴 것.

## 보안

- 공개 엔드포인트다. 인증은 없다 — 앱 소스가 public이라 키를 넣어도 그대로 노출된다.
- CORS는 앱 출처만 허용한다(브라우저 오용 차단). curl은 못 막는다.
- 레이트 리밋: 외부 IP당 시간당 80건 **생성**. 캐시 히트는 무제한(CPU를 안 씀).
  VPS 내부(프리워밍·크론)는 면제.
- 입력 400자 제한.
- 최악의 경우 피해는 CPU 낭비뿐이다. 과금되는 외부 API를 쓰지 않는 이유이기도 하다.
