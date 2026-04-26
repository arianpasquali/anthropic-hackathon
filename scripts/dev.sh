#!/usr/bin/env bash
set -euo pipefail

trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo "==> Starting backend (http://localhost:8000)"
uvicorn src.backend.app:app --reload &

echo "==> Starting frontend (http://localhost:3000)"
cd src/frontend && pnpm dev &

wait
