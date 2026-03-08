"""
MongoDB Conversation History Service.

Persists every query + dossier response to MongoDB Atlas.
Uses Motor (async MongoDB driver) for non-blocking operations.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings


# ──────────────────────────────────────────────
#  MongoDB Connection
# ──────────────────────────────────────────────

_client: Optional[AsyncIOMotorClient] = None
_db = None


def get_mongo_client():
    """Get or create the MongoDB client singleton."""
    global _client, _db
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongo_uri)
        _db = _client[settings.mongo_db_name]
    return _db


async def close_mongo_client():
    """Close the MongoDB connection."""
    global _client
    if _client:
        _client.close()
        _client = None


# ──────────────────────────────────────────────
#  Conversation CRUD
# ──────────────────────────────────────────────

async def save_conversation(
    query: str,
    parsed_criteria: dict,
    dossiers: list[dict],
    total_candidates_evaluated: int,
) -> str:
    """
    Save a query + response as a conversation record.
    Returns the inserted document ID as a string.
    """
    db = get_mongo_client()
    doc = {
        "query": query,
        "parsed_criteria": parsed_criteria,
        "dossiers": dossiers,
        "total_candidates_evaluated": total_candidates_evaluated,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.conversations.insert_one(doc)
    return str(result.inserted_id)


async def get_conversations(limit: int = 20, skip: int = 0) -> list[dict]:
    """
    Get paginated conversation history, newest first.
    Returns lightweight summaries (no full dossier payloads).
    """
    db = get_mongo_client()
    cursor = db.conversations.find(
        {},
        {
            "_id": 1,
            "query": 1,
            "parsed_criteria.position": 1,
            "total_candidates_evaluated": 1,
            "created_at": 1,
            "dossiers": {"$slice": 0},  # Exclude dossiers from list view
        },
    ).sort("created_at", -1).skip(skip).limit(limit)

    results = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        results.append(doc)
    return results


async def get_conversation(conversation_id: str) -> Optional[dict]:
    """Get a single conversation by ID with full dossier data."""
    db = get_mongo_client()
    try:
        doc = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
    except Exception:
        return None

    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation by ID. Returns True if deleted."""
    db = get_mongo_client()
    try:
        result = await db.conversations.delete_one({"_id": ObjectId(conversation_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def count_conversations() -> int:
    """Get total number of stored conversations."""
    db = get_mongo_client()
    return await db.conversations.count_documents({})


async def find_by_criteria(parsed_criteria: dict) -> Optional[dict]:
    """
    Find the most recent conversation that matches the given parsed criteria.
    This allows cached results to survive server restarts.

    Matches on position, max_age, max_fee, min_press_score, etc.
    """
    db = get_mongo_client()

    # Build a query matching non-None criteria fields
    match_query = {}
    for key, value in parsed_criteria.items():
        if value is not None:
            match_query[f"parsed_criteria.{key}"] = value

    if not match_query:
        return None

    # Find the most recent matching conversation
    doc = await db.conversations.find_one(
        match_query,
        sort=[("created_at", -1)],
    )

    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc
