"""Centralized Streamlit session-state defaults and user cleanup."""
from typing import Any, MutableMapping

DEFAULT_SESSION_STATE = {
    "authenticated_user": None,
    "current_page": "landing",
    "auth_view": "login",
    "latest_scan": None,
    "scan_confirmed": False,
    "last_scan_ingredients": [],
    "pending_scan_items": None,
    "recipe_preferences": {},
    "generated_recipe": None,
    "recipe_flow_stage": "preferences",
    "active_recipe": None,
    "cooking_recipe": None,
    "current_step_idx": 0,
    "rescue_mode": False,
}

USER_SESSION_KEYS = (
    "authenticated_user",
    "current_page",
    "auth_view",
    "latest_scan",
    "scan_confirmed",
    "last_scan_ingredients",
    "pending_scan_items",
    "recipe_preferences",
    "generated_recipe",
    "recipe_flow_stage",
    "active_recipe",
    "cooking_recipe",
    "current_step_idx",
    "rescue_mode",
)


def initialize_session_state(state: MutableMapping[str, Any]) -> None:
    """Add missing defaults without overwriting values across Streamlit reruns."""
    for key, default in DEFAULT_SESSION_STATE.items():
        if key not in state:
            state[key] = default.copy() if isinstance(default, (dict, list)) else default


def clear_user_session_state(state: MutableMapping[str, Any]) -> None:
    """Clear transient authenticated workflow state while retaining app configuration."""
    for key in USER_SESSION_KEYS:
        default = DEFAULT_SESSION_STATE[key]
        state[key] = default.copy() if isinstance(default, (dict, list)) else default
