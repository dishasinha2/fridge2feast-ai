"""Kitchen Inventory and Freshness Service for Fridge2Feast AI."""
from datetime import date
from typing import List, Dict, Any, Optional
from utils.database import get_db_connection
from utils.calculations import calculate_freshness, calculate_expiry_date, calculate_zero_waste_score
from utils.validation import normalize_ingredient_name, VALID_CATEGORIES, VALID_UNITS
from utils.pandas_utils import inventory_to_freshness_df
from models.ingredient import Ingredient

def get_user_ingredients(
    user_id: int,
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    sort_by: str = "freshness"
) -> List[Ingredient]:
    """
    Retrieve all ingredients for the authenticated user with real-time freshness recalculation.
    Strictly isolated to user_id.
    """
    if not user_id:
        return []

    query = "SELECT * FROM ingredients WHERE user_id = ?"
    params: List[Any] = [user_id]

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query.strip()}%")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

    ingredients: List[Ingredient] = []
    for row in rows:
        shelf_life = row["estimated_shelf_life_days"]
        added_date = row["added_date"]
        
        # Calculate real-time freshness based on today's date
        status, days_left, exp_date_str = calculate_freshness(added_date, shelf_life)

        ing = Ingredient(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            category=row["category"],
            quantity=float(row["quantity"]),
            unit=row["unit"],
            freshness_status=status,
            estimated_shelf_life_days=shelf_life,
            storage_advice=row["storage_advice"] or "Store properly in refrigerator or pantry.",
            confidence=float(row["confidence"]),
            added_date=str(added_date),
            expiry_date=exp_date_str,
            days_remaining=days_left
        )
        ingredients.append(ing)

    # Sorting
    if sort_by == "freshness":
        # USE TODAY first (days_remaining <= 0), then USE SOON (1-2), then FRESH
        ingredients.sort(key=lambda x: x.days_remaining)
    elif sort_by == "name":
        ingredients.sort(key=lambda x: x.name.lower())
    elif sort_by == "category":
        ingredients.sort(key=lambda x: (x.category, x.name.lower()))

    return ingredients

def add_ingredient(user_id: int, item: Dict[str, Any]) -> Optional[Ingredient]:
    """Add a single ingredient to the user's kitchen inventory."""
    if not user_id:
        return None

    name = normalize_ingredient_name(item.get("name", ""))
    if not name:
        return None

    category = item.get("category", "Produce")
    if category not in VALID_CATEGORIES:
        category = "Other"

    qty = float(item.get("quantity", item.get("estimated_quantity", 1)))
    unit = item.get("unit", "pcs")
    if unit not in VALID_UNITS:
        unit = "pcs"

    shelf_life = int(item.get("estimated_shelf_life_days", item.get("shelf_life", 5)))
    storage_advice = item.get("storage_advice", item.get("storage_recommendation", "Store properly."))
    confidence = float(item.get("confidence", 1.0))
    today_str = date.today().strftime("%Y-%m-%d")
    status, days_left, exp_str = calculate_freshness(today_str, shelf_life)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ingredients (
                user_id, name, category, quantity, unit, freshness_status,
                estimated_shelf_life_days, storage_advice, confidence, added_date, expiry_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                user_id, name, category, qty, unit, status,
                shelf_life, storage_advice, confidence, today_str, exp_str
            )
        )
        new_id = cursor.lastrowid

    return Ingredient(
        id=new_id,
        user_id=user_id,
        name=name,
        category=category,
        quantity=qty,
        unit=unit,
        freshness_status=status,
        estimated_shelf_life_days=shelf_life,
        storage_advice=storage_advice,
        confidence=confidence,
        added_date=today_str,
        expiry_date=exp_str,
        days_remaining=days_left
    )

def batch_add_ingredients(user_id: int, items: List[Dict[str, Any]]) -> List[Ingredient]:
    """Add multiple ingredients in a single transaction after user scan review."""
    if not user_id or not items:
        return []

    added_list: List[Ingredient] = []
    today_str = date.today().strftime("%Y-%m-%d")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        for item in items:
            name = normalize_ingredient_name(item.get("name", ""))
            if not name:
                continue

            category = item.get("category", "Produce")
            if category not in VALID_CATEGORIES:
                category = "Other"

            qty = float(item.get("quantity", item.get("estimated_quantity", 1)))
            unit = item.get("unit", "pcs")
            if unit not in VALID_UNITS:
                unit = "pcs"

            shelf_life = int(item.get("estimated_shelf_life_days", item.get("shelf_life", 5)))
            storage_advice = item.get("storage_advice", item.get("storage_recommendation", "Store in refrigerator."))
            confidence = float(item.get("confidence", 0.95))
            status, days_left, exp_str = calculate_freshness(today_str, shelf_life)

            cursor.execute(
                """
                INSERT INTO ingredients (
                    user_id, name, category, quantity, unit, freshness_status,
                    estimated_shelf_life_days, storage_advice, confidence, added_date, expiry_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    user_id, name, category, qty, unit, status,
                    shelf_life, storage_advice, confidence, today_str, exp_str
                )
            )
            new_id = cursor.lastrowid
            added_list.append(
                Ingredient(
                    id=new_id,
                    user_id=user_id,
                    name=name,
                    category=category,
                    quantity=qty,
                    unit=unit,
                    freshness_status=status,
                    estimated_shelf_life_days=shelf_life,
                    storage_advice=storage_advice,
                    confidence=confidence,
                    added_date=today_str,
                    expiry_date=exp_str,
                    days_remaining=days_left
                )
            )

    return added_list

def update_ingredient(user_id: int, ingredient_id: int, updated: Dict[str, Any]) -> bool:
    """Update an ingredient belonging to the authenticated user."""
    if not user_id or not ingredient_id:
        return False

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ingredients WHERE id = ? AND user_id = ?;", (ingredient_id, user_id))
        row = cursor.fetchone()
        if not row:
            return False

        name = normalize_ingredient_name(updated.get("name", row["name"]))
        category = updated.get("category", row["category"])
        if category not in VALID_CATEGORIES:
            category = "Other"

        qty = float(updated.get("quantity", row["quantity"]))
        unit = updated.get("unit", row["unit"])
        shelf_life = int(updated.get("estimated_shelf_life_days", row["estimated_shelf_life_days"]))
        storage_advice = updated.get("storage_advice", row["storage_advice"] or "Store properly.")

        added_date = row["added_date"]
        status, _, exp_str = calculate_freshness(added_date, shelf_life)

        cursor.execute(
            """
            UPDATE ingredients SET
                name = ?, category = ?, quantity = ?, unit = ?,
                estimated_shelf_life_days = ?, storage_advice = ?,
                freshness_status = ?, expiry_date = ?
            WHERE id = ? AND user_id = ?;
            """,
            (name, category, qty, unit, shelf_life, storage_advice, status, exp_str, ingredient_id, user_id)
        )
        return cursor.rowcount > 0

def delete_ingredient(user_id: int, ingredient_id: int) -> bool:
    """Delete an ingredient owned by user_id."""
    if not user_id or not ingredient_id:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ingredients WHERE id = ? AND user_id = ?;", (ingredient_id, user_id))
        return cursor.rowcount > 0

def get_kitchen_summary(user_id: int) -> Dict[str, Any]:
    """
    Calculate kitchen counts strictly from SQLite for the authenticated user.
    """
    ingredients = get_user_ingredients(user_id)
    inventory_df = inventory_to_freshness_df(ingredients)
    total_count = len(inventory_df)
    use_today_count = int((inventory_df["days_remaining"] <= 0).sum()) if not inventory_df.empty else 0
    use_soon_count = int(inventory_df["days_remaining"].between(1, 2).sum()) if not inventory_df.empty else 0
    fresh_count = int((inventory_df["days_remaining"] >= 3).sum()) if not inventory_df.empty else 0
    expiring_count = use_today_count + use_soon_count

    # Calculate zero waste score based on fresh items vs expiring items
    zero_waste_score = calculate_zero_waste_score(total_count, fresh_count, expiring_count)


    return {
        "total_count": total_count,
        "use_today_count": use_today_count,
        "use_soon_count": use_soon_count,
        "expiring_count": expiring_count,
        "fresh_count": fresh_count,
        "zero_waste_score": zero_waste_score
    }

def get_expiring_ingredients(user_id: int) -> List[Ingredient]:
    """Get items that are USE TODAY or USE SOON for urgent rescue."""
    ingredients = get_user_ingredients(user_id, sort_by="freshness")
    return [item for item in ingredients if item.days_remaining <= 2]
