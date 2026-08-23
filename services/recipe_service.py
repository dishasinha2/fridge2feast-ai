"""Recipe Generation and Management Service for Fridge2Feast AI."""
import json
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from utils.database import get_db_connection
from services.kitchen_service import get_user_ingredients, get_expiring_ingredients
from services.gemini_client import get_gemini_client
from models.recipe import Recipe

logger = logging.getLogger(__name__)

RECIPE_PROMPT_TEMPLATE = """
You are Fridge2Feast AI, a world-class zero-waste chef and culinary AI.
Your goal is to turn available kitchen ingredients into a delicious, high-craft, personalized recipe while minimizing food waste.

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

CRITICAL RULES:
1. Prioritize using the EXPIRING ingredients first to prevent food waste.
2. In "available_ingredients", ONLY include items that actually appear in the USER INVENTORY list above. Never claim an item is in their kitchen if it is not listed.
3. In "additional_ingredients", list only pantry staples (e.g. olive oil, salt, black pepper, water) or minimal optional additions not found in their inventory.
4. Ensure instructions are clear, step-by-step, and numbered sequentially.
5. Provide a "waste_saved_score" (integer between 60 and 100) reflecting how effectively this recipe rescues expiring food.
6. Dietary safety is mandatory: Vegetarian excludes meat and seafood; Vegan excludes meat, seafood, eggs, dairy, and all animal-derived ingredients. Non-Vegetarian may use meat or seafood only when appropriate.
7. Include preparation time, total time, substitutions when useful, storage guidance, and a short zero-waste explanation in the description or tips.

Output a strictly valid JSON object matching this exact schema:
{{
  "title": "Recipe Title",
  "description": "Appetizing 1-2 sentence description highlighting the flavors and zero-waste rescue.",
  "cuisine": "{cuisine}",
  "meal_type": "{meal_type}",
  "dietary_tags": ["Vegetarian", "Dairy-Free"],
  "spice_level": "{spice_level}",
  "cooking_time_minutes": 30,
  "servings": {servings},
  "available_ingredients": [
    {{"name": "Tomatoes", "quantity": "2", "unit": "pcs", "note": "rescued from pantry"}}
  ],
  "additional_ingredients": [
    {{"name": "Olive Oil", "quantity": "1", "unit": "tbsp", "optional_substitute": "any cooking oil"}},
    {{"name": "Salt & Pepper", "quantity": "to taste", "unit": "", "optional_substitute": ""}}
  ],
  "instructions": [
    "Wash and dice the rescued tomatoes into 1/2 inch cubes.",
    "Heat olive oil in a skillet over medium heat...",
    "Serve warm and enjoy!"
  ],
  "tips": [
    "Save tomato skins or ends in a freezer bag for making vegetable broth."
  ],
  "waste_saved_score": 92
}}

Output ONLY the raw JSON object. Do not include markdown code block syntax or exterior commentary.
"""

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

    inventory_lines = [
        f"- {item.name}: {item.quantity} {item.unit} (Category: {item.category}, Status: {item.freshness_status}, Days Left: {item.days_remaining})"
        for item in inventory
    ]
    inventory_text = "\n".join(inventory_lines)

    expiring_lines = [
        f"- {item.name}: {item.quantity} {item.unit} ({item.freshness_status})"
        for item in expiring
    ]
    expiring_text = "\n".join(expiring_lines) if expiring_lines else "None (all ingredients are fresh)."
    latest_scan_text = json.dumps(latest_scanned_ingredients or [], ensure_ascii=False)

    prompt = RECIPE_PROMPT_TEMPLATE.format(
        inventory_text=inventory_text,
        expiring_text=expiring_text,
        servings=servings,
        meal_type=meal_type,
        cuisine=cuisine,
        diet=diet,
        spice_level=spice_level,
        cooking_time_minutes=cooking_time_minutes,
        custom_prompt=custom_prompt or "Create a balanced, tasty zero-waste meal."
        ,latest_scan_text=latest_scan_text
    )

    try:
        client = get_gemini_client()
        raw_text = None

        if hasattr(client, "models") and hasattr(client.models, "generate_content"):
            # Keep the official google-genai configuration when installed.  The
            # fallback also makes the wrapper testable with its existing client seam.
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    temperature=0.4, response_mime_type="application/json"
                )
            except ImportError:
                config = {"temperature": 0.4, "response_mime_type": "application/json"}
            try:
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt,
                    config=config
                )
            except Exception as model_err:
                logger.warning(f"Primary recipe model failed, falling back to gemini-flash-lite-latest: {model_err}")
                response = client.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents=prompt,
                    config=config
                )
            raw_text = response.text
        else:
            model = client.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            raw_text = response.text

        if not raw_text:
            return None, "Recipe generation is temporarily unavailable. Please try again."

        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned)
            cleaned = re.sub(r"```$", "", cleaned)
            cleaned = cleaned.strip()

        data = json.loads(cleaned)

        title = str(data.get("title", "Chef's Kitchen Creation")).strip()
        desc = str(data.get("description", "")).strip()
        # Preferences are constraints, not suggestions; keep the persisted recipe
        # aligned with the request even if the model echoes different metadata.
        res_cuisine = cuisine
        res_meal = meal_type
        dietary_tags = [diet] if diet != "No Preference" else (data.get("dietary_tags", []) if isinstance(data.get("dietary_tags"), list) else [])
        res_spice = spice_level
        res_time = min(int(data.get("cooking_time_minutes", cooking_time_minutes)), cooking_time_minutes)
        res_servings = servings
        available_ing = data.get("available_ingredients", [])
        additional_ing = data.get("additional_ingredients", [])
        instructions = data.get("instructions", [])
        tips = data.get("tips", [])
        waste_score = int(data.get("waste_saved_score", 85))

        if not instructions or not isinstance(instructions, list):
            return None, "Recipe generation produced incomplete instructions. Please try again."

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
        logger.error(f"Failed to parse recipe JSON: {je}")
        return None, "Recipe generation is temporarily unavailable. Please try again."
    except Exception as e:
        logger.error(f"Recipe generation error: {e}")
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
