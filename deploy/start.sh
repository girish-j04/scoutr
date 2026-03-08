#!/usr/bin/env bash
# ScoutR — Start / restart both services via PM2
# Run from any directory:  bash /opt/scoutr/deploy/start.sh
set -e

APP_DIR="/opt/scoutr"

echo "Starting ScoutR services..."

# ── Backend ──────────────────────────────────────────────────────────────────
pm2 delete scoutr-backend 2>/dev/null || true
pm2 start "$APP_DIR/deploy/backend.sh" \
  --name scoutr-backend \
  --interpreter bash
echo "[✓] Backend starting on :8000"

# ── Frontend ─────────────────────────────────────────────────────────────────
pm2 delete scoutr-frontend 2>/dev/null || true
pm2 start "$APP_DIR/deploy/frontend.sh" \
  --name scoutr-frontend \
  --interpreter bash
echo "[✓] Frontend starting on :3000"

pm2 save
pm2 startup systemd -u root --hp /root
echo ""
pm2 list
echo ""
echo "Done! Visit http://$(curl -s ifconfig.me)"
