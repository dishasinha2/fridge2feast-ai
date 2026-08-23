"""Tests for Authentication & Cryptography."""
import pytest
import os
import tempfile
from utils.database import init_db
from utils.security import hash_password, verify_password, validate_password_strength, validate_email
from services.auth_service import signup_user, login_user, get_user_by_id

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Create isolated SQLite test database for each test run."""
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

def test_password_hashing_and_verification():
    raw_pwd = "SecretPassword123"
    h, salt = hash_password(raw_pwd)
    assert len(h) == 128  # scrypt hex hash
    assert len(salt) == 64  # 32 bytes hex salt
    assert verify_password(raw_pwd, h, salt) is True
    assert verify_password("WrongPassword123", h, salt) is False

def test_user_signup_and_login():
    user, err = signup_user("chef.sarah@example.com", "Sarah Jenkins", "CulinaryArt99")
    assert err == ""
    assert user is not None
    assert user.email == "chef.sarah@example.com"
    assert user.name == "Sarah Jenkins"
    assert user.id is not None

    # Duplicate signup should fail
    dup_user, dup_err = signup_user("chef.sarah@example.com", "Sarah Copy", "AnotherPass123")
    assert dup_user is None
    assert "already exists" in dup_err

    # Successful login
    logged_in, log_err = login_user("chef.sarah@example.com", "CulinaryArt99")
    assert log_err == ""
    assert logged_in is not None
    assert logged_in.id == user.id

    # Invalid password login
    bad_login, bad_err = login_user("chef.sarah@example.com", "WrongPass123")
    assert bad_login is None
    assert "Invalid email or password" in bad_err

def test_password_strength_validation():
    valid, _ = validate_password_strength("ValidPass123")
    assert valid is True

    too_short, _ = validate_password_strength("Pass1")
    assert too_short is False

    no_number, _ = validate_password_strength("NoNumberPass")
    assert no_number is False
