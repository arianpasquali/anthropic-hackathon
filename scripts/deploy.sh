#!/usr/bin/env bash
# Deploy kavel (backend + caddy) to boxd VM
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

# ── Caddy (HTTPS for api.kavel.tech) ──────────────────────────────────────
echo "==> Ensuring caddy is installed"
ssh $SSH_OPTS "$VM" '
  if ! command -v caddy &>/dev/null; then
    sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
    curl -1sLf "https://dl.cloudsmith.io/public/caddy/stable/gpg.key" | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf "https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt" | sudo tee /etc/apt/sources.list.d/caddy-stable.list
    sudo apt-get update && sudo apt-get install -y caddy
  fi
'
ssh $SSH_OPTS "$VM" "sudo cp $REMOTE_DIR/Caddyfile /etc/caddy/Caddyfile && sudo systemctl enable caddy && sudo systemctl reload-or-restart caddy"
STATUS=$(ssh $SSH_OPTS "$VM" "sudo systemctl is-active caddy")
echo "==> Caddy: $STATUS"

# ── Backend ────────────────────────────────────────────────────────────────
echo "==> Installing Python dependencies"
ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && uv sync --no-dev"

echo "==> Running migrations"
ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && uv run alembic upgrade head"

if $RESTART || ! ssh $SSH_OPTS "$VM" "pgrep -f 'uvicorn src.backend.app' > /dev/null 2>&1"; then
  echo "==> Restarting backend (port 8002)"
  ssh $SSH_OPTS "$VM" "pkill -f 'uvicorn src.backend.app' 2>/dev/null || true"
  sleep 2
  ssh $SSH_OPTS "$VM" "cd $REMOTE_DIR && mkdir -p logs && nohup uv run uvicorn src.backend.app:app --host 127.0.0.1 --port 8002 --workers 2 > logs/uvicorn.log 2>&1 < /dev/null &"
  sleep 3
  STATUS=$(ssh $SSH_OPTS "$VM" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8002/docs")
  echo "==> Backend health: /docs → HTTP $STATUS"
else
  echo "==> Backend already running (pass --restart to restart)"
fi

echo ""
echo "Done. API: https://api.kavel.tech"
