"""
Scout Agent.

Searches for players matching structured criteria, applies weighted ranking,
and uses Gemini to generate scouting reasoning for each candidate.
"""

import asyncio

from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas import (
    ParsedSearchCriteria,
    PlayerProfile,
    RankedCandidate,
    CandidateReasoning,
)
from app.config import get_settings
from app.services.player_search import search_players


REASONING_SYSTEM_PROMPT = """You are an elite football scout. Given a player's profile and the search criteria, write a scouting assessment.

Your output must contain:
- ranking_reason: ONE sentence explaining why this player ranks at this specific position
- scouting_summary: 2-3 sentences highlighting the player's key strengths and how they fit the sporting director's requirements

Be specific — reference actual stats, league context, and contract situation. Sound like a real scout, not a generic AI."""


def _compute_tactical_fit_score(player: PlayerProfile, criteria: ParsedSearchCriteria) -> float:
    """Compute tactical fit sub-score (0-100) based on pressing metrics."""
    score = player.press_score  # Base: the player's composite press score

    # Bonus for progressive carrying
    if player.progressive_carries_per_90 >= 4.0:
        score = min(100, score + 8)
    elif player.progressive_carries_per_90 >= 3.5:
        score = min(100, score + 4)

    # Bonus for high pressure success rate
    if player.press_metrics.pressure_success_rate >= 35:
        score = min(100, score + 5)

    return round(score, 1)


def _compute_fee_fit_score(player: PlayerProfile, criteria: ParsedSearchCriteria) -> float:
    """Compute fee fit sub-score (0-100) — lower market value relative to budget scores higher."""
    if criteria.max_fee is None or criteria.max_fee == 0:
        return 50.0  # Neutral if no budget specified

    ratio = player.market_value / criteria.max_fee
    if ratio <= 0.5:
        return 95.0  # Bargain
    elif ratio <= 0.7:
        return 85.0
    elif ratio <= 0.85:
        return 70.0
    elif ratio <= 1.0:
        return 55.0
    else:
        return 20.0  # Over budget


def _compute_contract_urgency_score(player: PlayerProfile, criteria: ParsedSearchCriteria) -> float:
    """Compute contract urgency sub-score (0-100) — shorter contract = higher score."""
    months = player.contract_expiry_months

    if months <= 3:
        return 100.0  # Free agent territory
    elif months <= 6:
        return 95.0   # Maximum urgency
    elif months <= 9:
        return 80.0
    elif months <= 12:
        return 65.0
    elif months <= 18:
        return 40.0
    else:
        return 15.0  # Long contract, no urgency


def _compute_rank_score(
    tactical: float, fee: float, urgency: float
) -> float:
    """Weighted composite score: tactical 40%, fee 30%, contract urgency 30%."""
    return round(tactical * 0.4 + fee * 0.3 + urgency * 0.3, 1)


async def run_scout_agent(
    criteria: ParsedSearchCriteria,
    top_n: int = 3,
) -> list[RankedCandidate]:
    """
    Run the Scout Agent:
    1. Search for players matching criteria
    2. Apply weighted ranking
    3. Generate Gemini-powered scouting reasoning for top candidates
    4. Return top N ranked candidates
    """
    settings = get_settings()

    # Step 1: Search
    players = await search_players(criteria)

    if not players:
        return []

    # Step 2: Score and rank
    scored: list[tuple[PlayerProfile, float, float, float, float]] = []
    for player in players:
        tactical = _compute_tactical_fit_score(player, criteria)
        fee = _compute_fee_fit_score(player, criteria)
        urgency = _compute_contract_urgency_score(player, criteria)
        composite = _compute_rank_score(tactical, fee, urgency)
        scored.append((player, composite, tactical, fee, urgency))

    # Sort by composite score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    top_players = scored[:top_n]

    # Step 3: Generate reasoning via Gemini
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model_name,
        google_api_key=settings.gemini_api_key,
        temperature=0.4,
    )
    structured_llm = llm.with_structured_output(CandidateReasoning)

    candidates: list[RankedCandidate] = []

    # Build reasoning tasks for concurrent execution
    async def _get_reasoning(rank_idx, player, composite, tactical, fee, urgency):
        return await structured_llm.ainvoke([
            ("system", REASONING_SYSTEM_PROMPT),
            ("human", (
                f"Rank #{rank_idx} out of {len(players)} candidates evaluated.\n\n"
                f"Search criteria: {criteria.model_dump_json()}\n\n"
                f"Player profile:\n"
                f"- Name: {player.name}\n"
                f"- Club: {player.club} ({player.league})\n"
                f"- Age: {player.age}, Position: {player.position}\n"
                f"- Contract: {player.contract_expiry_months} months remaining\n"
                f"- Market value: EUR {player.market_value}M\n"
                f"- Press score: {player.press_score}/100 (PPDA: {player.press_metrics.ppda}, "
                f"Pressure success: {player.press_metrics.pressure_success_rate}%)\n"
                f"- Progressive carries/90: {player.progressive_carries_per_90}\n"
                f"- xA/90: {player.xa_per_90}, xG/90: {player.xg_per_90}\n\n"
                f"Composite score: {composite} "
                f"(tactical fit: {tactical}, fee fit: {fee}, contract urgency: {urgency})"
            )),
        ])

    # Run ALL reasoning calls concurrently (saves ~10-15s)
    reasoning_results = await asyncio.gather(*[
        _get_reasoning(rank_idx, player, composite, tactical, fee, urgency)
        for rank_idx, (player, composite, tactical, fee, urgency) in enumerate(top_players, start=1)
    ])

    for rank_idx, ((player, composite, tactical, fee, urgency), reasoning) in enumerate(
        zip(top_players, reasoning_results), start=1
    ):
        candidates.append(RankedCandidate(
            player=player,
            rank=rank_idx,
            rank_score=composite,
            tactical_fit_score=tactical,
            fee_fit_score=fee,
            contract_urgency_score=urgency,
            reasoning=reasoning,
        ))

    return candidates
