import hashlib
import hmac
import secrets
import sqlite3
from pathlib import Path

import streamlit as st
from utils.validation import validate_email, validate_password

def initialize_session_state(force_reset: bool = False):
    """
    Centralized session state initializer for Fridge2Feast AI Kitchen Decision Agent.
    Ensures strictly isolated, session-scoped runtime state across authenticated users.
    """
    defaults = {
        # Authentication & Isolation
        "authenticated": False,
        "user": None,
        "auth_view": "public_landing",  # 'public_landing', 'login', 'signup', 'app'
        "active_tab": "Dashboard",      # Default to AI Decision Dashboard
        
        # Scanner & Vision Detection
        "detected_ingredients": [],     # Perishable user inventory
        "uncertain_items": [],
        "non_food_items": [],
        "vision_summary": "",
        "scanner_in_memory_image": None,
        "scanner_in_memory_mime": "image/jpeg",
        "scanner_status": "idle",       # 'idle', 'analyzing', 'failed', 'success'
        "scanner_error_message": None,
        "scanner_is_transient_error": False,
        
        # Structured Human-in-the-Loop Vision Audit
        "hitl_vision_audit": {
            "initial_detected_count": 0,
            "confirmed_count": 0,
            "edited_count": 0,
            "removed_count": 0,
            "added_count": 0,
            "raw_detected_names": [],
        },

        # Structured Kitchen Intent & Meal Context
        "meal_context": {
            "craving": "Spicy",
            "meal_type": "Evening Snack",
            "hunger_level": "Medium",
            "household_size": 2,
            "household_type": "Couple",
            "diet": "Vegetarian",
            "spice_level": "Medium",
            "cookingTime": "Under 30 minutes",
            "difficulty": "Easy",
            "budgetINR": 150,
            "avoid_list": [],
            "dietaryRestrictions": [],
            "optimization_objective": "Balanced",
        },
        
        # Personal Taste Profile (Learns from user feedback without claiming model retraining)
        "taste_profile": {
            "favorite_cuisines": ["Indian"],
            "disliked_ingredients": [],
            "preferred_spice": "Medium",
            "preferred_speed": "Under 30 mins",
            "recipes_cooked_count": 0,
            "ingredients_rescued_count": 0,
            "ratings_history": [],
            "repeat_cook_count": 0,
            "rejected_count": 0,
        },
        
        # Recipe & Decision Engine
        "generated_recipes": [],
        "selected_recipe": None,
        "rescue_plan": None,
        "meal_plan": None,
        "leftover_suggestions": None,
        "saved_recipes": [],
        "cooking_recipe": None,
        "cooking_step": 0,
        "shopping_recipe": None,
        
        # Reminders & Feedback
        "active_reminders": [],
        "last_feedback": None,
        
        # Sous-Chef Chat Messages
        "sous_chef_messages": [
            {
                "role": "assistant",
                "content": "Hello Chef! I am your AI Kitchen Decision Sous-Chef. Ask me for ingredient substitutions, freshness advice, or cooking techniques!"
            }
        ],
        
        # AI Telemetry & Observability
        "ai_telemetry": {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "errors_503": 0,
            "errors_429": 0,
            "timeouts": 0,
            "validation_failures": 0,
            "latencies_ms": [],
        }
    }

    for key, value in defaults.items():
        if force_reset or key not in st.session_state:
            st.session_state[key] = value

def init_auth_state():
    """Alias for backwards compatibility."""
    initialize_session_state(force_reset=False)

def login_user(email: str, name: str = None) -> bool:
    """
    Logs in user with clean, isolated session state.
    """
    display_name = name or (email.split('@')[0].capitalize() if '@' in email else 'Chef')
    st.session_state.authenticated = True
    st.session_state.user = {
        "name": display_name,
        "email": email,
        "plan": "Pro Zero-Waste",
    }
    st.session_state.auth_view = "app"
    return True

USER_DATABASE = Path(__file__).resolve().parent.parent / "data" / "fridge2feast_users.db"


def _connection() -> sqlite3.Connection:
    """Return the local account store, creating its schema on first use."""
    USER_DATABASE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(USER_DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)
    return conn


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1).hex()


def authenticate_user(email: str, password: str) -> tuple[bool, str | None]:
    """Authenticate a local account without ever storing a plain-text password."""
    normalized_email = (email or "").strip().lower()
    with _connection() as conn:
        row = conn.execute(
            "SELECT name, password_hash, salt FROM users WHERE email = ?", (normalized_email,)
        ).fetchone()
    if not row:
        return False, None
    expected = _hash_password(password, bytes.fromhex(row[2]))
    return hmac.compare_digest(expected, row[1]), row[0]


def signup_user(name: str, email: str, password: str) -> tuple[bool, str | None]:
    """
    Creates an authenticated, session-scoped user without persisting credentials.
    """
    normalized_name = " ".join((name or "").split())
    normalized_email = (email or "").strip().lower()

    if not normalized_name or not validate_email(normalized_email) or not validate_password(password):
        return False, "Please complete all fields with a valid email and stronger password."

    salt = secrets.token_bytes(16)
    password_hash = _hash_password(password, salt)
    try:
        with _connection() as conn:
            conn.execute(
                "INSERT INTO users (email, name, password_hash, salt) VALUES (?, ?, ?, ?)",
                (normalized_email, normalized_name, password_hash, salt.hex()),
            )
    except sqlite3.IntegrityError:
        return False, "An account already exists for this email. Please log in instead."

    st.session_state.authenticated = True
    st.session_state.user = {
        "name": normalized_name,
        "email": normalized_email,
        "plan": "Pro Zero-Waste",
    }
    st.session_state.auth_view = "app"
    return True, None

def logout_user():
    """
    Safely purges all session state and returns to landing.
    """
    st.session_state.clear()
    initialize_session_state(force_reset=True)
    st.session_state.auth_view = "public_landing"
