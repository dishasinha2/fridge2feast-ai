import json
import time
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ValidationError
from google.genai import types
from services.gemini_client import invoke_gemini_with_retry, GeminiServiceException, _record_telemetry_event
from utils.validation import validate_preferences
from prompts.recipe_generation import (
    RECIPE_GENERATOR_SYSTEM_INSTRUCTION,
    build_recipe_generation_prompt,
)

# Pydantic schema for recipe output validation
class RecipeIngredientSchema(BaseModel):
    name: str = Field(description="Ingredient name")
    quantity: str = Field(description="Quantity required")
    isAvailable: bool = Field(description="True if ingredient is available in user's fridge")

class MissingIngredientSchema(BaseModel):
    name: str = Field(description="Missing ingredient name")
    estimated_quantity: str = Field(description="Estimated quantity needed to buy")
    estimated_price_inr: float = Field(description="Estimated cost in Indian Rupees (INR)")

class NutritionEstimateSchema(BaseModel):
    calories: int = Field(description="Total calories")
    protein_g: int = Field(description="Protein in grams")
    carbs_g: int = Field(description="Carbohydrates in grams")
    fat_g: int = Field(description="Fat in grams")
    fiber_g: int = Field(description="Fiber in grams")

class SubstitutionSchema(BaseModel):
    original: str = Field(description="Original ingredient")
    substitute: str = Field(description="Possible replacement")
    note: str = Field(description="Usage tip")

class RecipeSchema(BaseModel):
    badge: Literal["Best Match", "Quick Feast", "Creative Pick"]
    title: str = Field(description="Dish name")
    short_description: str = Field(description="Appealing summary")
    cuisine: str = Field(description="Cuisine type")
    difficulty: str = Field(description="Easy, Medium, or Advanced")
    cooking_time_minutes: int = Field(description="Total cooking time in minutes")
    servings: int = Field(description="Number of servings")
    ingredient_utilization_percentage: float = Field(description="Percentage of available ingredients utilized (0-100)")
    ingredients_available: List[RecipeIngredientSchema] = Field(default_factory=list)
    ingredients_missing: List[MissingIngredientSchema] = Field(default_factory=list)
    estimated_missing_cost_inr: float = Field(description="Total estimated extra cost in INR")
    nutrition_estimate: NutritionEstimateSchema
    preparation_steps: List[str] = Field(min_length=1)
    cooking_tips: List[str] = Field(default_factory=list)
    substitutions: List[SubstitutionSchema] = Field(default_factory=list)
    food_waste_note: str = Field(description="Explanation of zero-waste impact")

class RecipeResponseContainerSchema(BaseModel):
    recipes: List[RecipeSchema] = Field(min_length=3, max_length=3, description="List of exactly 3 recipes")

def generate_recipes(confirmed_ingredients: list, preferences: Optional[dict] = None) -> list:
    """
    Calls Gemini API via centralized client to generate exactly 3 custom recipes.
    Validates output strictly through Pydantic.
    """
    active_ingredients = [i for i in (confirmed_ingredients or []) if i.get("included", True)]
    if not active_ingredients:
        raise GeminiServiceException("No confirmed ingredients available to generate recipes. Please select or add ingredients first.", is_transient=False)

    prefs = preferences or {}
    is_valid, validation_errors = validate_preferences(prefs)
    if not is_valid:
        raise GeminiServiceException(f"Invalid preference configuration: {'; '.join(validation_errors)}", error_code=400, is_transient=False, error_category="VALIDATION_ERROR")

    # Safe normalization of preferences
    normalized_prefs = {
        "diet": prefs.get("diet") or "No Preference",
        "cuisine": prefs.get("cuisine") or "Fusion",
        "cookingTime": prefs.get("cookingTime") or "Under 30 minutes",
        "difficulty": prefs.get("difficulty") or "Medium",
        "servings": int(prefs.get("servings")) if prefs.get("servings") is not None and int(prefs.get("servings")) > 0 else 2,
        "spiceLevel": str(prefs.get("spiceLevel")) if prefs.get("spiceLevel") is not None else "Medium",
        "budgetINR": float(prefs.get("budgetINR")) if prefs.get("budgetINR") is not None and float(prefs.get("budgetINR")) >= 0 else 300.0,
        "dietaryRestrictions": prefs.get("dietaryRestrictions") if isinstance(prefs.get("dietaryRestrictions"), list) else [],
        "craving": prefs.get("craving") or "Spicy",
        "meal_type": prefs.get("meal_type") or prefs.get("meal_occasion") or "Dinner",
        "avoid_list": prefs.get("avoid_list") if isinstance(prefs.get("avoid_list"), list) else [],
    }

    prompt_text = build_recipe_generation_prompt(active_ingredients, normalized_prefs)

    response_text = invoke_gemini_with_retry(
        contents=prompt_text,
        system_instruction=RECIPE_GENERATOR_SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=RecipeResponseContainerSchema,
        temperature=0.4,
        operation_name="recipe_generation",
    )

    try:
        parsed = json.loads(response_text)
        validated_container = RecipeResponseContainerSchema(**parsed)
        parsed = validated_container.model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        _record_telemetry_event(success=False, latency_ms=0, validation_error=True)
        raise GeminiServiceException(
            "The AI response could not be validated against the culinary schema. Please try generating again.",
            error_code=422,
            is_transient=False,
            error_category="VALIDATION_ERROR",
            technical_details=str(e)[:200],
        )

    recipes_list = []
    raw_recipes = parsed.get("recipes", [])
    if len(raw_recipes) != 3:
        raise GeminiServiceException("Three validated recipes were not returned. Please try generating again.", is_transient=False)

    badges = ["Best Match", "Quick Feast", "Creative Pick"]
    for idx, r in enumerate(raw_recipes):
        badge = r["badge"]
        recipes_list.append({
            "id": f"recipe-{int(time.time())}-{idx}",
            "badge": badge,
            "title": r["title"],
            "short_description": r["short_description"],
            "cuisine": r["cuisine"],
            "difficulty": r["difficulty"],
            "cooking_time_minutes": r["cooking_time_minutes"],
            "servings": r["servings"],
            "ingredient_utilization_percentage": r["ingredient_utilization_percentage"],
            "ingredients_available": r["ingredients_available"],
            "ingredients_missing": r["ingredients_missing"],
            "estimated_missing_cost_inr": r["estimated_missing_cost_inr"],
            "nutrition_estimate": r["nutrition_estimate"],
            "preparation_steps": r["preparation_steps"],
            "cooking_tips": r["cooking_tips"],
            "substitutions": r["substitutions"],
            "food_waste_note": r["food_waste_note"],
        })

    return recipes_list
