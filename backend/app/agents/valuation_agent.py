"""
Valuation Agent.

Estimates transfer fee range using comparable transfers, and classifies
contract risk. Uses Gemini for narrative valuation summaries.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas import (
    RankedCandidate,
    ValuationResult,
    ValuationSummary,
    FeeRange,
    ContractRisk,
    ComparableTransfer,
)
from app.config import get_settings
from app.services.comparables import get_comparables


VALUATION_SYSTEM_PROMPT = """You are a football transfer valuation expert. Given a player's profile, comparable transfers, and estimated fee range, write a valuation assessment.

Your output must contain:
- valuation_narrative: 2-3 sentences explaining how the fee range was derived, referencing comparable transfers and the contract situation
- negotiation_insight: ONE actionable sentence of negotiation advice for the sporting director

Be specific and tactical. Reference actual numbers, club situations, and market dynamics."""


def _classify_contract_risk(months_remaining: int) -> ContractRisk:
    """Classify contract risk based on months remaining."""
    if months_remaining < 6:
        return ContractRisk.RED
    elif months_remaining <= 18:
        return ContractRisk.AMBER
    else:
        return ContractRisk.GREEN


def _estimate_fee_range(
    player_market_value: float,
    contract_months: int,
    comparables: list[ComparableTransfer],
) -> FeeRange:
    """
    Estimate transfer fee range using a regression-style formula.

    Factors:
    - Base: player's listed market value
    - Contract discount: shorter contract → bigger discount
    - Comparable average: anchors the mid estimate
    """
    # Contract discount factor (0.3 for expiring, 1.0 for 24+ months)
    if contract_months <= 3:
        contract_factor = 0.35
    elif contract_months <= 6:
        contract_factor = 0.55
    elif contract_months <= 9:
        contract_factor = 0.70
    elif contract_months <= 12:
        contract_factor = 0.80
    elif contract_months <= 18:
        contract_factor = 0.90
    else:
        contract_factor = 1.0

    # Comparable average
    if comparables:
        comp_fees = [c.fee_millions for c in comparables if c.fee_millions > 0]
        comp_avg = sum(comp_fees) / len(comp_fees) if comp_fees else player_market_value
    else:
        comp_avg = player_market_value

    # Blended mid estimate (60% market value adjusted, 40% comparable average)
    adjusted_value = player_market_value * contract_factor
    mid = adjusted_value * 0.6 + comp_avg * 0.4

    # Low and high as a spread around mid
    low = mid * 0.70
    high = mid * 1.30

    return FeeRange(
        low_estimate=round(low, 1),
        mid_estimate=round(mid, 1),
        high_estimate=round(high, 1),
    )


async def run_valuation_agent(
    candidate: RankedCandidate,
) -> ValuationResult:
    """
    Run the Valuation Agent for a single candidate:
    1. Fetch comparable transfers
    2. Compute fee range using regression formula
    3. Classify contract risk
    4. Generate Gemini-powered valuation narrative
    """
    settings = get_settings()
    player = candidate.player

    # Step 1: Get comparables
    comparables = await get_comparables(
        position=player.position,
        target_fee=player.market_value,
        age=player.age,
    )

    # Step 2: Compute fee range
    fee_range = _estimate_fee_range(
        player_market_value=player.market_value,
        contract_months=player.contract_expiry_months,
        comparables=comparables,
    )

    # Step 3: Contract risk
    contract_risk = _classify_contract_risk(player.contract_expiry_months)

    # Step 4: Gemini valuation narrative
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model_name,
        google_api_key=settings.gemini_api_key,
        temperature=0.3,
    )
    structured_llm = llm.with_structured_output(ValuationSummary)

    comp_text = "\n".join(
        f"  - {c.player_name}: {c.from_club} → {c.to_club}, €{c.fee_millions}M ({c.transfer_year}, age {c.age_at_transfer})"
        for c in comparables
    )

    valuation_summary = await structured_llm.ainvoke(
        [
            ("system", VALUATION_SYSTEM_PROMPT),
            ("human", (
                f"Player: {player.name} ({player.age}, {player.position})\n"
                f"Club: {player.club} ({player.league})\n"
                f"Market value: €{player.market_value}M\n"
                f"Contract remaining: {player.contract_expiry_months} months "
                f"(risk: {contract_risk.value})\n\n"
                f"Estimated fee range: €{fee_range.low_estimate}M - €{fee_range.mid_estimate}M - €{fee_range.high_estimate}M\n\n"
                f"Comparable transfers:\n{comp_text}"
            )),
        ]
    )

    return ValuationResult(
        player_id=player.player_id,
        fee_range=fee_range,
        contract_risk=contract_risk,
        comparable_transfers=comparables,
        valuation_summary=valuation_summary,
    )
