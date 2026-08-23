"""Authentication Service for Fridge2Feast AI."""
import json
from typing import Optional, Tuple, Dict, Any
from utils.database import get_db_connection
from utils.security import hash_password, verify_password, validate_email, validate_password_strength
from models.user import User

def signup_user(email: str, name: str, password: str) -> Tuple[Optional[User], str]:
    """
    Register a new user with scrypt password hash and salt.
    Returns (User, "") on success, or (None, error_message) on failure.
    """
    email_clean = email.strip().lower()
    name_clean = name.strip()

    if not name_clean or len(name_clean) < 2:
        return None, "Please enter your full name."

    if not validate_email(email_clean):
        return None, "Please enter a valid email address."

    is_valid_pw, pw_err = validate_password_strength(password)
    if not is_valid_pw:
        return None, pw_err

    # Check if user already exists
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?;", (email_clean,))
        if cursor.fetchone():
            return None, "An account with this email already exists."

        # Hash password
        pwd_hash, salt = hash_password(password)

        cursor.execute(
            """
            INSERT INTO users (email, name, password_hash, salt)
            VALUES (?, ?, ?, ?);
            """,
            (email_clean, name_clean, pwd_hash, salt)
        )
        user_id = cursor.lastrowid

        # Initialize default preferences
        default_prefs = {
            "cuisines": ["Indian", "Italian", "Mexican"],
            "dietary": ["Vegetarian"],
            "spice_level": "Medium",
            "default_servings": 2,
            "prioritized_ingredients": [],
            "avoided_ingredients": []
        }
        cursor.execute(
            """
            INSERT INTO preferences (user_id, cuisines, dietary, spice_level, default_servings, prioritized_ingredients, avoided_ingredients)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                user_id,
                json.dumps(default_prefs["cuisines"]),
                json.dumps(default_prefs["dietary"]),
                default_prefs["spice_level"],
                default_prefs["default_servings"],
                json.dumps(default_prefs["prioritized_ingredients"]),
                json.dumps(default_prefs["avoided_ingredients"])
            )
        )

        cursor.execute("SELECT id, email, name, created_at FROM users WHERE id = ?;", (user_id,))
        row = cursor.fetchone()
        user = User(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            created_at=str(row["created_at"]),
            preferences=default_prefs
        )
        return user, ""

def login_user(email: str, password: str) -> Tuple[Optional[User], str]:
    """
    Authenticate user using scrypt constant-time hash comparison.
    Returns (User, "") on success, or (None, error_message) on failure.
    """
    email_clean = email.strip().lower()
    if not email_clean or not password:
        return None, "Please enter both email and password."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, name, password_hash, salt, created_at FROM users WHERE email = ?;",
            (email_clean,)
        )
        row = cursor.fetchone()
        if not row:
            return None, "Invalid email or password."

        stored_hash = row["password_hash"]
        stored_salt = row["salt"]

        if not verify_password(password, stored_hash, stored_salt):
            return None, "Invalid email or password."

        user_id = row["id"]
        # Fetch preferences
        cursor.execute("SELECT * FROM preferences WHERE user_id = ?;", (user_id,))
        pref_row = cursor.fetchone()
        preferences = {}
        if pref_row:
            try:
                preferences = {
                    "cuisines": json.loads(pref_row["cuisines"]),
                    "dietary": json.loads(pref_row["dietary"]),
                    "spice_level": pref_row["spice_level"],
                    "default_servings": pref_row["default_servings"],
                    "prioritized_ingredients": json.loads(pref_row["prioritized_ingredients"]),
                    "avoided_ingredients": json.loads(pref_row["avoided_ingredients"])
                }
            except Exception:
                preferences = {"cuisines": ["Italian"], "dietary": [], "spice_level": "Medium", "default_servings": 2}

        user = User(
            id=user_id,
            email=row["email"],
            name=row["name"],
            created_at=str(row["created_at"]),
            preferences=preferences
        )
        return user, ""

def get_user_by_id(user_id: int) -> Optional[User]:
    """Retrieve user object by ID."""
    if not user_id:
        return None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, created_at FROM users WHERE id = ?;", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        cursor.execute("SELECT * FROM preferences WHERE user_id = ?;", (user_id,))
        pref_row = cursor.fetchone()
        preferences = {}
        if pref_row:
            try:
                preferences = {
                    "cuisines": json.loads(pref_row["cuisines"]),
                    "dietary": json.loads(pref_row["dietary"]),
                    "spice_level": pref_row["spice_level"],
                    "default_servings": pref_row["default_servings"],
                    "prioritized_ingredients": json.loads(pref_row["prioritized_ingredients"]),
                    "avoided_ingredients": json.loads(pref_row["avoided_ingredients"])
                }
            except Exception:
                pass
        return User(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            created_at=str(row["created_at"]),
            preferences=preferences
        )

def update_user_preferences(user_id: int, preferences: Dict[str, Any]) -> bool:
    """Update user culinary preferences in SQLite."""
    if not user_id:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO preferences (user_id, cuisines, dietary, spice_level, default_servings, prioritized_ingredients, avoided_ingredients, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                cuisines = excluded.cuisines,
                dietary = excluded.dietary,
                spice_level = excluded.spice_level,
                default_servings = excluded.default_servings,
                prioritized_ingredients = excluded.prioritized_ingredients,
                avoided_ingredients = excluded.avoided_ingredients,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (
                user_id,
                json.dumps(preferences.get("cuisines", [])),
                json.dumps(preferences.get("dietary", [])),
                preferences.get("spice_level", "Medium"),
                preferences.get("default_servings", 2),
                json.dumps(preferences.get("prioritized_ingredients", [])),
                json.dumps(preferences.get("avoided_ingredients", []))
            )
        )
        return True
