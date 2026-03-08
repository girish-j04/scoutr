"""
ScoutR Pydantic Schemas.

Every LLM call and agent output is bounded by these models.
This guarantees structured output without prompt engineering hacks — Gemini's
native JSON schema mode + Pydantic enforces the shape at the API level.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
#  Query Parser Output
# ──────────────────────────────────────────────

class ParsedSearchCriteria(BaseModel):
    """Structured search criteria parsed from a sporting director's natural language query."""

    position: str = Field(description="Primary position, e.g. 'Left-Back', 'Centre-Midfielder'")
    max_age: Optional[int] = Field(default=None, description="Maximum player age")
    max_fee: Optional[float] = Field(default=None, description="Maximum transfer fee in millions EUR")
    min_press_score: Optional[float] = Field(default=None, description="Minimum pressing intensity score (0-100)")
    contract_expiry_within_months: Optional[int] = Field(default=None, description="Contract must expire within this many months")
    preferred_leagues: Optional[list[str]] = Field(default=None, description="Preferred league names or tiers, e.g. ['Championship', 'Bundesliga 2']")
    additional_requirements: Optional[str] = Field(default=None, description="Any other requirements mentioned in the query")


# ──────────────────────────────────────────────
#  Player Data (from Dev 1 API)
# ──────────────────────────────────────────────

class PressMetrics(BaseModel):
    """Pressing and defensive metrics for a player."""

    ppda: float = Field(description="Passes Per Defensive Action — lower is more aggressive")
    pressure_success_rate: float = Field(description="Percentage of pressures that win possession (0-100)")
    defensive_actions_per_90: float = Field(description="Tackles + interceptions + blocks per 90 minutes")


class PlayerProfile(BaseModel):
    """Full player profile — the canonical data shape from Dev 1's API."""

    player_id: str
    name: str
    club: str
    league: str
    age: int
    position: str
    nationality: str
    contract_expiry_months: int = Field(description="Months remaining on current contract")
    market_value: float = Field(description="Estimated market value in millions EUR")
    press_metrics: PressMetrics
    progressive_carries_per_90: float
    xa_per_90: float = Field(description="Expected assists per 90 minutes")
    xg_per_90: float = Field(description="Expected goals per 90 minutes")
    minutes_played: int = Field(description="Total minutes played this season")
    press_score: float = Field(description="Composite pressing intensity score 0-100")


# ──────────────────────────────────────────────
#  Scout Agent Output
# ──────────────────────────────────────────────

class CandidateReasoning(BaseModel):
    """LLM-generated scouting reasoning for a ranked candidate."""

    ranking_reason: str = Field(description="One-sentence explanation of why this player ranks at this position")
    scouting_summary: str = Field(description="2-3 sentence scouting report highlighting strengths and fit")


class RankedCandidate(BaseModel):
    """A player candidate with ranking score and reasoning from the Scout Agent."""

    player: PlayerProfile
    rank: int = Field(description="Rank position (1 = best)")
    rank_score: float = Field(description="Composite weighted score (0-100)")
    tactical_fit_score: float = Field(description="Tactical fit sub-score (0-100)")
    fee_fit_score: float = Field(description="Fee fit sub-score (0-100)")
    contract_urgency_score: float = Field(description="Contract urgency sub-score (0-100)")
    reasoning: CandidateReasoning


# ──────────────────────────────────────────────
#  Valuation Agent Output
# ──────────────────────────────────────────────

class ContractRisk(str, Enum):
    """Contract risk classification based on months remaining."""

    GREEN = "green"    # > 18 months
    AMBER = "amber"    # 6-18 months
    RED = "red"        # < 6 months


class ComparableTransfer(BaseModel):
    """A historical transfer used as a comparable for fee estimation."""

    player_name: str
    from_club: str
    to_club: str
    fee_millions: float
    transfer_year: int
    age_at_transfer: int
    position: str


class FeeRange(BaseModel):
    """Estimated transfer fee range in millions EUR."""

    low_estimate: float = Field(description="Conservative fee estimate in €M")
    mid_estimate: float = Field(description="Most likely fee in €M")
    high_estimate: float = Field(description="Upper bound fee estimate in €M")


class ValuationSummary(BaseModel):
    """LLM-generated valuation narrative."""

    valuation_narrative: str = Field(description="2-3 sentence valuation analysis explaining the fee range and contract situation")
    negotiation_insight: str = Field(description="One-sentence tactical negotiation advice for the sporting director")


class ValuationResult(BaseModel):
    """Full valuation output for a single player."""

    player_id: str
    fee_range: FeeRange
    contract_risk: ContractRisk
    comparable_transfers: list[ComparableTransfer]
    valuation_summary: ValuationSummary


# ──────────────────────────────────────────────
#  Assembled Dossier (Final Output)
# ──────────────────────────────────────────────

class PlayerDossier(BaseModel):
    """Complete scouting dossier for a single candidate — the main output card."""

    player: PlayerProfile
    rank: int
    rank_score: float
    ranking_reason: str
    scouting_summary: str
    fee_range: FeeRange
    contract_risk: ContractRisk
    comparable_transfers: list[ComparableTransfer]
    valuation_narrative: str
    negotiation_insight: str

    # Dev 3 Tactical Fit Agent output
    tactical_fit_score: Optional[float] = Field(default=None, description="Score 0-100, filled by Tactical Fit Agent")
    fit_explanation: Optional[str] = Field(default=None, description="Plain-English tactical fit explanation")
    heatmap_zones: Optional[list[str]] = Field(default=None, description="Positional zones from heatmap analysis")
    formation_compatibility: Optional[list[str]] = Field(default=None, description="Best formations, e.g. ['4-3-3', '4-2-3-1']")


class QueryResponse(BaseModel):
    """Top-level response returned by the POST /query endpoint."""

    query: str
    parsed_criteria: ParsedSearchCriteria
    dossiers: list[PlayerDossier]
    total_candidates_evaluated: int


# ──────────────────────────────────────────────
#  SSE Streaming Event
# ──────────────────────────────────────────────

class SSEEvent(BaseModel):
    """A single reasoning step event streamed via SSE."""

    step: str = Field(description="Step identifier, e.g. 'parsing_query', 'searching_players'")
    detail: str = Field(description="Human-readable detail of what the agent is doing")


# ──────────────────────────────────────────────
#  Data Layer Search Query (from Dev 1)
# ──────────────────────────────────────────────

class SearchQuery(BaseModel):
    """Search query for the data layer POST /search endpoint."""

    position: Optional[str] = None
    max_age: Optional[int] = None
    max_fee: Optional[float] = None
    min_press_score: Optional[float] = None
    contract_expiry_within_months: Optional[int] = None
    preferred_leagues: Optional[list[str]] = None
