"""
Query Parser Agent.

Uses Gemini with Pydantic structured output to parse a sporting director's
natural language query into structured search criteria.
"""

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


async def parse_query(query: str) -> ParsedSearchCriteria:
    """
    Parse a natural language sporting director query into structured search criteria.
    Uses Gemini's native structured output with Pydantic schema.
    """
    settings = get_settings()

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model_name,
        google_api_key=settings.gemini_api_key,
        temperature=0.1,  # Low temperature for precise extraction
    )

    # Use with_structured_output — Gemini enforces the schema natively
    structured_llm = llm.with_structured_output(ParsedSearchCriteria)

    result = await structured_llm.ainvoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", f"Parse this transfer request into search criteria:\n\n{query}"),
        ]
    )

    return result
