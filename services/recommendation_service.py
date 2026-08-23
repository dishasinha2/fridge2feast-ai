"""Recommendation Engine for Fridge2Feast AI."""
import random
from typing import List, Dict, Any
from services.kitchen_service import get_user_ingredients, get_expiring_ingredients
from services.recipe_service import get_saved_recipes, get_cooking_history

def get_personalized_recommendations(user_id: int, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce structured dynamic recommendations derived strictly from user's actual inventory,
    urgency of expiring ingredients, and logged preferences.
    """
    if not user_id:
        return {"rescue_ideas": [], "cuisine_focus": "", "discovery_prompt": ""}

    expiring = get_expiring_ingredients(user_id)
    all_ingredients = get_user_ingredients(user_id)
    saved = get_saved_recipes(user_id)
    history = get_cooking_history(user_id)

    preferred_cuisines = user_preferences.get("cuisines", ["Italian", "Indian", "Mexican"])
    dietary = user_preferences.get("dietary", ["Vegetarian"])

    rescue_ideas = []
    if expiring:
        # Highlight specific combinations from expiring items
        exp_names = [item.name for item in expiring[:4]]
        if len(exp_names) >= 2:
            rescue_ideas.append(f"Rescue Bowl: Sauté {exp_names[0]} and {exp_names[1]} with olive oil and favorite herbs.")
        elif len(exp_names) == 1:
            rescue_ideas.append(f"Quick Hero: Feature {exp_names[0]} as the centerpiece before it expires.")
        
        rescue_ideas.append(f"Zero-Waste Broth: Simmer remaining vegetable trimmings for a flavorful soup base.")
    elif all_ingredients:
        names = [item.name for item in all_ingredients[:3]]
        rescue_ideas.append(f"Fresh creation: Combine {', '.join(names)} for a balanced {preferred_cuisines[0] if preferred_cuisines else 'home-cooked'} meal.")

    # Discovery inspiration
    discovery_cuisines = [c for c in ["Mediterranean", "Asian Stir-Fry", "Rustic Mexican", "Hearty Indian", "Classic Italian", "French Bistro"] if c not in preferred_cuisines]
    discovery_cuisine = random.choice(discovery_cuisines) if discovery_cuisines else "Mediterranean"

    return {
        "expiring_count": len(expiring),
        "rescue_ideas": rescue_ideas,
        "recommended_cuisine": preferred_cuisines[0] if preferred_cuisines else "Italian",
        "discovery_cuisine": discovery_cuisine,
        "has_inventory": len(all_ingredients) > 0
    }
