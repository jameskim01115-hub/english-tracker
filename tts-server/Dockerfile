FROM python:3.12-slim
# edge-tts 는 버전을 낮게 고정하지 말 것. 요청에 실리는 `Sec-MS-GEC-Version`(Edge 버전 문자열)이
# 낡으면 Microsoft 가 **403 으로 거부**한다 — 7.0.2 로 박았다가 전 음성이 죽었다(2026-08-15).
# 하한만 두고 최신을 받는다. 나중에 갑자기 403 이 나면 먼저 이걸 올려볼 것.
# Kokoro 는 espeak-ng 로 발음기호를 만든다. 없으면 남성 음성이 통째로 죽는다.
RUN apt-get update -qq && apt-get install -y --no-install-recommends espeak-ng \
    && rm -rf /var/lib/apt/lists/*
# kokoro-onnx 는 torch 가 아니라 **onnxruntime** 을 쓴다 — Supertonic 과 런타임을 공유해
# 이미지가 커지지 않는다. 모델 파일(353MB)은 이미지에 넣지 않고 호스트에서 마운트한다.
RUN pip install --no-cache-dir onnxruntime==1.23.1 numpy soundfile "edge-tts>=7.2.8" kokoro-onnx
WORKDIR /app
COPY server.py /app/
ENV TTS_CACHE=/cache TTS_PORT=8080 KOKORO_DIR=/kokoro
EXPOSE 8080
CMD ["python", "-u", "server.py"]
