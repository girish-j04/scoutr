"""
Response Cache Service.

Two-tier caching:
1. Raw text cache  — instant hit for identical queries (normalized by case/whitespace)
2. Criteria cache  — hit for semantically equivalent queries that parse to the same criteria
   (e.g. "left-back under 25" and "I need a left back younger than 25" both parse to
    {position: "Left-Back", max_age: 25} → same cache key)
"""

import json
import re
import time
from typing import Optional


# ──────────────────────────────────────────────
#  Cache Storage
# ──────────────────────────────────────────────

# { normalized_raw_query: (response_dict, timestamp) }
_text_cache: dict[str, tuple[dict, float]] = {}

# { criteria_key: (response_dict, timestamp) }
_criteria_cache: dict[str, tuple[dict, float]] = {}


# ──────────────────────────────────────────────
#  Key Generation
# ──────────────────────────────────────────────

def _normalize_query(query: str) -> str:
    """Normalize raw query text for exact-match cache."""
    q = query.lower().strip()
    q = re.sub(r'\s+', ' ', q)
    q = q.rstrip('.,!?;:')
    return q


def criteria_key(parsed_criteria: dict) -> str:
    """
    Generate a canonical cache key from parsed search criteria.
    Sorts keys and values so ordering doesn't matter.
    """
    # Only include non-None fields
    filtered = {}
    for k, v in sorted(parsed_criteria.items()):
        if v is None:
            continue
        if isinstance(v, list):
            filtered[k] = sorted([str(x).lower() for x in v])
        elif isinstance(v, str):
            filtered[k] = v.lower().strip()
        else:
            filtered[k] = v
    return json.dumps(filtered, sort_keys=True)


# ──────────────────────────────────────────────
#  Cache Operations
# ──────────────────────────────────────────────

def get_cached_response(query: str, ttl_seconds: int = 600) -> Optional[dict]:
    """
    Tier 1: Check raw text cache for an exact (normalized) match.
    Returns cached response dict or None.
    """
    key = _normalize_query(query)
    entry = _text_cache.get(key)
    if entry is None:
        return None

    response, cached_at = entry
    if time.time() - cached_at > ttl_seconds:
        del _text_cache[key]
        return None

    return response


def get_cached_by_criteria(parsed_criteria: dict, ttl_seconds: int = 600) -> Optional[dict]:
    """
    Tier 2: Check criteria cache for a semantically equivalent match.
    Call this after the query parser has run.
    Returns cached response dict or None.
    """
    key = criteria_key(parsed_criteria)
    entry = _criteria_cache.get(key)
    if entry is None:
        return None

    response, cached_at = entry
    if time.time() - cached_at > ttl_seconds:
        del _criteria_cache[key]
        return None

    return response


def cache_response(query: str, parsed_criteria: dict, response: dict) -> None:
    """
    Store response in both caches (raw text + criteria).
    """
    now = time.time()
    _text_cache[_normalize_query(query)] = (response, now)
    _criteria_cache[criteria_key(parsed_criteria)] = (response, now)


def clear_cache() -> int:
    """Clear all caches. Returns total entries removed."""
    count = len(_text_cache) + len(_criteria_cache)
    _text_cache.clear()
    _criteria_cache.clear()
    return count


def cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "text_cache_entries": len(_text_cache),
        "criteria_cache_entries": len(_criteria_cache),
    }
