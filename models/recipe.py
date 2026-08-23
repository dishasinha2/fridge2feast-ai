"""Recipe data model."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Recipe:
    id: Optional[int]
    user_id: int
    title: str
    description: str
    cuisine: str
    meal_type: str
    dietary_tags: List[str]
    spice_level: str
    cooking_time_minutes: int
    servings: int
    available_ingredients: List[Dict[str, Any]]
    additional_ingredients: List[Dict[str, Any]]
    instructions: List[str]
    tips: List[str]
    waste_saved_score: int
    created_at: str
    is_saved: bool = False
