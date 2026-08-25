"""Gemini Vision Service for Fridge and Pantry Ingredient Recognition."""
import json
import re
import logging
import os
import time
from io import BytesIO
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageOps
from utils.validation import validate_image_bytes, validate_detected_ingredient
from services.gemini_client import generate_json_content, get_gemini_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_VISION_IMAGE_EDGE = 1280
VISION_JPEG_QUALITY = 80
VISION_REQUEST_TIMEOUT_MS = 20_000
# This exact model has been verified with the configured project key. A fallback
# is disabled by default so an unknown model can never create a second long wait.
VISION_MODEL = "gemini-3.6-flash"
VISION_FALLBACK_MODEL = os.getenv("GEMINI_VISION_FALLBACK_MODEL") or None

VISION_PROMPT = """
Identify distinct food ingredients visible in this refrigerator or pantry image.

For each detected ingredient, output a strictly valid JSON array of objects with the following keys:
- "name": string, clear singular/standardized food name (e.g. "Tomatoes", "Milk", "Eggs", "Cheddar Cheese", "Bell Pepper", "Spinach", "Tofu")
- "category": one of ["Produce", "Dairy", "Protein", "Pantry", "Condiments", "Bakery", "Other"]
- "estimated_quantity": number (e.g. 1, 2, 0.5)
- "unit": one of ["pcs", "g", "kg", "ml", "l", "bunch", "can", "cup", "tbsp", "tsp", "pack", "slice", "handful", "item"]
- "freshness_status": based on visual inspection, one of ["USE TODAY", "USE SOON", "FRESH"]
- "estimated_shelf_life_days": integer estimated remaining days until optimal freshness expires
- "storage_recommendation": short storage tip
- "confidence": float between 0.0 and 1.0 representing detection confidence

Return only the JSON array. No explanation, recipe, or markdown.
"""


def prepare_image_for_vision(image_bytes: bytes) -> Tuple[bytes, str]:
    """Shrink photos for fast vision inference without losing food-level detail.

    Phone images are commonly 4K+ and several megabytes. Gemini needs a clear
    view of shelves, not the original camera resolution; a 1280px JPEG greatly
    reduces upload and model processing time while retaining usable detail.
    """
    with Image.open(BytesIO(image_bytes)) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "L"):
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.getchannel("A") if "A" in image.getbands() else None)
            image = background
        elif image.mode == "L":
            image = image.convert("RGB")
        image.thumbnail((MAX_VISION_IMAGE_EDGE, MAX_VISION_IMAGE_EDGE), Image.Resampling.LANCZOS)
        output = BytesIO()
        image.save(output, format="JPEG", quality=VISION_JPEG_QUALITY, optimize=True)
    return output.getvalue(), "image/jpeg"

def analyze_fridge_image(image_bytes: bytes, filename: str = "", mime_type: str = "") -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Validate image and send to Gemini Vision for structured ingredient detection.
    Returns (success, list_of_validated_ingredients, user_facing_error_message).
    """
    if not isinstance(image_bytes, bytes):
        logger.error("Vision received invalid image payload type=%s", type(image_bytes).__name__)
        return False, [], "Image data is invalid. Please upload the photo again."

    total_started = time.perf_counter()
    input_byte_count = len(image_bytes)
    # 1. Strict image validation
    validation_started = time.perf_counter()
    is_valid_img, img_err = validate_image_bytes(image_bytes, filename, mime_type)
    logger.info(
        "Vision image validation completed duration_ms=%d byte_count=%d mime_type=%s valid=%s",
        (time.perf_counter() - validation_started) * 1000,
        input_byte_count,
        mime_type or "unknown",
        is_valid_img,
    )
    if not is_valid_img:
        return False, [], img_err

    preprocess_started = time.perf_counter()
    try:
        image_bytes, mime_type = prepare_image_for_vision(image_bytes)
    except (OSError, ValueError) as error:
        logger.error("Image preparation failed: %s", error)
        return False, [], "Image data is corrupted or unreadable. Please choose another photo."
    logger.info(
        "Vision image preprocessing completed duration_ms=%d input_byte_count=%d output_byte_count=%d mime_type=%s",
        (time.perf_counter() - preprocess_started) * 1000,
        input_byte_count,
        len(image_bytes),
        mime_type,
    )

    # 2. Call Gemini
    try:
        client = get_gemini_client()
        detected_raw = None

        # Check client type (Google GenAI official SDK vs fallback)
        if hasattr(client, "models") and hasattr(client.models, "generate_content"):
            from google.genai import types
            
            # Keep the actual binary JPEG as a Gemini multimodal image part.
            part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            request_started = time.perf_counter()
            logger.info("Vision Gemini request starting model=%s timeout_ms=%d", VISION_MODEL, VISION_REQUEST_TIMEOUT_MS)
            detected_raw = generate_json_content(
                [VISION_PROMPT, part],
                temperature=0.1,
                max_output_tokens=1200,
                primary_model=VISION_MODEL,
                fallback_model=VISION_FALLBACK_MODEL,
                request_timeout_ms=VISION_REQUEST_TIMEOUT_MS,
                client=client,
            )
            logger.info(
                "Vision Gemini response received duration_ms=%d model=%s response_length=%d",
                (time.perf_counter() - request_started) * 1000,
                VISION_MODEL,
                len(detected_raw or ""),
            )
        else:
            # Legacy google.generativeai fallback
            import PIL.Image
            import io
            img = PIL.Image.open(io.BytesIO(image_bytes))
            model = client.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([VISION_PROMPT, img])
            detected_raw = response.text

        if not detected_raw:
            return False, [], "No ingredients could be detected in this image. Please try taking a clearer photo."

        parse_started = time.perf_counter()
        # Parse JSON
        cleaned_text = detected_raw.strip()
        # Remove any stray codeblocks if model added them
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```(?:json)?", "", cleaned_text)
            cleaned_text = re.sub(r"```$", "", cleaned_text)
            cleaned_text = cleaned_text.strip()

        data = json.loads(cleaned_text)
        logger.info("Vision JSON parsing completed duration_ms=%d", (time.perf_counter() - parse_started) * 1000)
        if isinstance(data, dict):
            # If wrapped in a key like {"ingredients": [...]}
            for key in ["ingredients", "items", "detected_ingredients", "data"]:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            if isinstance(data, dict):
                data = [data]

        if not isinstance(data, list):
            return False, [], "Ingredient scanning is temporarily unavailable. Please try again."

        # Validate and deduplicate items
        validated_items: List[Dict[str, Any]] = []
        seen_names = set()

        for item in data:
            is_valid, norm_item, _ = validate_detected_ingredient(item)
            if is_valid:
                norm_name = norm_item["name"].lower()
                if norm_name not in seen_names:
                    seen_names.add(norm_name)
                    validated_items.append(norm_item)

        logger.info(
            "Vision ingredient validation completed duration_ms=%d valid_item_count=%d",
            (time.perf_counter() - parse_started) * 1000,
            len(validated_items),
        )
        if not validated_items:
            return False, [], "No valid ingredients identified in the photo. Please try a different angle."

        logger.info("Vision result returned total_duration_ms=%d item_count=%d", (time.perf_counter() - total_started) * 1000, len(validated_items))
        return True, validated_items, ""

    except json.JSONDecodeError as error:
        logger.exception("Vision JSON parsing failed error_type=%s message=%s", type(error).__name__, error)
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
    except ValueError as error:
        # A missing key cannot be fixed by retrying; make the setup action clear.
        logger.exception("Gemini vision configuration error error_type=%s message=%s", type(error).__name__, error)
        if "GEMINI_API_KEY" in str(error):
            return False, [], "Gemini is not configured. Add GEMINI_API_KEY to .streamlit/secrets.toml, then restart the app."
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
    except Exception as e:
        logger.exception("Gemini vision request failed error_type=%s message=%s", type(e).__name__, e)
        if "timeout" in type(e).__name__.lower() or "timeout" in str(e).lower():
            return False, [], "Ingredient scanning timed out after 20 seconds. Please try a clearer photo."
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
