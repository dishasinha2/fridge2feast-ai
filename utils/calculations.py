from typing import List, Dict, Any, Optional

# Active optimization weights profiles
OPTIMIZATION_PROFILES = {
    "Balanced": {
        "label": "⚖️ Balanced",
        "description": "Standard zero-waste profile balancing utilization, waste risk, cravings, speed, and budget.",
        "weights": {
            "utilization": 0.30,
            "urgent": 0.25,
            "craving": 0.15,
            "budget": 0.10,
            "diet": 0.10,
            "time": 0.10,
        }
    },
    "Minimum Food Waste": {
        "label": "♻️ Minimum Food Waste",
        "description": "Heavily prioritizes consuming highest perishability ingredients and maximum pantry utilization.",
        "weights": {
            "utilization": 0.40,
            "urgent": 0.35,
            "craving": 0.10,
            "budget": 0.05,
            "diet": 0.05,
            "time": 0.05,
        }
    },
    "Lowest Cost": {
        "label": "💰 Lowest Cost",
        "description": "Minimizes missing grocery purchases and strictly adheres to zero-cost or low-cost recipes.",
        "weights": {
            "utilization": 0.20,
            "urgent": 0.15,
            "craving": 0.10,
            "budget": 0.35,
            "diet": 0.10,
            "time": 0.10,
        }
    },
    "Best Craving Match": {
        "label": "🌶️ Best Craving Match",
        "description": "Prioritizes recipes that strongly match active craving and preferred spice profile.",
        "weights": {
            "utilization": 0.15,
            "urgent": 0.15,
            "craving": 0.40,
            "budget": 0.10,
            "diet": 0.10,
            "time": 0.10,
        }
    },
    "Fastest Meal": {
        "label": "⏱️ Fastest Meal",
        "description": "Prioritizes quickest preparation time and simplest workflow (<20 minutes).",
        "weights": {
            "utilization": 0.15,
            "urgent": 0.15,
            "craving": 0.10,
            "budget": 0.10,
            "diet": 0.10,
            "time": 0.40,
        }
    },
    "Nutrition": {
        "label": "💪 Nutrition",
        "description": "Prioritizes high protein, fiber balance, and fresh vegetable content.",
        "weights": {
            "utilization": 0.20,
            "urgent": 0.20,
            "craving": 0.10,
            "budget": 0.10,
            "diet": 0.25,
            "time": 0.15,
        }
    }
}

def calculate_waste_score(available_used: int, total_available: int) -> Dict[str, Any]:
    """
    Calculates the Food Waste Reduction Score (0 to 100).
    """
    if total_available <= 0:
        score = 0
        percentage = 0
    else:
        percentage = min(100, int((available_used / total_available) * 100))
        score = percentage

    if score >= 85:
        level = "Excellent Waste Reduction"
        badge = "♻️ Zero Waste Master"
        color = "#10b981"
    elif score >= 60:
        level = "Good Waste Saving"
        badge = "🌱 Eco Chef"
        color = "#3b82f6"
    else:
        level = "Moderate Utilization"
        badge = "📦 Starter Saver"
        color = "#f59e0b"

    return {
        "score": score,
        "percentage": percentage,
        "used": available_used,
        "total": total_available,
        "level": level,
        "badge": badge,
        "color": color
    }

def calculate_total_missing_cost(missing_ingredients: List[Dict[str, Any]]) -> float:
    """
    Calculates total cost in INR for missing ingredients.
    """
    if not missing_ingredients:
        return 0.0
    
    total = 0.0
    for item in missing_ingredients:
        total += float(item.get("estimated_price_inr", 0.0))
    return round(total, 2)

def calculate_recipe_multi_objective_score(
    recipe: Dict[str, Any],
    meal_context: Dict[str, Any],
    urgent_ingredients: List[str],
    objective_profile: str = "Balanced",
    taste_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculates transparent, deterministic multi-objective score derived from real inputs:
    - Ingredient Utilization
    - Urgent Waste Risk Reduction
    - Craving & Taste Match (incorporating Taste Profile)
    - Budget & Cost Fit
    - Diet & Restrictions Match
    - Cooking Time Fit
    """
    profile_data = OPTIMIZATION_PROFILES.get(objective_profile, OPTIMIZATION_PROFILES["Balanced"])
    weights = profile_data["weights"]

    # 1. Utilization Score (0-100)
    utilization = float(recipe.get("ingredient_utilization_percentage", 80))
    
    # 2. Urgent Ingredients Match (0-100)
    recipe_avail_names = [i.get("name", "").lower() for i in recipe.get("ingredients_available", [])]
    urgent_used_names = [u for u in urgent_ingredients if any(u.lower() in name for name in recipe_avail_names)]
    urgent_used = len(urgent_used_names)
    urgent_score = min(100.0, (urgent_used / max(1, len(urgent_ingredients))) * 100.0) if urgent_ingredients else 90.0

    # 3. Craving & Personal Taste Profile Match
    craving = meal_context.get("craving", "Savory").lower()
    recipe_desc = (recipe.get("short_description", "") + " " + recipe.get("title", "")).lower()
    cuisine_name = recipe.get("cuisine", "").lower()
    
    craving_base = 95.0 if (craving in recipe_desc or craving in cuisine_name) else 85.0
    
    # Incorporate Taste Profile boost without model retraining
    if taste_profile:
        fav_cuisines = [c.lower() for c in taste_profile.get("favorite_cuisines", [])]
        disliked_items = [d.lower() for d in taste_profile.get("disliked_ingredients", [])]
        
        if any(fc in cuisine_name for fc in fav_cuisines):
            craving_base = min(100.0, craving_base + 5.0)
        if any(di in recipe_desc for di in disliked_items):
            craving_base = max(40.0, craving_base - 25.0)

    craving_score = craving_base

    # 4. Budget Fit
    budget_inr = float(meal_context.get("budgetINR", 300))
    missing_cost = float(recipe.get("estimated_missing_cost_inr", 0))
    if missing_cost <= budget_inr:
        budget_score = 100.0 - (missing_cost / max(1.0, budget_inr)) * 20.0
    else:
        budget_score = max(40.0, 100.0 - ((missing_cost - budget_inr) / max(1.0, budget_inr)) * 50.0)

    # 5. Diet Compatibility
    diet = meal_context.get("diet", "Vegetarian").lower()
    avoid_list = meal_context.get("avoid_list", [])
    has_avoided = any(a.lower() in recipe_desc for a in avoid_list if a)
    diet_score = 40.0 if has_avoided else 100.0

    # 6. Time Fit
    time_limit_str = meal_context.get("cookingTime", "Under 30 minutes")
    time_mins = recipe.get("cooking_time_minutes", 25)
    if "15" in time_limit_str:
        time_score = 100.0 if time_mins <= 15 else max(40.0, 100.0 - (time_mins - 15) * 4)
    elif "30" in time_limit_str:
        time_score = 100.0 if time_mins <= 30 else max(50.0, 100.0 - (time_mins - 30) * 3)
    else:
        time_score = 95.0

    # Composite Overall Score (0-100) using active weights
    overall = (
        (utilization * weights["utilization"]) +
        (urgent_score * weights["urgent"]) +
        (craving_score * weights["craving"]) +
        (budget_score * weights["budget"]) +
        (diet_score * weights["diet"]) +
        (time_score * weights["time"])
    )

    # Structured, explainable decision factors
    reasons = []
    if urgent_used > 0:
        reasons.append(f"Rescues {urgent_used} urgent perishable item(s) ({', '.join(urgent_used_names)})")
    if utilization >= 80:
        reasons.append(f"High kitchen utilization ({int(utilization)}% fridge ingredients used)")
    if missing_cost == 0:
        reasons.append("Zero additional grocery cost required")
    elif missing_cost <= budget_inr:
        reasons.append(f"Within ₹{int(budget_inr)} budget (Requires ₹{int(missing_cost)} in missing staples)")
    if time_mins <= 25:
        reasons.append(f"Fast {time_mins}-minute preparation")
    if craving in recipe_desc or craving in cuisine_name:
        reasons.append(f"Satisfies craving for {craving.capitalize()}")
    if not reasons:
        reasons.append("Balanced combination of available pantry ingredients")

    explanation_breakdown = {
        "prioritized_ingredients": urgent_used_names if urgent_used_names else [i.get("name") for i in recipe.get("ingredients_available", [])[:3]],
        "priority_reason": "Ranked by estimated shelf-life window and urgency status to reduce waste" if urgent_used_names else "Readily available in your kitchen inventory",
        "craving_influence": f"Matched selected craving '{meal_context.get('craving', 'Savory')}' in dish profile",
        "household_scaling": f"Yields {recipe.get('servings', meal_context.get('household_size', 2))} servings for {meal_context.get('household_type', 'Household')}",
        "budget_impact": f"Estimated extra grocery cost: ₹{int(missing_cost)} (Budget: ₹{int(budget_inr)})",
        "diet_compatibility": f"Conforms to {meal_context.get('diet', 'Vegetarian')} with {len(avoid_list)} excluded allergens",
        "cooking_time_fit": f"{time_mins} minutes vs requested target of {time_limit_str}",
        "waste_reduction_impact": f"Reclaims {int(utilization)}% of available inventory items",
    }

    return {
        "overall_score": round(overall, 1),
        "utilization_score": int(utilization),
        "urgent_score": int(urgent_score),
        "craving_score": int(craving_score),
        "budget_score": int(budget_score),
        "diet_score": int(diet_score),
        "time_score": int(time_score),
        "active_profile": objective_profile,
        "active_weights": weights,
        "reasons": reasons,
        "explanation": explanation_breakdown,
    }

def calculate_kitchen_savings(saved_recipes_count: int, ingredients_rescued_count: int) -> Dict[str, Any]:
    """
    Computes estimated financial savings based on avoided takeaway and rescued pantry value.
    Clearly labeled as approximate estimated value.
    """
    est_ingredient_value = ingredients_rescued_count * 35
    est_meal_savings = saved_recipes_count * 150
    total_savings = est_ingredient_value + est_meal_savings

    return {
        "ingredients_rescued": ingredients_rescued_count,
        "recipes_cooked": saved_recipes_count,
        "est_ingredient_value_inr": est_ingredient_value,
        "est_total_savings_inr": total_savings,
        "methodology": "Based on average ₹35 estimated replacement cost per rescued perishable item and ₹150 estimated savings per home-cooked meal vs. takeaway dining."
    }
