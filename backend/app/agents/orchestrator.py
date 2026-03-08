"""
LangGraph Orchestrator.

Chains: query parser → Scout Agent → Valuation Agent → Tactical Fit (Dev 3) → output assembly.
Emits SSE events at each step for live frontend streaming.
"""

from __future__ import annotations

import asyncio
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

from scoutr.scoring.tactical_score import (
    compute_tactical_fit_score,
    compute_formation_compatibility,
    get_top_formations,
)
from scoutr.agents.tactical_fit import _infer_heatmap_zones, _fallback_explanation

from app.schemas import (
    ParsedSearchCriteria,
    RankedCandidate,
    ValuationResult,
    PlayerDossier,
    QueryResponse,
    SSEEvent,
)
from app.agents.query_parser import parse_query
from app.agents.scout_agent import run_scout_agent
from app.agents.valuation_agent import run_valuation_agent


# ──────────────────────────────────────────────
#  LangGraph State
# ──────────────────────────────────────────────

class OrchestratorState(TypedDict):
    query: str
    parsed_criteria: Optional[ParsedSearchCriteria]
    candidates: Optional[list[RankedCandidate]]
    valuations: Optional[list[ValuationResult]]
    dossiers: Optional[list[PlayerDossier]]
    events: list[SSEEvent]
    # For follow-up queries: merge with previous context
    previous_query: Optional[str]
    previous_criteria: Optional[dict]


# ──────────────────────────────────────────────
#  Graph Nodes
# ──────────────────────────────────────────────

async def parse_query_node(state: OrchestratorState) -> dict:
    """Node 1: Parse the natural language query into structured criteria."""
    query = state["query"]
    previous_query = state.get("previous_query")
    previous_criteria = state.get("previous_criteria")

    criteria = await parse_query(
        query,
        previous_query=previous_query,
        previous_criteria=previous_criteria,
    )

    return {
        "parsed_criteria": criteria,
        "events": state["events"] + [
            SSEEvent(
                step="parsing_query",
                detail=f"Parsed query into criteria: position={criteria.position}, "
                       f"max_age={criteria.max_age}, max_fee=€{criteria.max_fee}M, "
                       f"contract within {criteria.contract_expiry_within_months} months",
            ),
        ],
    }


async def scout_node(state: OrchestratorState) -> dict:
    """Node 2: Run the Scout Agent to find and rank candidates."""
    criteria = state["parsed_criteria"]

    events = state["events"] + [
        SSEEvent(
            step="searching_players",
            detail=f"Searching for {criteria.position}s matching criteria across player database...",
        ),
    ]

    candidates = await run_scout_agent(criteria, top_n=3)

    # Emit ranking events
    for c in candidates:
        events.append(SSEEvent(
            step="ranking_candidate",
            detail=f"#{c.rank} {c.player.name} ({c.player.club}) — "
                   f"score: {c.rank_score} | {c.reasoning.ranking_reason}",
        ))

    return {
        "candidates": candidates,
        "events": events,
    }


async def valuation_node(state: OrchestratorState) -> dict:
    """Node 3: Run the Valuation Agent on each candidate."""
    candidates = state["candidates"]

    events = state["events"] + [
        SSEEvent(
            step="starting_valuation",
            detail=f"Running valuation analysis on {len(candidates)} candidates...",
        ),
    ]

    # Run valuations concurrently for speed
    valuation_tasks = [run_valuation_agent(c) for c in candidates]
    valuations = await asyncio.gather(*valuation_tasks)

    for v in valuations:
        events.append(SSEEvent(
            step="valuation_complete",
            detail=f"Valued player {v.player_id}: €{v.fee_range.low_estimate}M - "
                   f"€{v.fee_range.high_estimate}M (contract risk: {v.contract_risk.value})",
        ))

    return {
        "valuations": list(valuations),
        "events": events,
    }


async def assemble_node(state: OrchestratorState) -> dict:
    """Node 4: Assemble final dossiers from all agent outputs."""
    candidates = state["candidates"]
    valuations = state["valuations"]

    # Build a lookup from player_id to valuation
    val_map = {v.player_id: v for v in valuations}

    dossiers: list[PlayerDossier] = []
    for c in candidates:
        v = val_map.get(c.player.player_id)
        if v is None:
            continue

        # Compute tactical fit directly from player data (no HTTP call)
        player_dict = c.player.model_dump()
        try:
            tac_score = compute_tactical_fit_score(player_dict)
            formations = get_top_formations(player_dict, top_n=3)
            zones = _infer_heatmap_zones(player_dict)
            explanation = _fallback_explanation(player_dict, tac_score)
        except Exception:
            tac_score = None
            formations = None
            zones = None
            explanation = None

        dossier = PlayerDossier(
            player=c.player,
            rank=c.rank,
            rank_score=c.rank_score,
            ranking_reason=c.reasoning.ranking_reason,
            scouting_summary=c.reasoning.scouting_summary,
            fee_range=v.fee_range,
            contract_risk=v.contract_risk,
            comparable_transfers=v.comparable_transfers,
            valuation_narrative=v.valuation_summary.valuation_narrative,
            negotiation_insight=v.valuation_summary.negotiation_insight,
            tactical_fit_score=tac_score,
            fit_explanation=explanation,
            heatmap_zones=zones,
            formation_compatibility=formations,
        )
        dossiers.append(dossier)

    events = state["events"] + [
        SSEEvent(
            step="assembly_complete",
            detail=f"Assembled {len(dossiers)} complete player dossiers. Ready for review.",
        ),
    ]

    return {
        "dossiers": dossiers,
        "events": events,
    }


# ──────────────────────────────────────────────
#  Build the Graph
# ──────────────────────────────────────────────

def build_orchestrator_graph() -> StateGraph:
    """Build and compile the LangGraph orchestration graph."""
    graph = StateGraph(OrchestratorState)

    graph.add_node("parse_query", parse_query_node)
    graph.add_node("scout", scout_node)
    graph.add_node("valuate", valuation_node)
    graph.add_node("assemble", assemble_node)

    graph.set_entry_point("parse_query")
    graph.add_edge("parse_query", "scout")
    graph.add_edge("scout", "valuate")
    graph.add_edge("valuate", "assemble")
    graph.add_edge("assemble", END)

    return graph.compile()


async def run_orchestrator(
    query: str,
    previous_query: Optional[str] = None,
    previous_criteria: Optional[dict] = None,
) -> tuple[QueryResponse, list[SSEEvent]]:
    """
    Run the full orchestration pipeline and return the final response + events.
    When previous_query and previous_criteria are provided, the parser merges
    the follow-up with the previous context.
    """
    graph = build_orchestrator_graph()

    initial_state: OrchestratorState = {
        "query": query,
        "parsed_criteria": None,
        "candidates": None,
        "valuations": None,
        "dossiers": None,
        "events": [
            SSEEvent(
                step="received_query",
                detail=f"Received query: \"{query[:100]}{'...' if len(query) > 100 else ''}\"",
            ),
        ],
        "previous_query": previous_query,
        "previous_criteria": previous_criteria,
    }

    final_state = await graph.ainvoke(initial_state)

    response = QueryResponse(
        query=query,
        parsed_criteria=final_state["parsed_criteria"],
        dossiers=final_state["dossiers"],
        total_candidates_evaluated=len(final_state["candidates"]) if final_state["candidates"] else 0,
    )

    return response, final_state["events"]


async def run_orchestrator_streaming(
    query: str,
    previous_query: Optional[str] = None,
    previous_criteria: Optional[dict] = None,
):
    """
    Generator that yields SSEEvents as the orchestrator progresses.
    Supports follow-up merging via previous_query and previous_criteria.
    """
    graph = build_orchestrator_graph()

    initial_state: OrchestratorState = {
        "query": query,
        "parsed_criteria": None,
        "candidates": None,
        "valuations": None,
        "dossiers": None,
        "events": [
            SSEEvent(
                step="received_query",
                detail=f"Received query: \"{query[:100]}{'...' if len(query) > 100 else ''}\"",
            ),
        ],
        "previous_query": previous_query,
        "previous_criteria": previous_criteria,
    }

    seen_events = 0

    async for state_update in graph.astream(initial_state):
        # Each state_update is a dict keyed by node name
        for node_name, node_output in state_update.items():
            if "events" in node_output:
                new_events = node_output["events"][seen_events:]
                for event in new_events:
                    yield event
                seen_events = len(node_output["events"])

            # If this is the final assemble node, yield the result
            if "dossiers" in node_output and node_output["dossiers"] is not None:
                # Build and yield the final response object as a special event
                final_state = {**initial_state}
                final_state.update(node_output)

                # We need parsed_criteria too - get it from accumulated state
                yield SSEEvent(
                    step="final_result",
                    detail="DONE",
                )
