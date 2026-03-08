"""
ScoutR Unified FastAPI Application.

Merges Dev 1's data layer (ChromaDB, SQLite, CSV) with Dev 2's AI agent layer
(LangGraph orchestrator, Gemini LLM, SSE streaming) and Dev 3's Tactical Fit,
Monitoring, and PDF export into a single server.
"""

import json
import os
import sys

# 🛡️ THE SHIELD: ChromaDB crashes if it sees unrecognized variables.
# We remove them from memory here before any other library loads.
for key in ["RAPID_API_KEY", "SCOUTR_RAPID_API_KEY", "scoutr_rapid_api_key"]:
    os.environ.pop(key, None)

from contextlib import asynccontextmanager
from pathlib import Path

# Allow backend to import scoutr package (Dev 3) from backend/
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.agents.orchestrator import run_orchestrator, run_orchestrator_streaming
from scoutr.api.export_router import export_router
from app.mock_data import GOLDEN_PATH_RESPONSE
from app.schemas import QueryResponse, SSEEvent, SearchQuery
from app.services.chroma_service import chroma_service
from app.services.sqlite_service import get_player_financials
from app.services.csv_service import get_comparables as csv_get_comparables


# ──────────────────────────────────────────────
#  Request Models
# ──────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str


class WatchlistRequest(BaseModel):
    player_ids: list[int]


# ──────────────────────────────────────────────
#  App Lifecycle
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Print a clean banner
    print("\n" + "="*50)
    print(" 🛡️  ScoutR Unified Backend is Starting Up...")
    print("="*50)
    print("    -- AI Agent Endpoints --")
    print("    POST /query         - Full AI dossier response")
    print("    POST /query/stream  - SSE reasoning stream")
    print("    POST /watchlist     - Live form monitoring + contract alerts")
    print("    -- Data Layer Endpoints --")
    print("    POST /search        - ChromaDB player search")
    print("    GET  /player/{id}   - Player profile + financials")
    print("    GET  /health        - System Status")
    print("="*50 + "\n")
    yield

app = FastAPI(
    title="ScoutR Unified API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
#  Core Data API Endpoints (from Dev 1)
# ──────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "scoutr-unified"}


@app.get("/player/{player_id}")
async def get_player(player_id: str):
    """Fetch full player profile merging StatsBomb stats and SQLite financials."""
    # 1. Get raw stats from ChromaDB
    try:
        results = chroma_service.collection.get(ids=[player_id])
        if not results["ids"]:
             raise HTTPException(status_code=404, detail="Player not found in ChromaDB")
        
        metadata = results["metadatas"][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Add financial data from SQLite
    financials = get_player_financials(player_id)
    metadata.update(financials)

    return metadata


@app.post("/search")
async def search_players(query: SearchQuery):
    """Vector search for players based on position and filters."""
    # This uses the ChromaDB vector store for similarity
    results = chroma_service.search_players(query)
    return results


@app.get("/comparables")
async def get_comparables(player_id: str = None, fee: float = None):
    """Get historical comparable transfers."""
    return csv_get_comparables(player_id=player_id, fee=fee)


# Dev 3: PDF export router (POST /export)
app.include_router(export_router)


@app.post("/watchlist")
async def watchlist_endpoint(request: WatchlistRequest):
    """
    Check a watchlist of player IDs and return severity-tagged alerts.
    """
    from scoutr.agents.monitoring import check_watchlist
    return check_watchlist(
        request.player_ids,
        api_base_url="http://localhost:8000",
    )


# ──────────────────────────────────────────────
#  AI Agent Endpoints (from Dev 2)
# ──────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
async def query_batch(request: QueryRequest):
    """Full AI dossier response in a single JSON block."""
    result = await run_orchestrator(request.query)
    return result


@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """SSE stream of reasoning steps + final dossier."""
    return EventSourceResponse(run_orchestrator_streaming(request.query))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
