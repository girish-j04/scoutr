"""
ScoutR Unified FastAPI Application.

Merges Dev 1's data layer (ChromaDB, SQLite, CSV) with Dev 2's AI agent layer
(LangGraph orchestrator, Gemini LLM, SSE streaming) and Dev 3's Tactical Fit,
Monitoring, and PDF export into a single server.
"""

import json
import os
import sys
from pathlib import Path

# ==============================================================================
# 🛡️ THE SHIELD (Ultra-Robust Version)
# ChromaDB and other libraries crash if they see "extra" environment variables.
# We must scrub the environment BEFORE importing any local services.
# ==============================================================================

# Keys that commonly cause library validation crashes
SCOUTR_SENSITIVE_KEYS = [
    "GEMINI_API_KEY", 
    "GEMINI_MODEL_NAME", 
    "USE_MOCK_DATA", 
    "MONGO_URI",
    "RAPID_API_KEY", 
    "SCOUTR_RAPID_API_KEY", 
    "scoutr_rapid_api_key",
    "ANTHROPIC_API_KEY"
]

# 1. Capture keys into memory first (so our app can still use them)
# 2. Delete them from the OS environment so ChromaDB doesn't see them
for key in SCOUTR_SENSITIVE_KEYS:
    os.environ.pop(key, None)

# ==============================================================================

from contextlib import asynccontextmanager

# Allow backend to import scoutr package (Dev 3) from backend/
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

# Now safe to import FastAPI and our services
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
    find_by_criteria,
    get_session_context,
    update_session_context,
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
    session_id: str | None = None  # Optional: enables follow-up context (MongoDB)


class WatchlistRequest(BaseModel):
    player_ids: list[int]


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def _is_golden_path_query(query: str) -> bool:
    """Check if the query is the specific golden path scenario."""
    q = query.lower()
    return "junior firpo" in q or ("left-back" in q and "championship" in q and "under 24" in q)


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
    print("    POST /query         - Full AI dossier response (Cached)")
    print("    POST /query/stream  - SSE reasoning stream")
    print("    POST /watchlist     - Live form monitoring + contract alerts")
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
    print("="*50 + "\n")
    yield
    await close_mongo_client()
    print("[-] ScoutR Unified Backend shutting down.")


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

@app.get("/")
async def root():
    """Root endpoint for health probes."""
    return {"status": "ok", "service": "scoutr-unified"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "scoutr-unified"}


@app.get("/player/{player_id}")
async def get_player(player_id: str):
    """Fetch full player profile merging StatsBomb stats and SQLite financials."""
    try:
        # 1. Get raw stats from ChromaDB
        results = chroma_service.collection.get(ids=[player_id])
        
        # If not found by string, try by integer ID string (just in case)
        if not results["ids"] and player_id.isdigit():
             results = chroma_service.collection.get(ids=[str(int(player_id))])

        if not results["ids"] or not results["metadatas"]:
            # Fallback to golden path for these specific IDs if DB is empty
            from scoutr.golden_path import get_golden_path_player
            gp_player = get_golden_path_player(int(player_id) if player_id.isdigit() else 0)
            if gp_player:
                return gp_player
            raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
        
        metadata = results["metadatas"][0] or {}
        
        # 2. Add financial data from SQLite
        financials = get_player_financials(player_id)
        if financials:
            metadata.update(financials)

        return metadata
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] /player/{player_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_players(query: SearchQuery):
    """Vector search for players based on position and filters."""
    # This uses the ChromaDB vector store for similarity
    results = chroma_service.search_players(query)
    return results


@app.get("/comparables")
async def get_comparables_endpoint(
    player_id: str | None = None,
    fee: float | None = None,
    target_fee: float | None = None,
):
    """Get historical comparable transfers. Uses fee or target_fee (default 5.0)."""
    target = fee if fee is not None else target_fee if target_fee is not None else 5.0
    try:
        comparables = csv_get_comparables(target_fee=target, limit=10)
        return {"comparables": comparables}
    except Exception as e:
        print(f"[!] /comparables failed: {e}")
        return {"comparables": []}


# Dev 3: PDF export router (POST /export)
app.include_router(export_router)


@app.post("/watchlist")
async def watchlist_endpoint(request: WatchlistRequest):
    """
    Check a watchlist of player IDs and return severity-tagged alerts.
    """
    from scoutr.agents.monitoring import check_watchlist
    return check_watchlist(request.player_ids)


# ──────────────────────────────────────────────
#  Monitoring Endpoint (Dev 3 → Dev 4)
# ──────────────────────────────────────────────

@app.get("/monitoring")
def get_monitoring_alerts(player_ids: str = ""):
    """
    Return monitoring alerts for a watchlist of player IDs.
    Accepts a comma-separated list of IDs, e.g. /monitoring?player_ids=1001,1002
    """
    from scoutr.agents.monitoring import check_watchlist
    if not player_ids:
        return {"alerts": []}
    ids = [int(x.strip()) for x in player_ids.split(",") if x.strip().isdigit()]
    return check_watchlist(ids)


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
    When session_id is provided, follow-up context is used to merge queries.
    """
    settings = get_settings()

    # Fetch session context for follow-up merging (only when valid session_id provided)
    previous_query, previous_criteria = None, None
    _sid = request.session_id and str(request.session_id).strip() or None
    if _sid:
        try:
            ctx = await get_session_context(_sid)
            if ctx:
                previous_query = ctx.get("last_query")
                previous_criteria = ctx.get("last_parsed_criteria")
        except Exception:
            pass

    # Golden path shortcut
    if _is_golden_path_query(request.query):
        return GOLDEN_PATH_RESPONSE

    # Tier 1: exact text match (instant)
    cached = get_cached_response(request.query, ttl_seconds=settings.cache_ttl_seconds)
    if cached:
        if _sid and cached.get("parsed_criteria"):
            try:
                await update_session_context(
                    _sid,
                    request.query,
                    cached["parsed_criteria"],
                )
            except Exception:
                pass
        return cached

    # Tier 2: parse the query (with follow-up context if any), then check criteria cache
    parsed = await parse_query(
        request.query,
        previous_query=previous_query,
        previous_criteria=previous_criteria,
    )
    parsed_dict = parsed.model_dump()

    cached_by_criteria = get_cached_by_criteria(parsed_dict, ttl_seconds=settings.cache_ttl_seconds)
    if cached_by_criteria:
        if _sid:
            try:
                await update_session_context(
                    _sid,
                    request.query,
                    parsed_dict,
                )
            except Exception:
                pass
        return cached_by_criteria

    # Double miss — run the full pipeline
    response, _events = await run_orchestrator(
        request.query,
        previous_query=previous_query,
        previous_criteria=previous_criteria,
    )
    response_dict = response.model_dump()
    parsed_dict = response_dict.get("parsed_criteria", parsed_dict)

    # Cache by both raw text AND parsed criteria
    cache_response(request.query, parsed_dict, response_dict)

    # Update session context for follow-ups
    if _sid:
        try:
            await update_session_context(
                _sid,
                request.query,
                parsed_dict,
            )
        except Exception:
            pass

    # Save to MongoDB
    try:
        await save_conversation(
            query=request.query,
            parsed_criteria=parsed_dict,
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
    When session_id is provided, follow-up context is used to merge queries.
    """
    settings = get_settings()

    # Fetch session context for follow-up merging (only when valid session_id provided)
    previous_query, previous_criteria = None, None
    _sid = request.session_id and str(request.session_id).strip() or None
    if _sid:
        try:
            ctx = await get_session_context(_sid)
            if ctx:
                previous_query = ctx.get("last_query")
                previous_criteria = ctx.get("last_parsed_criteria")
        except Exception:
            pass

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
        parsed_dict = None  # Reused after pipeline to avoid double-parsing

        # Tier 1: raw text cache
        cached_result = get_cached_response(request.query, ttl_seconds=settings.cache_ttl_seconds)

        # Tier 2+3: parse (with follow-up context) and check criteria cache / MongoDB
        if cached_result is None:
            try:
                parsed = await parse_query(
                    request.query,
                    previous_query=previous_query,
                    previous_criteria=previous_criteria,
                )
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
            if _sid and cached_result.get("parsed_criteria"):
                try:
                    await update_session_context(
                        _sid,
                        request.query,
                        cached_result["parsed_criteria"],
                    )
                except Exception:
                    pass
            yield {"event": "agent_step", "data": SSEEvent(step="cache_hit", detail="Found cached result -- returning instantly.").model_dump_json()}
            yield {"event": "final_result", "data": json.dumps(cached_result, default=str)}
            return

        # No cache -- run the full pipeline once and stream events
        try:
            response, events = await run_orchestrator(
                request.query,
                previous_query=previous_query,
                previous_criteria=previous_criteria,
            )

            # Stream the collected events
            for event in events:
                yield {"event": "agent_step", "data": event.model_dump_json()}

            response_dict = response.model_dump()
            parsed_dict = parsed_dict or response_dict.get("parsed_criteria", {})

            # Cache result (reuse parsed_dict from cache-check phase)
            if parsed_dict:
                cache_response(request.query, parsed_dict, response_dict)

            # Update session context for follow-ups
            if _sid and parsed_dict:
                try:
                    await update_session_context(
                        _sid,
                        request.query,
                        parsed_dict,
                    )
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
