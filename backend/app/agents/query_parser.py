"""
Query Parser Agent.

Uses Gemini with Pydantic structured output to parse a sporting director's
natural language query into structured search criteria.
Supports follow-up queries by merging with previous context when provided.
"""

import json
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas import ParsedSearchCriteria
from app.config import get_settings


SYSTEM_PROMPT = """You are a football transfer intelligence system. Your job is to parse a sporting director's natural language transfer request into structured search criteria.

Key rules:
- Position should be normalized (e.g. "left-back" → "Left-Back", "CB" → "Centre-Back")
- Max fee should be in millions EUR
- Press score ranges from 0-100 (higher = more aggressive pressing)
- Preferred leagues should be full league names
- If the query mentions "high press" or "pressing intensity", set min_press_score to at least 65
- If the query mentions "similar intensity to the Championship", include neighboring leagues like Bundesliga, Serie A, Ligue 1 as preferred leagues
- Extract contract expiry requirements carefully (e.g. "expiring within 12 months" → 12)
"""


FOLLOWUP_SYSTEM_PROMPT = """You are a football transfer intelligence system. The user is making a FOLLOW-UP request.

PREVIOUS query: "{previous_query}"
PREVIOUS parsed criteria: {previous_criteria}

CURRENT follow-up: "{query}"

Your job: Merge/refine the criteria. ONLY change what the user explicitly asks to change.
- Keep all previous criteria values that are not mentioned in the follow-up
- Update only the fields the user modifies (e.g. "under 24" → max_age=24, "€5M" → max_fee=5)
- If the follow-up is vague, prefer keeping previous values over inventing new ones
- Output the complete merged criteria (all fields), not a delta
"""


async def parse_query(
    query: str,
    previous_query: Optional[str] = None,
    previous_criteria: Optional[dict] = None,
) -> ParsedSearchCriteria:
    """
    Parse a natural language sporting director query into structured search criteria.
    When previous_query and previous_criteria are provided, merges the follow-up
    with the previous context (e.g. "give me under 24" after "left back under 27").
    """
    settings = get_settings()

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model_name,
        google_api_key=settings.gemini_api_key,
        temperature=0.1,  # Low temperature for precise extraction
    )

    structured_llm = llm.with_structured_output(ParsedSearchCriteria)

    if previous_query and previous_criteria:
        # Sanitize: ensure dict is JSON-serializable (MongoDB may return BSON types)
        try:
            clean = {k: v for k, v in previous_criteria.items() if v is not None}
            criteria_str = json.dumps(clean, indent=2, default=str)
        except (TypeError, ValueError):
            criteria_str = str(previous_criteria)
        system = FOLLOWUP_SYSTEM_PROMPT.format(
            previous_query=previous_query,
            previous_criteria=criteria_str,
            query=query,
        )
        human = f"Output the merged criteria for this follow-up:\n\n{query}"
    else:
        system = SYSTEM_PROMPT
        human = f"Parse this transfer request into search criteria:\n\n{query}"

    result = await structured_llm.ainvoke(
        [
            ("system", system),
            ("human", human),
        ]
    )

    return result
