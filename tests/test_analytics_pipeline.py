"""Tests for authenticated analytics data loading and empty states."""
import os
import tempfile
import inspect
import json

import pytest

from components.analytics import load_analytics_data
from services.auth_service import signup_user
from services.kitchen_service import add_ingredient
from services.recipe_service import get_cooking_history, get_saved_recipes, record_cooking_history
from services.recipe_service import save_recipe
from utils.database import get_db_connection, init_db
from components import analytics


@pytest.fixture(autouse=True)
def database(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        path = handle.name
    monkeypatch.setenv("FRIDGE2FEAST_DB_PATH", path)
    init_db()
    yield
    os.remove(path)


def test_analytics_loads_only_authenticated_users_data():
    user_a, _ = signup_user("analytics-a@example.com", "Analytics A", "Password123")
    user_b, _ = signup_user("analytics-b@example.com", "Analytics B", "Password123")
    add_ingredient(user_a.id, {"name": "Tomato", "category": "Produce", "quantity": 2, "unit": "pcs", "estimated_shelf_life_days": 1})
    add_ingredient(user_b.id, {"name": "Rice", "category": "Pantry", "quantity": 1, "unit": "kg", "estimated_shelf_life_days": 30})
    record_cooking_history(user_a.id, "Tomato Bowl", "Indian", 2)

    data_a = load_analytics_data(user_a.id)
    data_b = load_analytics_data(user_b.id)

    assert list(data_a["inventory"]["name"]) == ["Tomato"]
    assert list(data_b["inventory"]["name"]) == ["Rice"]
    assert len(data_a["cooking_history"]) == 1
    assert data_b["cooking_history"] == []
    assert data_a["saved_recipes"] == []
    assert data_b["saved_recipes"] == []


def test_analytics_ignores_legacy_session_lists(monkeypatch):
    user, _ = signup_user("analytics-real@example.com", "Real Analytics", "Password123")
    add_ingredient(user.id, {"name": "Carrot", "category": "Produce", "quantity": 1, "unit": "pcs", "estimated_shelf_life_days": 7})
    monkeypatch.setattr("components.analytics.st.session_state", {"detected_ingredients": [{"name": "Fake"}], "saved_recipes": [{"title": "Fake"}], "generated_recipes": [{"title": "Fake"}]})

    data = load_analytics_data(user.id)

    assert list(data["inventory"]["name"]) == ["Carrot"]
    assert data["saved_recipes"] == []
    assert data["cooking_history"] == []


def test_empty_analytics_has_no_fabricated_frames():
    user, _ = signup_user("analytics-empty@example.com", "Empty Analytics", "Password123")

    data = load_analytics_data(user.id)

    assert data["inventory"].empty
    assert data["insights"]["freshness"].empty
    assert data["insights"]["categories"].empty
    assert data["saved_recipes"] == get_saved_recipes(user.id) == []
    assert data["cooking_history"] == get_cooking_history(user.id) == []


def test_saved_recipe_analytics_are_user_scoped():
    user_a, _ = signup_user("analytics-saved-a@example.com", "Saved A", "Password123")
    user_b, _ = signup_user("analytics-saved-b@example.com", "Saved B", "Password123")
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO recipes (
                user_id, title, description, cuisine, meal_type, dietary_tags,
                spice_level, cooking_time_minutes, servings, available_ingredients,
                additional_ingredients, instructions, tips, waste_saved_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_a.id, "Saved Bowl", "A real saved recipe", "Indian", "Dinner", json.dumps(["Vegetarian"]),
             "Medium", 30, 2, json.dumps([]), json.dumps([]), json.dumps(["Cook"]), json.dumps([]), 80),
        )
        recipe_id = cursor.lastrowid
    assert save_recipe(user_a.id, recipe_id)

    assert len(load_analytics_data(user_a.id)["saved_recipes"]) == 1
    assert load_analytics_data(user_b.id)["saved_recipes"] == []


def test_analytics_renderer_has_no_gemini_dependency():
    source = inspect.getsource(analytics.render_analytics_component)

    assert "gemini" not in source.lower()
