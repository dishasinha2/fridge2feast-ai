"""Transparent, user-scoped recommendation ranking for Fridge2Feast."""
from collections import Counter
from typing import Any, Dict, List, Optional

from services.kitchen_service import get_user_ingredients
from services.recipe_service import get_cooking_history, get_saved_recipes


def _list(value: Any) -> List[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _is_diet_compatible(recipe: Any, diet: str) -> bool:
    """Apply only explicit dietary tags; unknown recipes are never claimed compatible."""
    if not diet or diet == "No Preference":
        return True
    return diet.lower() in {str(tag).lower() for tag in getattr(recipe, "dietary_tags", [])}


def _history_affinity(saved: List[Any], history: List[Dict[str, Any]]) -> Dict[str, Counter]:
    """Require two signals before history changes a recommendation."""
    cuisines = Counter(recipe.cuisine for recipe in saved if recipe.cuisine)
    cuisines.update(row.get("cuisine") for row in history if row.get("cuisine"))
    meals = Counter(recipe.meal_type for recipe in saved if recipe.meal_type)
    return {
        "cuisines": Counter({key: count for key, count in cuisines.items() if count >= 2}),
        "meals": Counter({key: count for key, count in meals.items() if count >= 2}),
    }


def get_personalized_recommendations(
    user_id: int,
    user_preferences: Optional[Dict[str, Any]] = None,
    explicit_preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Rank only this user's saved recipes and current kitchen context locally."""
    empty = {
        "expiring_count": 0, "rescue_ideas": [], "recommended_cuisine": "",
        "discovery_cuisine": "", "has_inventory": False, "ranked_recipes": [],
        "history_personalization_available": False,
    }
    if not user_id:
        return empty

    stored = user_preferences or {}
    requested = explicit_preferences or {}
    ingredients = get_user_ingredients(user_id, sort_by="freshness")
    saved = get_saved_recipes(user_id)
    history = get_cooking_history(user_id)
    if not ingredients:
        return empty

    diet = str(requested.get("diet", "") or (_list(stored.get("dietary")) or [""])[0])
    cuisine = str(requested.get("cuisine", "") or (_list(stored.get("cuisines")) or [""])[0])
    meal_type = str(requested.get("meal_type", ""))
    max_time = requested.get("cooking_time_minutes")
    servings = requested.get("servings")
    preferred_cuisines = set(_list(stored.get("cuisines")))
    affinity = _history_affinity(saved, history)

    freshness_score = {"USE TODAY": 30, "USE SOON": 20, "FRESH": 10}
    kitchen_names = {item.name.strip().lower(): item for item in ingredients}
    urgent = sorted(
        (item for item in ingredients if item.days_remaining <= 2),
        key=lambda item: (item.days_remaining, item.name.lower()),
    )
    rescue_ideas = [
        f"Use {item.name} {('today' if item.freshness_status == 'USE TODAY' else 'soon')} — it is a priority ingredient in your kitchen."
        for item in urgent[:3]
    ] or [f"Start with {ingredients[0].name}, which is currently available in your kitchen."]

    ranked = []
    for recipe in saved:
        if not _is_diet_compatible(recipe, diet):
            continue
        available = [item for item in recipe.available_ingredients if isinstance(item, dict)]
        matched = [item for item in available if str(item.get("name", "")).strip().lower() in kitchen_names]
        score = len(matched) * 25 + sum(
            freshness_score.get(kitchen_names[str(item.get("name", "")).strip().lower()].freshness_status, 0)
            for item in matched
        )
        reasons = []
        if matched:
            reasons.append(f"uses {len(matched)} ingredient{'s' if len(matched) != 1 else ''} from your kitchen")
        if any(kitchen_names[str(item.get("name", "")).strip().lower()].days_remaining <= 2 for item in matched):
            reasons.append("prioritizes an ingredient that needs using soon")
        if cuisine and recipe.cuisine == cuisine:
            score += 20
            reasons.append(f"matches your {cuisine} preference")
        elif recipe.cuisine in preferred_cuisines:
            score += 10
            reasons.append(f"matches your saved {recipe.cuisine} preference")
        if meal_type and recipe.meal_type == meal_type:
            score += 15
            reasons.append(f"fits your {meal_type} meal")
        if isinstance(max_time, int) and recipe.cooking_time_minutes <= max_time:
            score += 10
            reasons.append(f"fits your {max_time}-minute limit")
        if isinstance(servings, int) and recipe.servings == servings:
            score += 5
        if affinity["cuisines"].get(recipe.cuisine, 0):
            score += 12
            reasons.append("aligns with a repeated cooking or saving pattern")
        explanation = "Recommended because it " + "; ".join(reasons) + "." if reasons else "Saved recipe with no current kitchen match."
        ranked.append({"recipe": recipe, "score": score, "explanation": explanation})

    ranked.sort(key=lambda item: (-item["score"], item["recipe"].title.lower()))
    recommended_cuisine = cuisine if cuisine and cuisine != "Any Cuisine" else (next(iter(affinity["cuisines"]), ""))
    return {
        "expiring_count": len(urgent), "rescue_ideas": rescue_ideas,
        "recommended_cuisine": recommended_cuisine, "discovery_cuisine": "",
        "has_inventory": True, "ranked_recipes": ranked,
        "history_personalization_available": bool(affinity["cuisines"] or affinity["meals"]),
    }
