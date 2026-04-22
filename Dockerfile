FROM ghcr.io/stanleyy123/mai-ui-base:latest

WORKDIR /app

COPY server.py zoom_inference.py worker.py start.sh ./
RUN chmod +x start.sh

EXPOSE 8000 8080 3000

CMD ["/app/start.sh"]
