"""Focused tests for the scan -> preferences -> recipe workflow."""
import json
import os
import tempfile
import pytest

from utils.database import init_db
from services.auth_service import signup_user
from services.kitchen_service import batch_add_ingredients, add_ingredient, get_user_ingredients
from services.recipe_service import generate_recipe, save_recipe, get_saved_recipes


@pytest.fixture(autouse=True)
def database(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        path = handle.name
    monkeypatch.setenv("FRIDGE2FEAST_DB_PATH", path)
    init_db()
    yield
    os.remove(path)


class FakeModels:
    def __init__(self, body): self.body = body; self.prompt = ""
    def generate_content(self, **kwargs):
        self.prompt = kwargs["contents"]
        return type("Response", (), {"text": self.body})()

class FakeClient:
    def __init__(self, body): self.models = FakeModels(body)


def payload(available, additional=None):
    return json.dumps({"title": "Kitchen Bowl", "description": "A practical zero-waste meal.", "cuisine": "Indian", "meal_type": "Dinner", "dietary_tags": ["Vegetarian"], "spice_level": "Spicy", "cooking_time_minutes": 30, "servings": 4, "available_ingredients": available, "additional_ingredients": additional or [], "instructions": ["Prepare ingredients.", "Cook and serve."], "tips": ["Store leftovers chilled; this rescues urgent produce."], "waste_saved_score": 90})


def test_confirmed_scan_persists_and_generation_uses_real_scan_context(monkeypatch):
    user, _ = signup_user("scan@example.com", "Scan Chef", "Password123")
    added = batch_add_ingredients(user.id, [{"name": "Tomato", "category": "Produce", "quantity": 2, "unit": "pcs", "estimated_shelf_life_days": 1}])
    assert [item.name for item in get_user_ingredients(user.id)] == ["Tomato"]
    client = FakeClient(payload([{"name": "Tomato", "quantity": "2", "unit": "pcs"}]))
    monkeypatch.setattr("services.recipe_service.get_gemini_client", lambda: client)
    recipe, error = generate_recipe(user.id, servings=4, meal_type="Dinner", cuisine="Indian", diet="Vegetarian", spice_level="Spicy", cooking_time_minutes=30, latest_scanned_ingredients=[{"name": added[0].name, "freshness_status": "USE SOON"}])
    assert not error and recipe.servings == 4
    assert "Latest confirmed scan" in client.models.prompt and "Tomato" in client.models.prompt
    assert "Days Left: 1" in client.models.prompt


@pytest.mark.parametrize("diet, forbidden", [("Vegetarian", "Chicken"), ("Vegan", "Cheese")])
def test_dietary_rules_reject_animal_ingredients(monkeypatch, diet, forbidden):
    user, _ = signup_user(f"{diet}@example.com", "Diet Chef", "Password123")
    add_ingredient(user.id, {"name": "Tomato", "category": "Produce", "quantity": 2, "unit": "pcs", "estimated_shelf_life_days": 1})
    monkeypatch.setattr("services.recipe_service.get_gemini_client", lambda: FakeClient(payload([{"name": "Tomato"}], [{"name": forbidden}])))
    recipe, error = generate_recipe(user.id, diet=diet)
    assert recipe is None and "temporarily unavailable" in error


def test_non_vegetarian_preferences_and_kitchen_separation_and_saved_owner(monkeypatch):
    user, _ = signup_user("owner@example.com", "Owner", "Password123")
    other, _ = signup_user("other@example.com", "Other", "Password123")
    add_ingredient(user.id, {"name": "Chicken", "category": "Meat", "quantity": 500, "unit": "g", "estimated_shelf_life_days": 0})
    client = FakeClient(payload([{"name": "Chicken", "quantity": "500", "unit": "g"}, {"name": "Rice", "quantity": "1", "unit": "cup"}]))
    monkeypatch.setattr("services.recipe_service.get_gemini_client", lambda: client)
    recipe, error = generate_recipe(user.id, servings=6, cuisine="Mexican", spice_level="Very Spicy", cooking_time_minutes=45, diet="Non-Vegetarian")
    assert not error and recipe.servings == 6 and recipe.spice_level == "Very Spicy"
    assert [item["name"] for item in recipe.available_ingredients] == ["Chicken"]
    assert any(item["name"] == "Rice" for item in recipe.additional_ingredients)
    assert save_recipe(user.id, recipe.id)
    assert len(get_saved_recipes(user.id)) == 1 and get_saved_recipes(other.id) == []


def test_empty_kitchen_and_gemini_failure_are_safe(monkeypatch):
    user, _ = signup_user("empty@example.com", "Empty", "Password123")
    recipe, error = generate_recipe(user.id)
    assert recipe is None and error == "Your kitchen is empty. Scan your fridge or add ingredients first."
    add_ingredient(user.id, {"name": "Carrot", "category": "Produce", "quantity": 1, "unit": "pcs", "estimated_shelf_life_days": 3})
    monkeypatch.setattr("services.recipe_service.get_gemini_client", lambda: (_ for _ in ()).throw(RuntimeError("no service")))
    recipe, error = generate_recipe(user.id)
    assert recipe is None and error == "Recipe generation is temporarily unavailable. Please try again."


def test_prompt_carries_every_recipe_preference_and_zero_waste_rules(monkeypatch):
    user, _ = signup_user("prompt@example.com", "Prompt Chef", "Password123")
    add_ingredient(user.id, {"name": "Spinach", "category": "Produce", "quantity": 1, "unit": "bunch", "estimated_shelf_life_days": 1})
    client = FakeClient(payload([{"name": "Spinach"}]))
    monkeypatch.setattr("services.recipe_service.get_gemini_client", lambda: client)

    recipe, error = generate_recipe(
        user.id, servings=3, meal_type="Lunch", cuisine="Thai", diet="Vegan",
        spice_level="Mild", cooking_time_minutes=20, custom_prompt="Use one pan.",
    )

    assert recipe is not None and not error
    for expected in ("Requested Servings: 3", "Meal Type: Lunch", "Target Cuisine: Thai",
                     "Dietary Preference: Vegan", "Preferred Spice Level: Mild",
                     "Target Cooking Time: 20 minutes", "Use one pan.",
                     "From Your Kitchen", "You May Need", "Prioritize using the EXPIRING"):
        assert expected in client.models.prompt


def test_malformed_recipe_response_is_never_saved(monkeypatch):
    user, _ = signup_user("malformed@example.com", "Safe Chef", "Password123")
    add_ingredient(user.id, {"name": "Potato", "category": "Produce", "quantity": 2, "unit": "pcs", "estimated_shelf_life_days": 2})
    monkeypatch.setattr("services.recipe_service.get_gemini_client", lambda: FakeClient('{"title": "Broken"}'))

    recipe, error = generate_recipe(user.id)

    assert recipe is None
    assert error == "Recipe generation is temporarily unavailable. Please try again."
    assert get_saved_recipes(user.id) == []
