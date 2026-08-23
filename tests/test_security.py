"""Security & Strict User Isolation Tests."""
import pytest
import os
import tempfile
from utils.database import init_db
from services.auth_service import signup_user
from services.kitchen_service import (
    add_ingredient, get_user_ingredients, update_ingredient, delete_ingredient
)
from services.recipe_service import save_recipe, get_saved_recipes, unsave_recipe
from models.recipe import Recipe

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db_path = tmp.name
    monkeypatch.setenv("FRIDGE2FEAST_DB_PATH", test_db_path)
    init_db()
    yield test_db_path
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

def test_user_data_isolation():
    # User A
    user_a, _ = signup_user("user_a@example.com", "User Alpha", "AlphaPass123")
    # User B
    user_b, _ = signup_user("user_b@example.com", "User Beta", "BetaPass123")

    # User A adds Avocado
    ing_a = add_ingredient(user_a.id, {
        "name": "Avocado",
        "category": "Produce",
        "quantity": 2.0,
        "unit": "pcs",
        "estimated_shelf_life_days": 4
    })

    # User B adds Milk
    ing_b = add_ingredient(user_b.id, {
        "name": "Almond Milk",
        "category": "Dairy",
        "quantity": 1.0,
        "unit": "bottle",
        "estimated_shelf_life_days": 14
    })

    # User A must ONLY see Avocado
    items_a = get_user_ingredients(user_a.id)
    assert len(items_a) == 1
    assert items_a[0].name == "Avocado"

    # User B must ONLY see Almond Milk
    items_b = get_user_ingredients(user_b.id)
    assert len(items_b) == 1
    assert items_b[0].name == "Almond Milk"

    # User B cannot update User A's Avocado
    cross_update = update_ingredient(user_b.id, ing_a.id, {"name": "Hacked Avocado"})
    assert cross_update is False
    assert get_user_ingredients(user_a.id)[0].name == "Avocado"

    # User B cannot delete User A's Avocado
    cross_delete = delete_ingredient(user_b.id, ing_a.id)
    assert cross_delete is False
    assert len(get_user_ingredients(user_a.id)) == 1

def test_sql_injection_resilience():
    # Attempt SQL injection through inputs
    user, _ = signup_user("inject@example.com", "Test'; DROP TABLE users; --", "SecurePass123")
    assert user is not None

    # Search query with injection string
    injection_items = get_user_ingredients(user.id, search_query="' OR '1'='1")
    assert isinstance(injection_items, list)
