#!/bin/bash
set -e

mkdir -p /workspace/logs

# Stage 1: vLLM
echo "==> [1/3] Starting vLLM (MAI-UI-8B, bfloat16, port 8000)"
NUM_GPUS=$(nvidia-smi --list-gpus 2>/dev/null | wc -l)
NUM_GPUS=${NUM_GPUS:-1}
echo "==> Detected ${NUM_GPUS} GPU(s)"

python -m vllm.entrypoints.openai.api_server \
  --model /app/models/MAI-UI-8B \
  --served-model-name MAI-UI-8B \
  --dtype bfloat16 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 2 \
  --tensor-parallel-size ${NUM_GPUS} \
  --trust-remote-code \
  --host 0.0.0.0 \
  --port 8000 &

VLLM_PID=$!
echo "==> Waiting for vLLM on :8000 ..."
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
  kill -0 $VLLM_PID 2>/dev/null || { echo "ERROR: vLLM died"; exit 1; }
  sleep 5
done
echo "==> vLLM ready."

# Stage 2: FastAPI
echo "==> [2/3] Starting FastAPI (port 8080)"
uvicorn server:app --host 0.0.0.0 --port 8080 --workers 1 &
FASTAPI_PID=$!
echo "==> Waiting for FastAPI on :8080 ..."
until curl -sf http://localhost:8080/health > /dev/null 2>&1; do
  kill -0 $FASTAPI_PID 2>/dev/null || { echo "ERROR: FastAPI died"; exit 1; }
  sleep 3
done
echo "==> FastAPI ready."

# Stage 3: pyworker (foreground PID 1)
echo "==> [3/3] Starting pyworker (port ${WORKER_PORT:-3000})"
exec python worker.py
