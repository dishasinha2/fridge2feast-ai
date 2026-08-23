"""Security and Cryptography utilities for Fridge2Feast AI."""
import hashlib
import hmac
import os
import re
from typing import Tuple

def hash_password(password: str) -> Tuple[str, str]:
    """
    Hash a plaintext password using scrypt with a cryptographically secure random 32-byte salt.
    Returns (hex_hash, hex_salt).
    """
    if not password:
        raise ValueError("Password cannot be empty")
    salt = os.urandom(32)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )
    return derived_key.hex(), salt.hex()

def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """
    Verify a plaintext password against the stored scrypt hash and salt in constant time.
    """
    if not password or not stored_hash or not stored_salt:
        return False
    try:
        salt = bytes.fromhex(stored_salt)
        derived_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=16384,
            r=8,
            p=1
        )
        return hmac.compare_digest(derived_key.hex(), stored_hash)
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or len(email) > 254:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength requirements.
    At least 8 characters, at least 1 letter, and at least 1 number.
    """
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""
