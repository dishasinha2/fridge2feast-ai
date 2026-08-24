"""Deterministic recommendation tests using only mocked, user-scoped data."""
from models.ingredient import Ingredient
from models.recipe import Recipe
from services.recommendation_service import get_personalized_recommendations


def ingredient(name, status, days):
    return Ingredient(1, 1, name, "Produce", 1, "pcs", status, 5, "", 1.0, "", "", days)


def recipe(title, cuisine="Italian", meal="Dinner", minutes=30, tags=None, names=None):
    return Recipe(1, 1, title, "", cuisine, meal, tags or ["Vegetarian"], "Medium", minutes, 2,
                  [{"name": name} for name in (names or [])], [], ["Cook"], [], 80, "", True)


def test_freshness_priority_and_empty_history_are_explainable(monkeypatch):
    monkeypatch.setattr("services.recommendation_service.get_user_ingredients", lambda *_args, **_kwargs: [
        ingredient("Fresh Basil", "FRESH", 5), ingredient("Spinach", "USE SOON", 1), ingredient("Tomato", "USE TODAY", 0)
    ])
    monkeypatch.setattr("services.recommendation_service.get_saved_recipes", lambda _id: [])
    monkeypatch.setattr("services.recommendation_service.get_cooking_history", lambda _id: [])

    result = get_personalized_recommendations(1, {"cuisines": [], "dietary": []})

    assert result["rescue_ideas"][0].startswith("Use Tomato today")
    assert "Spinach" in result["rescue_ideas"][1]
    assert result["history_personalization_available"] is False
    assert result["ranked_recipes"] == []


def test_preferences_and_inventory_rank_compatible_saved_recipes(monkeypatch):
    monkeypatch.setattr("services.recommendation_service.get_user_ingredients", lambda *_args, **_kwargs: [ingredient("Tomato", "USE TODAY", 0)])
    monkeypatch.setattr("services.recommendation_service.get_cooking_history", lambda _id: [])
    monkeypatch.setattr("services.recommendation_service.get_saved_recipes", lambda _id: [
        recipe("Italian dinner", "Italian", "Dinner", 20, ["Vegetarian"], ["Tomato"]),
        recipe("Meaty dinner", "Italian", "Dinner", 10, ["Non-Vegetarian"], ["Tomato"]),
        recipe("Thai lunch", "Thai", "Lunch", 45, ["Vegetarian"], []),
    ])

    result = get_personalized_recommendations(
        1, {"cuisines": ["Italian"], "dietary": ["Vegetarian"]},
        {"diet": "Vegetarian", "cuisine": "Italian", "meal_type": "Dinner", "cooking_time_minutes": 25, "servings": 2},
    )

    assert [item["recipe"].title for item in result["ranked_recipes"]] == ["Italian dinner", "Thai lunch"]
    assert "needs using soon" in result["ranked_recipes"][0]["explanation"]
    assert "25-minute limit" in result["ranked_recipes"][0]["explanation"]


def test_other_users_saved_and_history_data_cannot_influence_result(monkeypatch):
    calls = []
    monkeypatch.setattr("services.recommendation_service.get_user_ingredients", lambda user_id, **_kwargs: calls.append(("ingredients", user_id)) or [ingredient("Carrot", "FRESH", 4)])
    monkeypatch.setattr("services.recommendation_service.get_saved_recipes", lambda user_id: calls.append(("saved", user_id)) or [recipe("User A", names=["Carrot"])])
    monkeypatch.setattr("services.recommendation_service.get_cooking_history", lambda user_id: calls.append(("history", user_id)) or [])

    result = get_personalized_recommendations(41, {"dietary": ["Vegetarian"]})

    assert result["ranked_recipes"][0]["recipe"].title == "User A"
    assert calls == [("ingredients", 41), ("saved", 41), ("history", 41)]
