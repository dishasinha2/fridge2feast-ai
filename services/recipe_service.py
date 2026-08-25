"""Recipe Generation and Management Service for Fridge2Feast AI."""
import json
import re
import logging
from collections import Counter
from typing import List, Dict, Any, Optional, Tuple
from utils.database import get_db_connection
from services.kitchen_service import get_user_ingredients, get_expiring_ingredients
from services.gemini_client import generate_json_content, get_gemini_client
from models.recipe import Recipe

logger = logging.getLogger(__name__)

RECIPE_PROMPT_TEMPLATE = """
You are Fridge2Feast AI. Create one practical, zero-waste recipe.

USER INVENTORY (ACTUAL INGREDIENTS IN USER'S KITCHEN):
{inventory_text}

EXPIRING INGREDIENTS REQUIRING IMMEDIATE RESCUE:
{expiring_text}

USER PREFERENCES & PARAMETERS:
- Requested Servings: {servings}
- Meal Type: {meal_type}
- Target Cuisine: {cuisine}
- Dietary Preference: {diet}
- Preferred Spice Level: {spice_level}
- Target Cooking Time: {cooking_time_minutes} minutes
- Additional User Request/Notes: {custom_prompt}
- Latest confirmed scan (use this context alongside the complete inventory): {latest_scan_text}
- Relevant, anonymous cooking context: {history_text}

RULES: Prioritize using the EXPIRING ingredients. "available_ingredients"
(From Your Kitchen) must only contain inventory items. "additional_ingredients"
(You May Need) may only contain minimal pantry staples. Respect the diet. Keep
instructions to 3-6 concise steps and tips to 1-2 concise items.

Return only JSON with these fields: title, description, cuisine, meal_type,
dietary_tags, spice_level, cooking_time_minutes, servings,
available_ingredients, additional_ingredients, instructions, tips,
waste_saved_score. Each ingredient object needs name, quantity, and unit.
"""


def _parse_recipe_payload(raw_text: str) -> Dict[str, Any]:
    """Validate untrusted Gemini JSON before it is displayed or persisted."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned).strip()
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("Recipe response must be a JSON object")

    title = data.get("title")
    steps = data.get("instructions")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Recipe response is missing title")
    if not isinstance(steps, list) or not steps or not all(isinstance(step, str) and step.strip() for step in steps):
        raise ValueError("Recipe response has invalid instructions")
    for field in ("available_ingredients", "additional_ingredients"):
        value = data.get(field)
        if not isinstance(value, list) or not all(isinstance(item, dict) and str(item.get("name", "")).strip() for item in value):
            raise ValueError(f"Recipe response has invalid {field}")
    for field in ("cooking_time_minutes", "servings"):
        try:
            if int(data.get(field)) <= 0:
                raise ValueError
        except (TypeError, ValueError) as error:
            raise ValueError(f"Recipe response has invalid {field}") from error
    return data

def generate_recipe(
    user_id: int,
    servings: int = 2,
    meal_type: str = "Dinner",
    cuisine: str = "Italian",
    diet: str = "Vegetarian",
    spice_level: str = "Medium",
    cooking_time_minutes: int = 30,
    custom_prompt: str = "",
    latest_scanned_ingredients: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Optional[Recipe], str]:
    """
    Generate a personalized zero-waste recipe using Gemini AI and user's actual inventory.
    """
    if not user_id:
        return None, "User is not authenticated."

    # 1. Fetch user ingredients
    inventory = get_user_ingredients(user_id)
    expiring = get_expiring_ingredients(user_id)

    if not inventory:
        return None, "Your kitchen is empty. Scan your fridge or add ingredients first."

    # Bound prompt size: a whole pantry and full scan metadata add latency without
    # improving a single recipe. Urgent items are always kept at the front.
    prompt_inventory = (expiring + [item for item in inventory if item not in expiring])[:35]
    inventory_lines = [
        f"- {item.name}: {item.quantity} {item.unit} (Category: {item.category}, Status: {item.freshness_status}, Days Left: {item.days_remaining})"
        for item in prompt_inventory
    ]
    inventory_text = "\n".join(inventory_lines)

    expiring_lines = [
        f"- {item.name}: {item.quantity} {item.unit} ({item.freshness_status})"
        for item in expiring[:15]
    ]
    expiring_text = "\n".join(expiring_lines) if expiring_lines else "None (all ingredients are fresh)."
    latest_scan_text = json.dumps([
        {"name": item.get("name"), "freshness_status": item.get("freshness_status")}
        for item in (latest_scanned_ingredients or [])[:15]
        if isinstance(item, dict) and item.get("name")
    ], ensure_ascii=False)
    history = get_cooking_history(user_id)
    saved = get_saved_recipes(user_id)
    history_cuisines = [row.get("cuisine") for row in history if row.get("cuisine")]
    saved_cuisines = [recipe.cuisine for recipe in saved if recipe.cuisine]
    repeated_cuisines = [
        cuisine_name for cuisine_name, count in Counter(history_cuisines + saved_cuisines).items()
        if count >= 2
    ]
    history_text = (
        f"Repeated cuisine preferences inferred from at least two saved/cooked recipes: {', '.join(repeated_cuisines)}."
        if repeated_cuisines
        else "No repeated cooking pattern is available; rely on the current kitchen and explicit preferences."
    )

    prompt = RECIPE_PROMPT_TEMPLATE.format(
        inventory_text=inventory_text,
        expiring_text=expiring_text,
        servings=servings,
        meal_type=meal_type,
        cuisine=cuisine,
        diet=diet,
        spice_level=spice_level,
        cooking_time_minutes=cooking_time_minutes,
        custom_prompt=(custom_prompt or "Create a balanced, tasty zero-waste meal.")[:300],
        latest_scan_text=latest_scan_text,
        history_text=history_text,
    )

    try:
        raw_text = generate_json_content(
            prompt,
            temperature=0.3,
            max_output_tokens=800,
            # Lite is optimized for quick, structured recipe generation. The
            # regular Flash model remains the automatic reliability fallback.
            primary_model="gemini-flash-lite-latest",
            fallback_model="gemini-flash-latest",
            client=get_gemini_client(),
        )

        if not raw_text:
            return None, "Recipe generation is temporarily unavailable. Please try again."

        data = _parse_recipe_payload(raw_text)

        title = data["title"].strip()
        desc = str(data.get("description", "")).strip()
        # Preferences are constraints, not suggestions; keep the persisted recipe
        # aligned with the request even if the model echoes different metadata.
        res_cuisine = cuisine
        res_meal = meal_type
        dietary_tags = [diet] if diet != "No Preference" else (data.get("dietary_tags", []) if isinstance(data.get("dietary_tags"), list) else [])
        res_spice = spice_level
        res_time = min(int(data["cooking_time_minutes"]), cooking_time_minutes)
        res_servings = servings
        available_ing = data.get("available_ingredients", [])
        additional_ing = data.get("additional_ingredients", [])
        instructions = data.get("instructions", [])
        tips = data.get("tips", [])
        waste_score = int(data.get("waste_saved_score", 85))

        # Gemini may suggest ingredients liberally. Enforce the SQLite inventory
        # boundary before anything is displayed or saved.
        inventory_names = {item.name.strip().lower() for item in inventory}
        claimed = available_ing if isinstance(available_ing, list) else []
        available_ing = [item for item in claimed if isinstance(item, dict) and str(item.get("name", "")).strip().lower() in inventory_names]
        claimed_names = {str(item.get("name", "")).strip().lower() for item in claimed if isinstance(item, dict)}
        moved_to_additional = [item for item in claimed if isinstance(item, dict) and str(item.get("name", "")).strip().lower() not in inventory_names]
        additional_ing = (additional_ing if isinstance(additional_ing, list) else []) + moved_to_additional

        if diet in ("Vegetarian", "Vegan"):
            prohibited = ["chicken", "beef", "pork", "lamb", "fish", "seafood", "shrimp", "meat", "gelatin"]
            if diet == "Vegan":
                prohibited += ["egg", "milk", "cheese", "butter", "yogurt", "cream", "honey"]
            all_names = " ".join(str(item.get("name", "")).lower() for item in available_ing + additional_ing if isinstance(item, dict))
            if any(word in all_names for word in prohibited):
                return None, "Recipe generation is temporarily unavailable. Please try again."

        # Save generated recipe to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO recipes (
                    user_id, title, description, cuisine, meal_type, dietary_tags,
                    spice_level, cooking_time_minutes, servings, available_ingredients,
                    additional_ingredients, instructions, tips, waste_saved_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """ if False else """
                INSERT INTO recipes (
                    user_id, title, description, cuisine, meal_type, dietary_tags,
                    spice_level, cooking_time_minutes, servings, available_ingredients,
                    additional_ingredients, instructions, tips, waste_saved_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    user_id, title, desc, res_cuisine, res_meal,
                    json.dumps(dietary_tags), res_spice, res_time, res_servings,
                    json.dumps(available_ing), json.dumps(additional_ing),
                    json.dumps(instructions), json.dumps(tips), waste_score
                )
            )
            recipe_id = cursor.lastrowid

        recipe = Recipe(
            id=recipe_id,
            user_id=user_id,
            title=title,
            description=desc,
            cuisine=res_cuisine,
            meal_type=res_meal,
            dietary_tags=dietary_tags,
            spice_level=res_spice,
            cooking_time_minutes=res_time,
            servings=res_servings,
            available_ingredients=available_ing,
            additional_ingredients=additional_ing,
            instructions=instructions,
            tips=tips,
            waste_saved_score=waste_score,
            created_at="Just now",
            is_saved=False
        )
        return recipe, ""

    except json.JSONDecodeError as je:
        logger.error("Failed to parse recipe JSON: %s", je)
        return None, "Recipe generation is temporarily unavailable. Please try again."
    except ValueError as validation_error:
        logger.error("Gemini recipe response failed validation: %s", validation_error)
        return None, "Recipe generation is temporarily unavailable. Please try again."
    except Exception as e:
        logger.error("Recipe generation error: %s", type(e).__name__)
        return None, "Recipe generation is temporarily unavailable. Please try again."

def save_recipe(user_id: int, recipe_id: int) -> bool:
    """Save a recipe to the user's saved collection."""
    if not user_id or not recipe_id:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Verify user owns or has access to recipe
        cursor.execute("SELECT id FROM recipes WHERE id = ? AND user_id = ?;", (recipe_id, user_id))
        if not cursor.fetchone():
            return False

        cursor.execute(
            """
            INSERT OR IGNORE INTO saved_recipes (user_id, recipe_id)
            VALUES (?, ?);
            """,
            (user_id, recipe_id)
        )
        return cursor.rowcount > 0

def unsave_recipe(user_id: int, recipe_id: int) -> bool:
    """Remove a recipe from user's saved collection."""
    if not user_id or not recipe_id:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_recipes WHERE user_id = ? AND recipe_id = ?;", (user_id, recipe_id))
        return cursor.rowcount > 0

def get_saved_recipes(user_id: int) -> List[Recipe]:
    """Retrieve all saved recipes belonging strictly to user_id."""
    if not user_id:
        return []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.*, sr.saved_at
            FROM saved_recipes sr
            JOIN recipes r ON sr.recipe_id = r.id
            WHERE sr.user_id = ?
            ORDER BY sr.saved_at DESC;
            """,
            (user_id,)
        )
        rows = cursor.fetchall()

    saved_list: List[Recipe] = []
    for row in rows:
        try:
            r = Recipe(
                id=row["id"],
                user_id=row["user_id"],
                title=row["title"],
                description=row["description"],
                cuisine=row["cuisine"],
                meal_type=row["meal_type"],
                dietary_tags=json.loads(row["dietary_tags"]),
                spice_level=row["spice_level"],
                cooking_time_minutes=row["cooking_time_minutes"],
                servings=row["servings"],
                available_ingredients=json.loads(row["available_ingredients"]),
                additional_ingredients=json.loads(row["additional_ingredients"]),
                instructions=json.loads(row["instructions"]),
                tips=json.loads(row["tips"]),
                waste_saved_score=row["waste_saved_score"],
                created_at=str(row["saved_at"]),
                is_saved=True
            )
            saved_list.append(r)
        except Exception as e:
            logger.error(f"Error parsing saved recipe: {e}")
    return saved_list

def get_recipe_by_id(user_id: int, recipe_id: int) -> Optional[Recipe]:
    """Retrieve a single recipe verifying user ownership."""
    if not user_id or not recipe_id:
        return None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes WHERE id = ? AND user_id = ?;", (recipe_id, user_id))
        row = cursor.fetchone()
        if not row:
            return None

        # Check if saved
        cursor.execute("SELECT id FROM saved_recipes WHERE user_id = ? AND recipe_id = ?;", (user_id, recipe_id))
        is_saved = cursor.fetchone() is not None

        return Recipe(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            cuisine=row["cuisine"],
            meal_type=row["meal_type"],
            dietary_tags=json.loads(row["dietary_tags"]),
            spice_level=row["spice_level"],
            cooking_time_minutes=row["cooking_time_minutes"],
            servings=row["servings"],
            available_ingredients=json.loads(row["available_ingredients"]),
            additional_ingredients=json.loads(row["additional_ingredients"]),
            instructions=json.loads(row["instructions"]),
            tips=json.loads(row["tips"]),
            waste_saved_score=row["waste_saved_score"],
            created_at=str(row["created_at"]),
            is_saved=is_saved
        )

def record_cooking_history(
    user_id: int,
    recipe_title: str,
    cuisine: str,
    servings: int,
    notes: str = "",
    rating: int = 5
) -> bool:
    """Record a completed cooking session in user's cooking history."""
    if not user_id or not recipe_title:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO cooking_history (user_id, recipe_title, cuisine, servings, notes, rating)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (user_id, recipe_title.strip(), cuisine.strip(), servings, notes.strip(), rating)
        )
        return cursor.rowcount > 0

def get_cooking_history(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve cooking history strictly for user_id."""
    if not user_id:
        return []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM cooking_history
            WHERE user_id = ?
            ORDER BY cooked_at DESC;
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
