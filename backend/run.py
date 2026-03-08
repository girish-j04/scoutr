"""
ScoutR Backend Entry Point.
"""

import os
import uvicorn

# 🛡️ THE MASTER SHIELD
# We must scrub the environment at the absolute entry point.
# This prevents ChromaDB from seeing "extra" variables and crashing on startup.
SENSITIVE_KEYS = [
    "GEMINI_API_KEY", 
    "GEMINI_MODEL_NAME", 
    "USE_MOCK_DATA", 
    "MONGO_URI",
    "RAPID_API_KEY", 
    "SCOUTR_RAPID_API_KEY", 
    "scoutr_rapid_api_key",
    "ANTHROPIC_API_KEY"
]

for key in SENSITIVE_KEYS:
    if key in os.environ:
        del os.environ[key]

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
