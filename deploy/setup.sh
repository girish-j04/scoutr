#!/usr/bin/env bash
# ScoutR — Vultr VPS Setup Script
# Run as root on a fresh Ubuntu 22.04 instance:
#   bash setup.sh
set -e

echo "=========================================="
echo " ScoutR VPS Setup"
echo "=========================================="

# ── 1. System packages ──────────────────────────────────────────────────────
apt-get update -qq
apt-get install -y \
  git curl wget nginx \
  python3.11 python3.11-venv python3-pip \
  # WeasyPrint system deps
  libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
  libgdk-pixbuf2.0-0 libffi-dev libssl-dev \
  # Build tools
  build-essential

# ── 2. Node.js 20 via NodeSource ────────────────────────────────────────────
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
npm install -g pm2

echo "[✓] System packages installed"

# ── 3. Clone the repo ───────────────────────────────────────────────────────
APP_DIR="/opt/scoutr"
if [ -d "$APP_DIR" ]; then
  echo "[!] $APP_DIR already exists — pulling latest..."
  git -C "$APP_DIR" pull
else
  git clone https://github.com/girish-j04/scoutr.git "$APP_DIR"
fi
echo "[✓] Repo at $APP_DIR"

# ── 4. Backend — Python virtualenv + deps ───────────────────────────────────
cd "$APP_DIR/backend"
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate
echo "[✓] Backend Python deps installed"

# ── 5. Frontend — npm install + build ───────────────────────────────────────
cd "$APP_DIR/frontend"
npm ci --legacy-peer-deps
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run build
echo "[✓] Frontend built"

# ── 6. Nginx config ─────────────────────────────────────────────────────────
cat > /etc/nginx/sites-available/scoutr <<'NGINX'
server {
    listen 80;
    server_name _;

    # Next.js frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # FastAPI backend
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        chunked_transfer_encoding on;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/scoutr /etc/nginx/sites-enabled/scoutr
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
echo "[✓] Nginx configured"

echo ""
echo "=========================================="
echo " Setup complete!"
echo " Next: fill in /opt/scoutr/backend/.env"
echo " Then: bash /opt/scoutr/deploy/start.sh"
echo "=========================================="
