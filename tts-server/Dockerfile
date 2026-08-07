FROM python:3.12-slim
RUN pip install --no-cache-dir onnxruntime==1.23.1 numpy soundfile
WORKDIR /app
COPY helper.py server.py /app/
ENV TTS_ASSETS=/assets TTS_CACHE=/cache TTS_PORT=8080
EXPOSE 8080
CMD ["python", "-u", "server.py"]
