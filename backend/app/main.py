"""
ScoutR Unified FastAPI Application.

Merges Dev 1's data layer (ChromaDB, SQLite, CSV) with Dev 2's AI agent layer
(LangGraph orchestrator, Gemini LLM, SSE streaming) and Dev 3's Tactical Fit,
Monitoring, and PDF export into a single server.

Exposes:
- POST /query         → Full AI dossier response (batch)
- POST /query/stream  → SSE stream of reasoning steps + final result
- POST /search        → Raw player search via ChromaDB vector store
- GET  /player/{id}   → Single player profile (stats + financials)
- GET  /comparables   → Historical comparable transfers by fee (or by player_id)
- POST /export        → PDF scouting report (Dev 3)
- GET  /health        → Health check
"""

import json
import os
import sys
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
from app.services.mongo_service import (
    save_conversation, get_conversations, get_conversation,
    delete_conversation, count_conversations, close_mongo_client,
)
from app.services.cache_service import (
    get_cached_response, get_cached_by_criteria, cache_response,
    clear_cache, cache_stats,
)
from app.agents.query_parser import parse_query
from app.config import get_settings


# ──────────────────────────────────────────────
#  Request Models
# ──────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str


# ──────────────────────────────────────────────
#  Golden Path Detection
# ──────────────────────────────────────────────

GOLDEN_PATH_KEYWORDS = ["left-back", "under 24", "high press", "contract expir", "7m", "championship"]

GOLDEN_PATH_CACHE_FILE = os.path.join(
    os.path.dirname(__file__), '../data_pipeline/data/db/golden_path.json'
)


def _is_golden_path_query(query: str) -> bool:
    """Check if the query matches the demo golden path."""
    query_lower = query.lower()
    matches = sum(1 for kw in GOLDEN_PATH_KEYWORDS if kw in query_lower)
    return matches >= 4  # At least 4 of 6 keywords must match


# ──────────────────────────────────────────────
#  App Setup
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[+] ScoutR Unified Backend starting...")
    print("    -- AI Agent Endpoints --")
    print("    POST /query         - Full AI dossier response")
    print("    POST /query/stream  - SSE reasoning stream")
    print("    -- Data Layer Endpoints --")
    print("    POST /search        - ChromaDB player search")
    print("    GET  /player/{id}   - Player profile + financials")
    print("    GET  /comparables   - Comparable transfers")
    print("    POST /export        - PDF scouting report (Dev 3)")
    print("    -- History & Cache --")
    print("    GET  /history       - Conversation history")
    print("    GET  /history/{id}  - Single conversation")
    print("    DELETE /history/{id} - Delete conversation")
    print("    POST /cache/clear   - Clear response cache")
    print("    -- System --")
    print("    GET  /health        - Health check")
    yield
    await close_mongo_client()
    print("[-] ScoutR Unified Backend shutting down.")


app = FastAPI(
    title="ScoutR Unified API",
    description="Agentic AI Transfer Intelligence — Data Layer + Scout & Valuation Agents",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
#  System Endpoints
# ──────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "scoutr-unified"}


@app.get("/")
async def root():
    return {"status": "ok", "service": "scoutr-unified"}


# ──────────────────────────────────────────────
#  Data Layer Endpoints (from Dev 1)
# ──────────────────────────────────────────────

@app.post("/search")
def search_players(query: SearchQuery):
    """
    Search players via ChromaDB vector store with smart position mapping.
    Returns enriched candidates with financial data from SQLite.
    """
    query_dict = query.model_dump(exclude_unset=True)

    # Golden Path cache fallback
    if query_dict.get("position") == "left-back" and "Championship" in str(query_dict.get("preferred_leagues", [])):
        if os.path.exists(GOLDEN_PATH_CACHE_FILE):
            with open(GOLDEN_PATH_CACHE_FILE, 'r') as f:
                return json.load(f)

    # Live vector store search
    results = chroma_service.search_players(query_dict)

    # Enrich candidates with SQLite financials
    candidates = results.get("metadatas", [])
    if candidates:
        for candidate in candidates:
            pid = str(candidate.get("player_id", ""))
            if pid:
                financials = get_player_financials(pid)
                if financials:
                    candidate.update(financials)

    return {"status": "success", "candidates": candidates}


@app.get("/player/{player_id}")
def get_player(player_id: str):
    """Fetch a single player by ID — merges vector store stats with SQLite financials."""
    # Fetch from ChromaDB
    results = chroma_service.collection.get(ids=[player_id])
    if not results or not results["ids"]:
        raise HTTPException(status_code=404, detail="Player not found in Vector Store")

    metadata = results["metadatas"][0]

    # Merge with SQLite financials
    financials = get_player_financials(player_id)
    metadata.update(financials)

    return metadata


@app.get("/comparables")
def get_comp_transfers(target_fee: float | None = None, player_id: str | None = None):
    """
    Get comparable historical transfers.
    - target_fee: fee in millions (primary)
    - player_id: optional; fetches player's market_value and uses as target_fee (Dev 3 PDF export)
    """
    if target_fee is None and player_id:
        try:
            metadata = chroma_service.collection.get(ids=[player_id])
            if metadata and metadata.get("metadatas"):
                mv = metadata["metadatas"][0].get("market_value", 5.0)
            else:
                fin = get_player_financials(player_id)
                mv = float(fin.get("market_value", 5_000_000) or 5_000_000)
            # CSV expects fee in millions; market_value may be raw (e.g. 5000000) or millions
            target_fee = mv / 1_000_000 if mv > 1000 else mv
        except Exception:
            target_fee = 5.0
    if target_fee is None:
        target_fee = 5.0
    comps = csv_get_comparables(target_fee)
    out = {"comparables": comps}
    # Dev 3 PDF expects low_fee, mid_fee, high_fee for fee range
    if comps:
        fees = []
        for c in comps:
            fm = c.get("fee_m") if isinstance(c, dict) else getattr(c, "fee_millions", None)
            try:
                fees.append(float(fm) if fm else 0)
            except (TypeError, ValueError):
                pass
        if fees:
            low, high = min(fees), max(fees)
            mid = (low + high) / 2
            out["low_fee"] = f"€{int(low*1e6):,}"
            out["mid_fee"] = f"€{int(mid*1e6):,}"
            out["high_fee"] = f"€{int(high*1e6):,}"
    return out


# Dev 3: PDF export router (POST /export)
app.include_router(export_router)


# ──────────────────────────────────────────────
#  AI Agent Endpoints (from Dev 2)
# ──────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Two-tier cached AI pipeline:
      1. Check raw text cache (instant hit for identical queries)
      2. Run query parser (~2s) then check criteria cache
         (catches semantically equivalent queries)
      3. Only on double-miss → run full pipeline (~20s)
    """
    settings = get_settings()

    # Golden path shortcut
    if _is_golden_path_query(request.query):
        return GOLDEN_PATH_RESPONSE

    # Tier 1: exact text match (instant)
    cached = get_cached_response(request.query, ttl_seconds=settings.cache_ttl_seconds)
    if cached:
        return cached

    # Tier 2: parse the query, then check criteria cache
    parsed = await parse_query(request.query)
    parsed_dict = parsed.model_dump()

    cached_by_criteria = get_cached_by_criteria(parsed_dict, ttl_seconds=settings.cache_ttl_seconds)
    if cached_by_criteria:
        return cached_by_criteria

    # Double miss — run the full pipeline
    response, _events = await run_orchestrator(request.query)
    response_dict = response.model_dump()

    # Cache by both raw text AND parsed criteria
    cache_response(request.query, parsed_dict, response_dict)

    # Save to MongoDB
    try:
        await save_conversation(
            query=request.query,
            parsed_criteria=response_dict.get("parsed_criteria", {}),
            dossiers=response_dict.get("dossiers", []),
            total_candidates_evaluated=response_dict.get("total_candidates_evaluated", 0),
        )
    except Exception as e:
        print(f"[!] MongoDB save failed (non-fatal): {e}")

    return response


@app.post("/query/stream")
async def query_stream_endpoint(request: QueryRequest):
    """
    Stream reasoning steps via SSE, then emit the final result.
    Uses the same caching tiers as /query to avoid redundant work.
    """
    settings = get_settings()

    async def event_generator():
        # Golden path shortcut
        if _is_golden_path_query(request.query):
            demo_events = [
                SSEEvent(step="received_query", detail=f'Received query: "{request.query[:80]}..."'),
                SSEEvent(step="parsing_query", detail="Parsed query: Left-Back, under 24, max 7M, contract within 12 months"),
                SSEEvent(step="searching_players", detail="Searching for Left-Backs matching criteria across 8 players..."),
                SSEEvent(step="ranking_candidate", detail="#1 Ian Maatsen (Burnley) -- score: 88.5 | Elite pressing in the Championship"),
                SSEEvent(step="ranking_candidate", detail="#2 Destiny Udogie (Udinese) -- score: 84.2 | Complete modern full-back profile"),
                SSEEvent(step="ranking_candidate", detail="#3 Ramy Bensebaini (Gladbach) -- score: 79.8 | Bundesliga-tested pressing ability"),
                SSEEvent(step="starting_valuation", detail="Running valuation analysis on 3 candidates..."),
                SSEEvent(step="valuation_complete", detail="Valued Ian Maatsen: 3.5M - 6.0M (contract risk: red)"),
                SSEEvent(step="valuation_complete", detail="Valued Destiny Udogie: 4.0M - 6.5M (contract risk: amber)"),
                SSEEvent(step="valuation_complete", detail="Valued Ramy Bensebaini: 3.0M - 5.5M (contract risk: amber)"),
                SSEEvent(step="assembly_complete", detail="Assembled 3 complete player dossiers. Ready for review."),
            ]
            for event in demo_events:
                yield {"event": "agent_step", "data": event.model_dump_json()}
            yield {"event": "final_result", "data": GOLDEN_PATH_RESPONSE.model_dump_json()}
            return

        # Check caches before running pipeline
        cached_result = None

        # Tier 1: raw text cache
        cached_result = get_cached_response(request.query, ttl_seconds=settings.cache_ttl_seconds)

        # Tier 2+3: parse and check criteria cache / MongoDB
        if cached_result is None:
            try:
                parsed = await parse_query(request.query)
                parsed_dict = parsed.model_dump()
                cached_result = get_cached_by_criteria(parsed_dict, ttl_seconds=settings.cache_ttl_seconds)
                if cached_result is None:
                    mongo_hit = await find_by_criteria(parsed_dict)
                    if mongo_hit:
                        cached_result = {
                            "query": mongo_hit["query"],
                            "parsed_criteria": mongo_hit["parsed_criteria"],
                            "dossiers": mongo_hit["dossiers"],
                            "total_candidates_evaluated": mongo_hit.get("total_candidates_evaluated", 0),
                        }
                        cache_response(request.query, parsed_dict, cached_result)
            except Exception:
                pass

        # If we have a cached result, stream it with synthetic events
        if cached_result:
            yield {"event": "agent_step", "data": SSEEvent(step="cache_hit", detail="Found cached result -- returning instantly.").model_dump_json()}
            yield {"event": "final_result", "data": json.dumps(cached_result, default=str)}
            return

        # No cache -- run the full pipeline once and stream events
        try:
            response, events = await run_orchestrator(request.query)

            # Stream the collected events
            for event in events:
                yield {"event": "agent_step", "data": event.model_dump_json()}

            response_dict = response.model_dump()

            # Cache and save to MongoDB
            try:
                parsed = await parse_query(request.query)
                parsed_dict = parsed.model_dump()
                cache_response(request.query, parsed_dict, response_dict)
            except Exception:
                pass

            try:
                await save_conversation(
                    query=request.query,
                    parsed_criteria=response_dict.get("parsed_criteria", {}),
                    dossiers=response_dict.get("dossiers", []),
                    total_candidates_evaluated=response_dict.get("total_candidates_evaluated", 0),
                )
            except Exception:
                pass

            yield {"event": "final_result", "data": response.model_dump_json()}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
            yield {"event": "final_result", "data": GOLDEN_PATH_RESPONSE.model_dump_json()}

    return EventSourceResponse(event_generator())


# ──────────────────────────────────────────────
#  History & Cache Endpoints
# ──────────────────────────────────────────────

@app.get("/history")
async def list_history(limit: int = 20, skip: int = 0):
    """List past conversations, newest first."""
    conversations = await get_conversations(limit=limit, skip=skip)
    total = await count_conversations()
    return {"conversations": conversations, "total": total}


@app.get("/history/{conversation_id}")
async def get_history_item(conversation_id: str):
    """Get a specific past conversation with full dossier data."""
    conversation = await get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.delete("/history/{conversation_id}")
async def delete_history_item(conversation_id: str):
    """Delete a conversation from history."""
    deleted = await delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted", "id": conversation_id}


@app.post("/cache/clear")
async def clear_response_cache():
    """Clear the in-memory response cache."""
    count = clear_cache()
    return {"status": "cleared", "entries_removed": count}


@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    return cache_stats()
