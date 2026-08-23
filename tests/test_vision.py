"""Tests for Image & Vision Validation."""
import pytest
import io
from PIL import Image
from utils.validation import validate_image_bytes, validate_ingredient_batch

def test_image_validation_valid_jpeg():
    # Create valid in-memory JPEG
    img = Image.new("RGB", (100, 100), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    jpeg_bytes = buf.getvalue()

    is_valid, err = validate_image_bytes(jpeg_bytes, "fridge.jpg", "image/jpeg")
    assert is_valid is True
    assert err == ""

def test_image_validation_valid_png():
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    is_valid, err = validate_image_bytes(png_bytes, "fridge.png", "image/png")
    assert is_valid is True
    assert err == ""

def test_image_validation_invalid_signature():
    fake_bytes = b"NOT_A_REAL_IMAGE_BYTES"
    is_valid, err = validate_image_bytes(fake_bytes, "fake.jpg", "image/jpeg")
    assert is_valid is False
    assert "Invalid image format" in err

def test_image_validation_oversized():
    huge_bytes = b"\xff\xd8\xff" + b"\x00" * (11 * 1024 * 1024)
    is_valid, err = validate_image_bytes(huge_bytes, "huge.jpg", "image/jpeg")
    assert is_valid is False
    assert "exceeds maximum allowed" in err

def test_ingredient_batch_validation():
    valid_batch = [
        {"name": "Tomatoes", "category": "Produce", "quantity": 3, "unit": "pcs", "estimated_shelf_life_days": 5},
        {"name": "Milk", "category": "Dairy", "quantity": 1, "unit": "carton", "estimated_shelf_life_days": 7}
    ]
    cleaned = validate_ingredient_batch(valid_batch)
    assert len(cleaned) == 2
    assert cleaned[0]["name"] == "Tomatoes"
    assert cleaned[0]["category"] == "Produce"

    # Batch with invalid categories/negative quantities gets normalized
    unclean_batch = [
        {"name": "Apples", "category": "UnknownCat", "quantity": -5, "unit": "badunit", "estimated_shelf_life_days": -10}
    ]
    cleaned_unclean = validate_ingredient_batch(unclean_batch)
    assert len(cleaned_unclean) == 1
    assert cleaned_unclean[0]["category"] == "Other"  # normalized to valid category
    assert cleaned_unclean[0]["quantity"] == 1.0  # normalized to positive default
    assert cleaned_unclean[0]["unit"] == "pcs"  # normalized to default unit
