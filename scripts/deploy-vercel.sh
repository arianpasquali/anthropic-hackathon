#!/usr/bin/env bash
# Deploy frontend to Vercel (production).
# Backend stays on boxd — set BACKEND_URL to override the default.
# Usage: ./scripts/deploy-vercel.sh [--preview]
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-https://klimaatkracht.boxd.sh}"
PROD_FLAG="--prod"
for arg in "$@"; do
  [[ "$arg" == "--preview" ]] && PROD_FLAG=""
done

# ── Preflight ────────────────────────────────────────────────────────────────
if ! command -v vercel &>/dev/null; then
  echo "==> Installing Vercel CLI"
  npm i -g vercel
fi

# Link project on first run (interactive)
if [ ! -f "src/frontend/.vercel/project.json" ]; then
  echo "==> Linking Vercel project (one-time setup)"
  vercel link --cwd src/frontend
fi

# ── Sync env vars ────────────────────────────────────────────────────────────
echo "==> Setting BACKEND_URL=$BACKEND_URL on Vercel (production)"
vercel env rm BACKEND_URL production --yes --cwd src/frontend 2>/dev/null || true
printf '%s' "$BACKEND_URL" | vercel env add BACKEND_URL production --cwd src/frontend
vercel env ls --cwd src/frontend 2>/dev/null | grep BACKEND_URL || echo "WARNING: BACKEND_URL not found in Vercel env after set"

# ── Deploy ───────────────────────────────────────────────────────────────────
echo "==> Deploying frontend to Vercel ${PROD_FLAG:-(preview)}"
vercel $PROD_FLAG --cwd src/frontend

echo ""
echo "Done. Backend: $BACKEND_URL"
