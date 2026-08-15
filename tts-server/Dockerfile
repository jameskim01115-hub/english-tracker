FROM python:3.12-slim
# edge-tts 는 버전을 낮게 고정하지 말 것. 요청에 실리는 `Sec-MS-GEC-Version`(Edge 버전 문자열)이
# 낡으면 Microsoft 가 **403 으로 거부**한다 — 7.0.2 로 박았다가 전 음성이 죽었다(2026-08-15).
# 하한만 두고 최신을 받는다. 나중에 갑자기 403 이 나면 먼저 이걸 올려볼 것.
RUN pip install --no-cache-dir onnxruntime==1.23.1 numpy soundfile "edge-tts>=7.2.8"
WORKDIR /app
COPY helper.py server.py /app/
ENV TTS_ASSETS=/assets TTS_CACHE=/cache TTS_PORT=8080
EXPOSE 8080
CMD ["python", "-u", "server.py"]
