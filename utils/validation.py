"""Validation utilities for Image files and Data schemas."""
import re
from io import BytesIO
from typing import Tuple, Dict, Any, List

from PIL import Image, UnidentifiedImageError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

VALID_CATEGORIES = [
    "Produce",
    "Dairy",
    "Protein",
    "Pantry",
    "Condiments",
    "Bakery",
    "Other"
]

VALID_UNITS = [
    "pcs",
    "g",
    "kg",
    "ml",
    "l",
    "bunch",
    "can",
    "cup",
    "tbsp",
    "tsp",
    "pack",
    "slice",
    "handful",
    "item"
]

def validate_image_bytes(file_bytes: bytes, filename: str = "", mime_type: str = "") -> Tuple[bool, str]:
    """
    Strictly validate image file:
    - size limit (<= 10MB)
    - binary magic number signature
    - file extension and mime type if provided
    """
    if not file_bytes:
        return False, "Image file is empty."
    
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({len(file_bytes)/(1024*1024):.1f} MB) exceeds maximum allowed 10 MB limit."

    # Binary signature check, followed by decoder verification. A matching header
    # alone is not enough: corrupted/truncated image bytes must never reach Gemini.
    is_jpeg = file_bytes.startswith(b"\xFF\xD8\xFF")
    is_png = file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    is_webp = len(file_bytes) >= 12 and file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP"

    if not (is_jpeg or is_png or is_webp):
        return False, "Invalid image format. Only real JPEG, PNG, and WebP files are supported."

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        return False, "Image data is corrupted or unreadable. Please choose another photo."

    if filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported file extension '{ext}'. Please upload JPG, PNG, or WEBP."

    if mime_type and mime_type.lower() not in ALLOWED_MIME_TYPES:
        return False, f"Unsupported MIME type '{mime_type}'."

    return True, ""

def normalize_ingredient_name(name: str) -> str:
    """Clean and normalize an ingredient name."""
    if not name:
        return ""
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", name).strip()
    return cleaned.title()

def validate_detected_ingredient(item: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
    """
    Validate and normalize a single detected ingredient from Gemini Vision output.
    Returns: (is_valid, normalized_dict, error_msg)
    """
    if not isinstance(item, dict):
        return False, {}, "Item must be a dictionary object."

    name = normalize_ingredient_name(str(item.get("name", "")))
    if not name or len(name) < 2:
        return False, {}, "Ingredient name is too short or missing."

    category = str(item.get("category", "Produce")).strip().title()
    if category not in VALID_CATEGORIES:
        category = "Other"

    raw_quantity = item.get("estimated_quantity", item.get("quantity"))
    try:
        qty = float(raw_quantity)
        if qty <= 0:
            return False, {}, "Ingredient quantity must be positive."
    except (ValueError, TypeError):
        return False, {}, "Ingredient quantity is missing or invalid."

    unit = str(item.get("unit", "pcs")).strip().lower()
    if unit not in VALID_UNITS:
        unit = "pcs"

    freshness_status = str(item.get("freshness_status", "FRESH")).strip().upper()
    if freshness_status not in ["USE TODAY", "USE SOON", "FRESH"]:
        freshness_status = "FRESH"

    try:
        shelf_life = int(item.get("estimated_shelf_life_days", item.get("estimated_shelf_life", 5)))
        if shelf_life < 0:
            shelf_life = 3
    except (ValueError, TypeError):
        shelf_life = 5

    storage_advice = str(item.get("storage_recommendation", item.get("storage_advice", "Store in a cool, dry place."))).strip()

    try:
        confidence = float(item.get("confidence", 0.9))
        confidence = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        confidence = 0.85

    normalized = {
        "name": name,
        "category": category,
        "quantity": qty,
        "unit": unit,
        "freshness_status": freshness_status,
        "estimated_shelf_life_days": shelf_life,
        "storage_advice": storage_advice,
        "confidence": confidence
    }
    return True, normalized, ""

def validate_ingredient_batch(raw_items: List[Any]) -> List[Dict[str, Any]]:
    """Validate a batch of raw detected items and return only valid normalized dictionaries."""
    valid_items = []
    if not isinstance(raw_items, list):
        return valid_items
    for item in raw_items:
        is_val, norm, _ = validate_detected_ingredient(item)
        if is_val:
            valid_items.append(norm)
    return valid_items
