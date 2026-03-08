#!/usr/bin/env bash
APP_DIR="/opt/scoutr"
cd "$APP_DIR/backend"
source .venv/bin/activate
set -a; source .env; set +a
exec python -c "
import os, uvicorn
for k in ['GEMINI_API_KEY','GEMINI_MODEL_NAME','USE_MOCK_DATA','MONGO_URI','RAPID_API_KEY','SCOUTR_RAPID_API_KEY','scoutr_rapid_api_key','ANTHROPIC_API_KEY']:
    os.environ.pop(k, None)
uvicorn.run('app.main:app', host='127.0.0.1', port=8000, workers=2)
"
