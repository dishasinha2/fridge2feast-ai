"""Focused scanner confirmation, isolation, and failure tests; all vision calls are mocked."""
import io
import os
import tempfile

import pytest
from PIL import Image

from components.scanner import confirm_scan_items
from services.auth_service import signup_user
from services.kitchen_service import get_user_ingredients
from services.vision_service import analyze_fridge_image
from utils.database import init_db


@pytest.fixture(autouse=True)
def database(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        path = handle.name
    monkeypatch.setenv("FRIDGE2FEAST_DB_PATH", path)
    init_db()
    yield
    os.remove(path)


def _jpeg_bytes():
    image = Image.new("RGB", (10, 10), color="green")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_unconfirmed_scan_never_writes_and_confirmed_scan_is_user_scoped():
    user_a, _ = signup_user("scan.a@example.com", "Scanner A", "Password123")
    user_b, _ = signup_user("scan.b@example.com", "Scanner B", "Password123")
    review_items = [{"name": "Tomato", "category": "Produce", "quantity": 2,
                     "unit": "pcs", "estimated_shelf_life_days": 1}]

    # Detection/review data is transient; no mutation happens before confirmation.
    assert get_user_ingredients(user_a.id) == []
    added, handoff = confirm_scan_items(user_a.id, review_items)

    assert [item.name for item in added] == ["Tomato"]
    assert [item["name"] for item in handoff] == ["Tomato"]
    assert handoff[0]["freshness_status"] == "USE SOON"
    assert [item.name for item in get_user_ingredients(user_a.id)] == ["Tomato"]
    assert get_user_ingredients(user_b.id) == []


def test_invalid_review_item_is_not_persisted():
    user, _ = signup_user("invalid.scan@example.com", "Scanner", "Password123")
    added, handoff = confirm_scan_items(user.id, [{"name": "Milk", "quantity": -1}])
    assert added == [] and handoff == []
    assert get_user_ingredients(user.id) == []


def test_malformed_or_failed_gemini_vision_leaves_inventory_untouched(monkeypatch):
    user, _ = signup_user("vision.failure@example.com", "Vision", "Password123")

    class BadModels:
        def generate_content(self, **kwargs):
            return type("Response", (), {"text": "not-json"})()

    monkeypatch.setattr("services.vision_service.get_gemini_client", lambda: type("Client", (), {"models": BadModels()})())
    success, items, error = analyze_fridge_image(_jpeg_bytes(), "fridge.jpg", "image/jpeg")
    assert not success and items == [] and "temporarily unavailable" in error
    assert get_user_ingredients(user.id) == []
