#!/usr/bin/env bash
set -euo pipefail

trap 'kill $(jobs -p) 2>/dev/null' EXIT

lsof -ti :8002 | xargs kill -9 2>/dev/null || true
lsof -ti :3000 | xargs kill -9 2>/dev/null || true

echo "==> Starting backend (http://localhost:8002)"
uvicorn src.backend.app:app --reload --port 8002 &

echo "==> Starting frontend (http://localhost:3000)"
cd src/frontend && pnpm dev &

wait
