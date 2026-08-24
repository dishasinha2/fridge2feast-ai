"""Tests for Image & Vision Validation."""
import pytest
import io
import json
from PIL import Image
from utils.validation import validate_image_bytes, validate_ingredient_batch
from services.vision_service import analyze_fridge_image

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


def test_image_validation_valid_webp():
    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    is_valid, err = validate_image_bytes(buf.getvalue(), "fridge.webp", "image/webp")
    assert is_valid is True
    assert err == ""

def test_image_validation_invalid_signature():
    fake_bytes = b"NOT_A_REAL_IMAGE_BYTES"
    is_valid, err = validate_image_bytes(fake_bytes, "fake.jpg", "image/jpeg")
    assert is_valid is False
    assert "Invalid image format" in err


def test_image_validation_rejects_corrupt_magic_bytes():
    is_valid, err = validate_image_bytes(b"\xff\xd8\xffnot-a-real-jpeg", "fridge.jpg", "image/jpeg")
    assert is_valid is False
    assert "corrupted or unreadable" in err

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

    # Invalid quantities are rejected so malformed model records cannot be saved.
    unclean_batch = [
        {"name": "Apples", "category": "UnknownCat", "quantity": -5, "unit": "badunit", "estimated_shelf_life_days": -10}
    ]
    cleaned_unclean = validate_ingredient_batch(unclean_batch)
    assert cleaned_unclean == []


def test_gemini_vision_output_is_validated_before_inventory_confirmation(monkeypatch):
    class FakeModels:
        def generate_content(self, **kwargs):
            self.contents = kwargs["contents"]
            return type("Response", (), {"text": json.dumps([
                {"name": "tomatoes", "category": "Produce", "estimated_quantity": 2,
                 "unit": "pcs", "freshness_status": "USE SOON", "confidence": 0.9},
                {"name": "?", "estimated_quantity": 1},
            ])})()

    models = FakeModels()
    monkeypatch.setattr("services.vision_service.get_gemini_client", lambda: type("Client", (), {"models": models})())
    image = Image.new("RGB", (10, 10), color="green")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    success, items, error = analyze_fridge_image(buffer.getvalue(), "fridge.jpg", "image/jpeg")

    assert success and not error
    assert items == [items[0]]
    assert items[0]["name"] == "Tomatoes"
    assert len(models.contents) == 2  # Prompt plus a Gemini image part, never raw unvalidated inventory.
