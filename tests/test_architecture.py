"""Focused tests for technical architecture boundaries."""
from datetime import date
from types import SimpleNamespace

from utils.pandas_utils import inventory_to_freshness_df
from utils.session_state import clear_user_session_state, initialize_session_state


def test_session_state_initialization_preserves_existing_values():
    state = {"current_page": "recipes", "recipe_preferences": {"spice_level": "Spicy"}}

    initialize_session_state(state)

    assert state["current_page"] == "recipes"
    assert state["recipe_preferences"] == {"spice_level": "Spicy"}
    assert state["authenticated_user"] is None
    assert state["latest_scan"] is None
    assert state["scan_confirmed"] is False


def test_user_session_cleanup_clears_workflow_state():
    state = {
        "authenticated_user": object(),
        "current_page": "recipes",
        "latest_scan": [{"name": "Tomato"}],
        "scan_confirmed": True,
        "recipe_preferences": {"spice_level": "Spicy"},
        "generated_recipe": object(),
        "recipe_flow_stage": "scan_complete",
        "unrelated_config": "keep",
    }

    clear_user_session_state(state)

    assert state["authenticated_user"] is None
    assert state["current_page"] == "landing"
    assert state["latest_scan"] is None
    assert state["scan_confirmed"] is False
    assert state["recipe_preferences"] == {}
    assert state["generated_recipe"] is None
    assert state["recipe_flow_stage"] == "preferences"
    assert state["unrelated_config"] == "keep"


def test_inventory_dataframe_uses_existing_freshness_rules_and_handles_bad_values():
    today = date.today()
    records = [
        SimpleNamespace(id=1, name="Tomato", category="Produce", quantity="2", unit="pcs", added_date=today.isoformat(), estimated_shelf_life_days=1),
        {"id": 2, "name": "Rice", "category": "Pantry", "quantity": "bad", "unit": "kg", "added_date": "not-a-date", "estimated_shelf_life_days": "bad"},
    ]

    dataframe = inventory_to_freshness_df(records)

    assert list(dataframe["name"]) == ["Tomato", "Rice"]
    assert dataframe.loc[0, "days_remaining"] == 1
    assert dataframe.loc[0, "freshness_status"] == "USE SOON"
    assert dataframe.loc[1, "quantity"] == 0.0
    assert dataframe.loc[1, "freshness_status"] == "USE TODAY"
    assert dataframe["expiry_date"].notna().all()


def test_inventory_dataframe_handles_empty_input():
    dataframe = inventory_to_freshness_df([])

    assert dataframe.empty
    assert "freshness_status" in dataframe.columns