"""Tests for Recipe Services, Voice Parsing, and Cooking History."""
import pytest
import os
import tempfile
from utils.database import init_db
from services.auth_service import signup_user
from services.kitchen_service import add_ingredient
from services.recipe_service import save_recipe, get_saved_recipes, unsave_recipe, record_cooking_history, get_cooking_history
from services.voice_service import parse_voice_recipe_query
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

def test_voice_query_parser():
    q1 = "Make Italian dinner for 4 people with mild spice"
    p1 = parse_voice_recipe_query(q1)
    assert p1.get("cuisine") == "Italian"
    assert p1.get("meal_type") == "Dinner"
    assert p1.get("servings") == 4
    assert p1.get("spice_level") == "Mild"

    q2 = "Quick vegan lunch for two in 15 minutes"
    p2 = parse_voice_recipe_query(q2)
    assert p2.get("diet") == "Vegan"
    assert p2.get("meal_type") == "Lunch"
    assert p2.get("servings") == 2
    assert p2.get("cooking_time_minutes") == 15

def test_cooking_history_logging():
    user, _ = signup_user("chef.history@example.com", "Chef History", "HistoryPass123")
    
    # Record a cooking session
    res = record_cooking_history(
        user_id=user.id,
        recipe_title="Rustic Tomato Pasta",
        cuisine="Italian",
        servings=4,
        notes="Delicious zero-waste meal",
        rating=5
    )
    assert res is True

    # Retrieve history
    history = get_cooking_history(user.id)
    assert len(history) == 1
    assert history[0]["recipe_title"] == "Rustic Tomato Pasta"
    assert history[0]["servings"] == 4
