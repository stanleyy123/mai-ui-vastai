FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-devel

WORKDIR /app

RUN git clone https://github.com/Tongyi-MAI/MAI-UI.git /app/MAI-UI

RUN pip install --no-cache-dir -r /app/MAI-UI/requirements.txt && \
    pip install --no-cache-dir \
        "vllm==0.11.0" \
        "fastapi>=0.111" \
        "uvicorn[standard]>=0.30" \
        "httpx>=0.27" \
        "python-dotenv>=1.0" \
        "vastai-sdk>=0.3.0" && \
    pip install --no-cache-dir "transformers>=4.49.0" --upgrade

COPY server.py zoom_inference.py worker.py start.sh ./
RUN chmod +x start.sh

EXPOSE 8000 8080 3000

CMD ["/app/start.sh"]
