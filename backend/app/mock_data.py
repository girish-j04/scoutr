"""
ScoutR Mock Data & Golden Path Cache.

Provides realistic player profiles, comparable transfers, and a pre-computed
golden path result so the system works standalone without Dev 1's API.
"""

from app.schemas import (
    PlayerProfile,
    PressMetrics,
    ComparableTransfer,
    ParsedSearchCriteria,
    PlayerDossier,
    FeeRange,
    ContractRisk,
    QueryResponse,
)

# ──────────────────────────────────────────────
#  Mock Player Database
# ──────────────────────────────────────────────

MOCK_PLAYERS: list[PlayerProfile] = [
    PlayerProfile(
        player_id="p001",
        name="Ramy Bensebaini",
        club="Borussia Mönchengladbach",
        league="Bundesliga",
        age=23,
        position="Left-Back",
        nationality="Algerian",
        contract_expiry_months=8,
        market_value=5.5,
        press_metrics=PressMetrics(ppda=8.2, pressure_success_rate=34.5, defensive_actions_per_90=6.1),
        progressive_carries_per_90=3.8,
        xa_per_90=0.14,
        xg_per_90=0.05,
        minutes_played=2450,
        press_score=78.0,
    ),
    PlayerProfile(
        player_id="p002",
        name="Ian Maatsen",
        club="Burnley",
        league="Championship",
        age=22,
        position="Left-Back",
        nationality="Dutch",
        contract_expiry_months=6,
        market_value=6.0,
        press_metrics=PressMetrics(ppda=7.5, pressure_success_rate=38.2, defensive_actions_per_90=5.8),
        progressive_carries_per_90=4.2,
        xa_per_90=0.18,
        xg_per_90=0.07,
        minutes_played=2680,
        press_score=85.0,
    ),
    PlayerProfile(
        player_id="p003",
        name="Álex Moreno",
        club="Real Betis",
        league="La Liga",
        age=23,
        position="Left-Back",
        nationality="Spanish",
        contract_expiry_months=10,
        market_value=6.5,
        press_metrics=PressMetrics(ppda=9.1, pressure_success_rate=31.0, defensive_actions_per_90=5.2),
        progressive_carries_per_90=3.5,
        xa_per_90=0.12,
        xg_per_90=0.04,
        minutes_played=2100,
        press_score=68.0,
    ),
    PlayerProfile(
        player_id="p004",
        name="Destiny Udogie",
        club="Udinese",
        league="Serie A",
        age=21,
        position="Left-Back",
        nationality="Italian",
        contract_expiry_months=11,
        market_value=5.0,
        press_metrics=PressMetrics(ppda=7.8, pressure_success_rate=36.7, defensive_actions_per_90=6.4),
        progressive_carries_per_90=4.5,
        xa_per_90=0.16,
        xg_per_90=0.08,
        minutes_played=2820,
        press_score=82.0,
    ),
    PlayerProfile(
        player_id="p005",
        name="Sergio Gómez",
        club="Anderlecht",
        league="Belgian Pro League",
        age=22,
        position="Left-Back",
        nationality="Spanish",
        contract_expiry_months=14,
        market_value=4.5,
        press_metrics=PressMetrics(ppda=8.5, pressure_success_rate=33.0, defensive_actions_per_90=5.0),
        progressive_carries_per_90=3.9,
        xa_per_90=0.20,
        xg_per_90=0.06,
        minutes_played=2550,
        press_score=72.0,
    ),
    PlayerProfile(
        player_id="p006",
        name="Nuno Tavares",
        club="Marseille",
        league="Ligue 1",
        age=23,
        position="Left-Back",
        nationality="Portuguese",
        contract_expiry_months=5,
        market_value=5.8,
        press_metrics=PressMetrics(ppda=8.0, pressure_success_rate=35.8, defensive_actions_per_90=5.5),
        progressive_carries_per_90=4.8,
        xa_per_90=0.15,
        xg_per_90=0.09,
        minutes_played=2200,
        press_score=76.0,
    ),
    PlayerProfile(
        player_id="p007",
        name="Luca Pellegrini",
        club="Eintracht Frankfurt",
        league="Bundesliga",
        age=23,
        position="Left-Back",
        nationality="Italian",
        contract_expiry_months=18,
        market_value=7.5,
        press_metrics=PressMetrics(ppda=9.0, pressure_success_rate=30.5, defensive_actions_per_90=4.8),
        progressive_carries_per_90=3.2,
        xa_per_90=0.10,
        xg_per_90=0.03,
        minutes_played=1980,
        press_score=62.0,
    ),
    PlayerProfile(
        player_id="p008",
        name="Antonee Robinson",
        club="Fulham",
        league="Championship",
        age=23,
        position="Left-Back",
        nationality="American",
        contract_expiry_months=9,
        market_value=6.2,
        press_metrics=PressMetrics(ppda=7.2, pressure_success_rate=37.0, defensive_actions_per_90=6.0),
        progressive_carries_per_90=4.0,
        xa_per_90=0.13,
        xg_per_90=0.05,
        minutes_played=2750,
        press_score=80.0,
    ),
]


# ──────────────────────────────────────────────
#  Mock Comparable Transfers
# ──────────────────────────────────────────────

MOCK_COMPARABLES: list[ComparableTransfer] = [
    ComparableTransfer(
        player_name="Tyrick Mitchell",
        from_club="Crystal Palace",
        to_club="Brighton",
        fee_millions=5.0,
        transfer_year=2024,
        age_at_transfer=22,
        position="Left-Back",
    ),
    ComparableTransfer(
        player_name="Rico Henry",
        from_club="Brentford",
        to_club="Aston Villa",
        fee_millions=6.5,
        transfer_year=2024,
        age_at_transfer=23,
        position="Left-Back",
    ),
    ComparableTransfer(
        player_name="Quentin Merlin",
        from_club="Nantes",
        to_club="Marseille",
        fee_millions=4.8,
        transfer_year=2024,
        age_at_transfer=21,
        position="Left-Back",
    ),
    ComparableTransfer(
        player_name="Diogo Dalot",
        from_club="AC Milan",
        to_club="Manchester United",
        fee_millions=7.2,
        transfer_year=2023,
        age_at_transfer=22,
        position="Left-Back",
    ),
    ComparableTransfer(
        player_name="Alex Grimaldo",
        from_club="Benfica",
        to_club="Bayer Leverkusen",
        fee_millions=0.0,
        transfer_year=2023,
        age_at_transfer=23,
        position="Left-Back",
    ),
]


# ──────────────────────────────────────────────
#  Golden Path: Pre-Computed Demo Result
# ──────────────────────────────────────────────

GOLDEN_PATH_CRITERIA = ParsedSearchCriteria(
    position="Left-Back",
    max_age=24,
    max_fee=7.0,
    min_press_score=65.0,
    contract_expiry_within_months=12,
    preferred_leagues=["Championship", "Bundesliga", "Bundesliga 2", "Serie A", "Ligue 1"],
    additional_requirements="Comfortable in a high press, similar intensity to the Championship",
)


def _build_golden_dossier(player: PlayerProfile, rank: int, reason: str, summary: str,
                          fee_low: float, fee_mid: float, fee_high: float,
                          narrative: str, insight: str) -> PlayerDossier:
    """Helper to build a golden path dossier card."""
    return PlayerDossier(
        player=player,
        rank=rank,
        rank_score=round(100 - (rank - 1) * 8, 1),
        ranking_reason=reason,
        scouting_summary=summary,
        fee_range=FeeRange(low_estimate=fee_low, mid_estimate=fee_mid, high_estimate=fee_high),
        contract_risk=ContractRisk.RED if player.contract_expiry_months < 6 else (
            ContractRisk.AMBER if player.contract_expiry_months <= 18 else ContractRisk.GREEN
        ),
        comparable_transfers=MOCK_COMPARABLES[:3],
        valuation_narrative=narrative,
        negotiation_insight=insight,
        tactical_fit_score=85 - (rank - 1) * 5,
        fit_explanation=f"{player.name} profiles strongly as a modern ball-carrying full-back who thrives in high-press systems.",
        heatmap_zones=["left flank", "opposition half", "final third"],
        formation_compatibility="4-3-3 high press",
    )


GOLDEN_PATH_RESPONSE = QueryResponse(
    query="Find me a left-back under 24, comfortable in a high press, contract expiring within 12 months, available for under €7M, preferably from a league with similar intensity to the Championship.",
    parsed_criteria=GOLDEN_PATH_CRITERIA,
    dossiers=[
        _build_golden_dossier(
            MOCK_PLAYERS[1],  # Ian Maatsen
            rank=1,
            reason="Top-ranked due to elite pressing metrics in the Championship itself, 6-month contract creating maximum urgency and negotiation leverage.",
            summary="Ian Maatsen has been one of the Championship's standout left-backs this season, combining aggressive pressing (85 press score) with outstanding progressive carrying. His contract situation at Burnley creates a rare window — expect a fee well below market value or a pre-contract in January.",
            fee_low=3.5, fee_mid=5.0, fee_high=6.0,
            narrative="With only 6 months on his contract, Burnley's leverage is minimal. Comparable left-back transfers in the Championship corridor suggest a €5M fee is realistic, with a pre-contract agreement as the fallback.",
            insight="Open pre-contract talks immediately. Burnley will sell now at a discount rather than lose him for free.",
        ),
        _build_golden_dossier(
            MOCK_PLAYERS[3],  # Destiny Udogie
            rank=2,
            reason="Highest progressive carries per 90 in the pool, elite defensive output, and Serie A's intense pressing style mirrors Championship demands.",
            summary="Destiny Udogie offers the complete modern full-back profile — attacking thrust with 4.5 progressive carries per 90 and a defensive solidity that belies his age. At 21, his upside is enormous. Udinese's selling model means a deal is achievable.",
            fee_low=4.0, fee_mid=5.5, fee_high=6.5,
            narrative="Udinese are a known selling club and Udogie's 11-month remaining deal limits their asking price. Comparable Serie A full-back exports averaged €5.5M at this age/contract stage.",
            insight="Move fast — multiple Premier League clubs are monitoring. Udinese prefer early certainty over auction dynamics.",
        ),
        _build_golden_dossier(
            MOCK_PLAYERS[0],  # Ramy Bensebaini
            rank=3,
            reason="Strong all-round pressing profile from the Bundesliga, well under budget at €5.5M valuation, 8-month contract creates good leverage.",
            summary="Ramy Bensebaini brings Bundesliga-tested pressing ability and positional intelligence. His PPDA numbers show an aggressive defender comfortable playing on the front foot. Gladbach's squad rebuild means they won't block a move.",
            fee_low=3.0, fee_mid=4.5, fee_high=5.5,
            narrative="Gladbach are in a transitional period and willing to cash in on expiring assets. The Bundesliga-to-Championship corridor has produced several value transfers recently.",
            insight="Leverage Gladbach's rebuild narrative — they need the fee to reinvest. Offer a structured deal with add-ons.",
        ),
    ],
    total_candidates_evaluated=8,
)
