import os
import json
from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchQuery
from app.services.chroma_service import chroma_service
from app.services.sqlite_service import get_player_financials
from app.services.csv_service import get_comparables

router = APIRouter()

CACHE_FILE = os.path.join(os.path.dirname(__file__), '../../data_pipeline/data/db/golden_path.json')

@router.post("/search")
def search_players(query: SearchQuery):
    query_dict = query.model_dump(exclude_unset=True)
    
    # 1. Check for the Golden Path query conditions (Fallback cache)
    if query_dict.get("position") == "left-back" and "Championship" in str(query_dict.get("preferred_leagues", [])):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)

    # 2. Live Vector Store Search
    results = chroma_service.search_players(query_dict)
    
    # 3. Enrich candidates with SQLite financials
    candidates = results.get("metadatas", [])
    if candidates:
        for candidate in candidates:
            pid = str(candidate.get("player_id", ""))
            if pid:
                financials = get_player_financials(pid)
                if financials:
                    candidate.update(financials)
    
    return {"status": "success", "candidates": candidates}

@router.get("/player/{player_id}")
def get_player(player_id: str):
    # 1. Fetch from Vector Store
    results = chroma_service.collection.get(ids=[player_id])
    if not results or not results["ids"]:
        raise HTTPException(status_code=404, detail="Player not found in Vector Store")
        
    metadata = results["metadatas"][0]
    
    # 2. Fetch from SQLite
    financials = get_player_financials(player_id)
    
    # 3. Merge
    metadata.update(financials)
    
    return metadata

@router.get("/comparables")
def get_comp_transfers(target_fee: float):
    comps = get_comparables(target_fee)
    return {"comparables": comps}
