from pydantic import BaseModel
from typing import Optional, List

class PlayerSchema(BaseModel):
    player_id: int
    name: str
    club: str
    league: str
    age: int
    position: str
    contract_expiry: Optional[str] = None
    market_value: Optional[float] = None
    ppda: Optional[float] = None
    pressure_success_rate: Optional[float] = None
    progressive_carries: Optional[int] = None
    xA: Optional[float] = None
    xG: Optional[float] = None

class SearchQuery(BaseModel):
    position: Optional[str] = None
    max_age: Optional[int] = None
    max_fee: Optional[float] = None
    min_press_score: Optional[float] = None
    contract_expiry_within_months: Optional[int] = None
    preferred_leagues: Optional[List[str]] = None
