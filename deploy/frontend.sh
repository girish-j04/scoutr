#!/usr/bin/env bash
APP_DIR="/opt/scoutr"
cd "$APP_DIR/frontend"
BACKEND_URL=http://127.0.0.1:8000 exec npm start -- -p 3000
