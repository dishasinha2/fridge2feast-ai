"""Tests for Kitchen Inventory & Deterministic Freshness Engine."""
import pytest
import os
import tempfile
from datetime import datetime, timedelta
from utils.database import init_db
from utils.calculations import calculate_freshness, calculate_zero_waste_score
from services.auth_service import signup_user
from services.kitchen_service import (
    add_ingredient, get_user_ingredients, update_ingredient, delete_ingredient,
    get_expiring_ingredients, get_kitchen_summary
)

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

def test_freshness_calculation():
    today = datetime.now()
    
    # Item added today with 7 days shelf life -> 7 days remaining -> FRESH
    added_str = today.strftime("%Y-%m-%d %H:%M:%S")
    status, days_rem, exp_str = calculate_freshness(added_str, 7)
    assert days_rem == 7
    assert status == "FRESH"

    # Item added 5 days ago with 6 days shelf life -> 1 day remaining -> USE SOON
    five_days_ago = (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    status, days_rem, exp_str = calculate_freshness(five_days_ago, 6)
    assert days_rem == 1
    assert status == "USE SOON"

    # Item added 7 days ago with 7 days shelf life -> 0 days remaining -> USE TODAY
    seven_days_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    status, days_rem, exp_str = calculate_freshness(seven_days_ago, 7)
    assert days_rem <= 0
    assert status == "USE TODAY"


def test_kitchen_crud_and_metrics():
    user, _ = signup_user("chef.test@example.com", "Test Chef", "SecurePass123")
    
    # 1. Add ingredients
    ing1 = add_ingredient(user.id, {
        "name": "Organic Tomatoes",
        "category": "Produce",
        "quantity": 4.0,
        "unit": "pcs",
        "estimated_shelf_life_days": 1,  # Expiring soon
        "storage_advice": "Room temperature"
    })
    assert ing1 is not None
    assert ing1.id is not None

    ing2 = add_ingredient(user.id, {
        "name": "Greek Yogurt",
        "category": "Dairy",
        "quantity": 1.0,
        "unit": "carton",
        "estimated_shelf_life_days": 10,
        "storage_advice": "Refrigerator"
    })
    assert ing2 is not None

    # 2. Query ingredients
    items = get_user_ingredients(user.id)
    assert len(items) == 2

    # 3. Check Expiring items
    expiring = get_expiring_ingredients(user.id)
    assert len(expiring) == 1
    assert expiring[0].name == "Organic Tomatoes"

    # 4. Update ingredient
    updated = update_ingredient(user.id, ing1.id, {"quantity": 2.0, "estimated_shelf_life_days": 5})
    assert updated is True
    
    items_after_upd = get_user_ingredients(user.id)
    tomatoes = next(i for i in items_after_upd if i.id == ing1.id)
    assert tomatoes.quantity == 2.0
    assert tomatoes.estimated_shelf_life_days == 5

    # 5. Summary calculation
    summary = get_kitchen_summary(user.id)
    assert summary["total_count"] == 2
    assert summary["zero_waste_score"] == 100  # since shelf life is now 5

    # 6. Delete ingredient
    deleted = delete_ingredient(user.id, ing2.id)
    assert deleted is True
    assert len(get_user_ingredients(user.id)) == 1
