#!/usr/bin/env bash
# Deploy / sync klimaatkracht backend to boxd VM
# Usage: ./scripts/deploy.sh [--restart]
set -euo pipefail

VM="klimaatkracht.boxd.sh"
REMOTE_DIR="/home/boxd/app"
SSH_OPTS="-o StrictHostKeyChecking=no"
FNM_BIN="/home/boxd/.local/share/fnm/node-versions/v22.22.2/installation/bin"

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
  --exclude='src/frontend/node_modules' \
  --exclude='src/frontend/.next' \
  -e "ssh $SSH_OPTS" \
  ./ "$VM:$REMOTE_DIR/"

echo "==> Syncing data files (db + env)"
rsync -az -e "ssh $SSH_OPTS" foodbank.db .env "$VM:$REMOTE_DIR/"

# ── Backend ────────────────────────────────────────────────────────────────
echo "==> Installing Python dependencies"
ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && uv sync --no-dev"

echo "==> Running migrations"
ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && uv run alembic upgrade head"

if $RESTART || ! ssh $SSH_OPTS "$VM" "pgrep -f 'uvicorn src.backend.app' > /dev/null 2>&1"; then
  echo "==> Restarting backend (port 8002)"
  ssh $SSH_OPTS "$VM" "pkill -f 'uvicorn src.backend.app' 2>/dev/null || true"
  sleep 2
  ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && mkdir -p logs && nohup uv run uvicorn src.backend.app:app --host 0.0.0.0 --port 8002 --workers 2 > logs/uvicorn.log 2>&1 < /dev/null &"
  sleep 3
  STATUS=$(ssh $SSH_OPTS "$VM" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8002/docs")
  echo "==> Backend health: /docs → HTTP $STATUS"
else
  echo "==> Backend already running (pass --restart to restart)"
fi

# ── Frontend ───────────────────────────────────────────────────────────────
echo "==> Installing frontend dependencies"
ssh $SSH_OPTS "$VM" "export PATH=\"$FNM_BIN:\$PATH\" && cd $REMOTE_DIR/src/frontend && pnpm install --frozen-lockfile"

echo "==> Building frontend"
ssh $SSH_OPTS "$VM" "export PATH=\"$FNM_BIN:\$PATH\" && cd $REMOTE_DIR/src/frontend && pnpm build"

echo "==> Restarting frontend (port 3000)"
ssh $SSH_OPTS "$VM" "pkill -f 'next start' 2>/dev/null || true"
sleep 1
ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR/src/frontend && export PATH=\"$FNM_BIN:\$PATH\" && nohup ./node_modules/.bin/next start -p 3000 > /tmp/next.log 2>&1 < /dev/null &"
sleep 5
STATUS=$(ssh $SSH_OPTS "$VM" "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000")
echo "==> Frontend health: / → HTTP $STATUS"

echo ""
echo "Done. https://klimaatkracht.boxd.sh"
