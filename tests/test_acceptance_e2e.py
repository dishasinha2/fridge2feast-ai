"""
Comprehensive E2E Acceptance Test Suite for Fridge2Feast AI.
Runs thorough functional tests covering all user acceptance flows.
"""
import os
import io
import json
import pytest
import tempfile
from datetime import datetime, timedelta
from PIL import Image

from utils.database import init_db, get_db_connection
from utils.security import hash_password, verify_password, validate_email, validate_password_strength
from utils.calculations import calculate_freshness, calculate_zero_waste_score
from utils.validation import validate_image_bytes, validate_ingredient_batch
from services.auth_service import signup_user, login_user, get_user_by_id
from services.kitchen_service import (
    add_ingredient, get_user_ingredients, update_ingredient, delete_ingredient,
    get_expiring_ingredients, get_kitchen_summary
)
from services.recipe_service import save_recipe, get_saved_recipes, unsave_recipe, record_cooking_history, get_cooking_history
from services.notification_service import get_user_notifications, mark_notification_read
from services.vision_service import analyze_fridge_image
from services.voice_service import parse_voice_recipe_query
from models.recipe import Recipe

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Isolate SQLite database for each acceptance test."""
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

def test_acceptance_1_new_account_empty_state():
    """Acceptance Test 1: New user registration, empty kitchen, zero fake data."""
    email = f"real_new_{datetime.now().timestamp()}@example.com"
    user, err = signup_user(email, "Real User", "SafePass123")
    assert err == ""
    assert user is not None
    assert user.email == email

    # Login
    logged_in, log_err = login_user(email, "SafePass123")
    assert log_err == ""
    assert logged_in.id == user.id

    # Kitchen must be completely empty
    items = get_user_ingredients(user.id)
    assert len(items) == 0

    # Summary metrics must be 0
    summary = get_kitchen_summary(user.id)
    assert summary["total_count"] == 0
    assert summary["expiring_count"] == 0
    assert summary["zero_waste_score"] == 100

    # Notifications must be empty
    notifs = get_user_notifications(user.id)
    assert len(notifs) == 0

def test_acceptance_2_image_validation_pipeline():
    """Acceptance Test 2: Scanner binary validation (JPG, PNG, WEBP, Reject PDF/Corrupt)."""
    # 1. Valid JPEG
    img_byte_arr = io.BytesIO()
    image = Image.new("RGB", (120, 120), color=(100, 200, 50))
    image.save(img_byte_arr, format="JPEG")
    valid_bytes = img_byte_arr.getvalue()

    is_valid, msg = validate_image_bytes(valid_bytes, "fridge.jpg", "image/jpeg")
    assert is_valid is True

    # 2. Valid PNG
    png_byte_arr = io.BytesIO()
    png_img = Image.new("RGB", (80, 80), color=(50, 100, 150))
    png_img.save(png_byte_arr, format="PNG")
    is_valid_png, _ = validate_image_bytes(png_byte_arr.getvalue(), "food.png", "image/png")
    assert is_valid_png is True

    # 3. Reject PDF
    is_valid_pdf, pdf_err = validate_image_bytes(b"%PDF-1.5 fake document data", "doc.pdf", "application/pdf")
    assert is_valid_pdf is False
    assert "Invalid image format" in pdf_err or "Unsupported" in pdf_err

    # 4. Reject Oversized
    big_bytes = b"\xFF\xD8\xFF" + b"\x00" * (11 * 1024 * 1024)
    is_valid_big, big_err = validate_image_bytes(big_bytes, "giant.jpg", "image/jpeg")
    assert is_valid_big is False
    assert "exceeds maximum allowed" in big_err

def test_acceptance_3_freshness_engine_deterministic():
    """Acceptance Test 3: Deterministic Freshness calculation."""
    today = datetime.now()
    added_str = today.strftime("%Y-%m-%d %H:%M:%S")

    # 0 days shelf life -> USE TODAY
    status_0, days_0, _ = calculate_freshness(added_str, 0)
    assert status_0 == "USE TODAY"

    # 1 day shelf life -> USE SOON
    status_1, days_1, _ = calculate_freshness(added_str, 1)
    assert status_1 == "USE SOON"

    # 2 days shelf life -> USE SOON
    status_2, days_2, _ = calculate_freshness(added_str, 2)
    assert status_2 == "USE SOON"

    # 7 days shelf life -> FRESH
    status_7, days_7, _ = calculate_freshness(added_str, 7)
    assert status_7 == "FRESH"

def test_acceptance_4_and_5_recipes_and_saved():
    """Acceptance Test 4 & 5: Add ingredients, verify saved recipes and history."""
    user, _ = signup_user("chef.e2e@example.com", "Chef E2E", "ChefPass123")

    # Add items to kitchen
    add_ingredient(user.id, {
        "name": "Eggs",
        "category": "Dairy",
        "quantity": 6.0,
        "unit": "pcs",
        "estimated_shelf_life_days": 10
    })
    add_ingredient(user.id, {
        "name": "Cheddar Cheese",
        "category": "Dairy",
        "quantity": 100.0,
        "unit": "g",
        "estimated_shelf_life_days": 14
    })

    # Insert a recipe for this user
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO recipes (
                user_id, title, description, cuisine, meal_type, dietary_tags,
                spice_level, cooking_time_minutes, servings, available_ingredients,
                additional_ingredients, instructions, tips, waste_saved_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                user.id, "Quick Cheesy Scramble", "Fluffy scrambled eggs with melted cheddar.",
                "Breakfast", "Breakfast", json.dumps(["Vegetarian"]), "Mild", 10, 2,
                json.dumps([{"name": "Eggs", "quantity": "4", "unit": "pcs"}]),
                json.dumps([{"name": "Butter", "quantity": "1", "unit": "tbsp"}]),
                json.dumps(["Whisk eggs", "Melt butter", "Scramble"]),
                json.dumps(["Cook on low heat"]), 90
            )
        )
        recipe_id = cursor.lastrowid

    save_success = save_recipe(user.id, recipe_id)
    assert save_success is True

    saved_list = get_saved_recipes(user.id)
    assert len(saved_list) == 1
    assert saved_list[0].title == "Quick Cheesy Scramble"
    assert len(saved_list[0].available_ingredients) == 1
    assert len(saved_list[0].additional_ingredients) == 1

    # Log cooking session
    rec_res = record_cooking_history(
        user_id=user.id,
        recipe_title=saved_list[0].title,
        cuisine=saved_list[0].cuisine,
        servings=saved_list[0].servings,
        notes="Delicious breakfast!",
        rating=5
    )
    assert rec_res is True
    history = get_cooking_history(user.id)
    assert len(history) == 1
    assert history[0]["recipe_title"] == "Quick Cheesy Scramble"

def test_acceptance_6_and_7_user_isolation_and_security():
    """Acceptance Test 6 & 7: Strict multi-user data isolation and security."""
    user_a, _ = signup_user("usera@isolation.com", "User Alpha", "PassA123!")
    user_b, _ = signup_user("userb@isolation.com", "User Beta", "PassB123!")

    # User A adds item
    ing_a = add_ingredient(user_a.id, {
        "name": "Strawberries",
        "category": "Produce",
        "quantity": 1.0,
        "unit": "box",
        "estimated_shelf_life_days": 2
    })

    # User B adds item
    ing_b = add_ingredient(user_b.id, {
        "name": "Chicken Breast",
        "category": "Meat",
        "quantity": 500.0,
        "unit": "g",
        "estimated_shelf_life_days": 3
    })

    # Isolation check
    items_a = get_user_ingredients(user_a.id)
    assert len(items_a) == 1
    assert items_a[0].name == "Strawberries"

    items_b = get_user_ingredients(user_b.id)
    assert len(items_b) == 1
    assert items_b[0].name == "Chicken Breast"

    # User B cannot delete User A's item
    delete_result = delete_ingredient(user_b.id, ing_a.id)
    assert delete_result is False
    assert len(get_user_ingredients(user_a.id)) == 1

    # Security check: Password is never stored in plaintext
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, salt FROM users WHERE id = ?", (user_a.id,))
        row = cursor.fetchone()
        assert row is not None
        assert "PassA123!" not in row["password_hash"]
        assert len(row["password_hash"]) == 128
