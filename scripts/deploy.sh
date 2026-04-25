#!/usr/bin/env bash
# Deploy / sync klimaatkracht backend to boxd VM
# Usage: ./scripts/deploy.sh [--restart]
set -euo pipefail

VM="klimaatkracht.boxd.sh"
REMOTE_DIR="/home/boxd/app"
SSH_OPTS="-o StrictHostKeyChecking=no"

RESTART=false
for arg in "$@"; do
  [[ "$arg" == "--restart" ]] && RESTART=true
done

echo "==> Syncing code to $VM:$REMOTE_DIR"
rsync -az --delete \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='.uv-cache' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='logs/' \
  --exclude='data/*.pdf' \
  --exclude='data/*.txt' \
  --exclude='.env' \
  -e "ssh $SSH_OPTS" \
  ./ "$VM:$REMOTE_DIR/"

echo "==> Syncing data files (db + env)"
rsync -az -e "ssh $SSH_OPTS" \
  foodbank.db \
  .env \
  "$VM:$REMOTE_DIR/"

echo "==> Installing dependencies"
ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && uv sync --no-dev"

echo "==> Running migrations"
ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && uv run alembic upgrade head"

if $RESTART || ! ssh $SSH_OPTS "$VM" "pgrep -f 'uvicorn src.backend.app' > /dev/null 2>&1"; then
  echo "==> Starting server"
  ssh $SSH_OPTS "$VM" "
    cd $REMOTE_DIR
    pkill -f 'uvicorn src.backend.app' 2>/dev/null || true
    sleep 1
    mkdir -p logs
    nohup uv run uvicorn src.backend.app:app \
      --host 0.0.0.0 --port 8000 \
      --workers 2 \
      > logs/uvicorn.log 2>&1 & disown
    echo 'Server started'
  "
  sleep 3
  STATUS=$(ssh $SSH_OPTS "$VM" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs")
  echo "==> Health check: /docs → HTTP $STATUS"
else
  echo "==> Server already running (pass --restart to restart)"
fi

echo ""
echo "Done. Live at: https://klimaatkracht.boxd.sh"
