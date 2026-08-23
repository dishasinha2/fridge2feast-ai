"""Ingredient data model."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Ingredient:
    id: Optional[int]
    user_id: int
    name: str
    category: str
    quantity: float
    unit: str
    freshness_status: str
    estimated_shelf_life_days: int
    storage_advice: str
    confidence: float
    added_date: str
    expiry_date: str
    days_remaining: int = 0
