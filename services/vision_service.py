"""Gemini Vision Service for Fridge and Pantry Ingredient Recognition."""
import json
import re
import logging
from io import BytesIO
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageOps
from utils.validation import validate_image_bytes, validate_detected_ingredient
from services.gemini_client import generate_json_content, get_gemini_client

logger = logging.getLogger(__name__)

MAX_VISION_IMAGE_EDGE = 1600
VISION_JPEG_QUALITY = 82

VISION_PROMPT = """
You are Fridge2Feast AI, an expert computer vision model for refrigerator and pantry food detection.
Analyze this photo of a refrigerator or pantry. Identify ALL distinct food ingredients, produce, dairy, proteins, condiments, and pantry items visible in the image.

For each detected ingredient, output a strictly valid JSON array of objects with the following keys:
- "name": string, clear singular/standardized food name (e.g. "Tomatoes", "Milk", "Eggs", "Cheddar Cheese", "Bell Pepper", "Spinach", "Tofu")
- "category": one of ["Produce", "Dairy", "Protein", "Pantry", "Condiments", "Bakery", "Other"]
- "estimated_quantity": number (e.g. 1, 2, 0.5)
- "unit": one of ["pcs", "g", "kg", "ml", "l", "bunch", "can", "cup", "tbsp", "tsp", "pack", "slice", "handful", "item"]
- "freshness_status": based on visual inspection, one of ["USE TODAY", "USE SOON", "FRESH"]
- "estimated_shelf_life_days": integer estimated remaining days until optimal freshness expires
- "storage_recommendation": brief practical storage tip (e.g. "Store in high humidity crisper drawer")
- "confidence": float between 0.0 and 1.0 representing detection confidence

Output ONLY the raw JSON array. Do NOT wrap in markdown backticks or include introductory or concluding commentary.
"""


def prepare_image_for_vision(image_bytes: bytes) -> Tuple[bytes, str]:
    """Shrink photos for fast vision inference without losing food-level detail.

    Phone images are commonly 4K+ and several megabytes. Gemini needs a clear
    view of shelves, not the original camera resolution; a 1600px JPEG greatly
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
    # 1. Strict image validation
    is_valid_img, img_err = validate_image_bytes(image_bytes, filename, mime_type)
    if not is_valid_img:
        return False, [], img_err

    try:
        image_bytes, mime_type = prepare_image_for_vision(image_bytes)
    except (OSError, ValueError) as error:
        logger.error("Image preparation failed: %s", error)
        return False, [], "Image data is corrupted or unreadable. Please choose another photo."

    # 2. Call Gemini
    try:
        client = get_gemini_client()
        detected_raw = None

        # Check client type (Google GenAI official SDK vs fallback)
        if hasattr(client, "models") and hasattr(client.models, "generate_content"):
            from google.genai import types
            
            part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            detected_raw = generate_json_content(
                [VISION_PROMPT, part], temperature=0.2, client=client
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

        # Parse JSON
        cleaned_text = detected_raw.strip()
        # Remove any stray codeblocks if model added them
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```(?:json)?", "", cleaned_text)
            cleaned_text = re.sub(r"```$", "", cleaned_text)
            cleaned_text = cleaned_text.strip()

        data = json.loads(cleaned_text)
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

        if not validated_items:
            return False, [], "No valid ingredients identified in the photo. Please try a different angle."

        return True, validated_items, ""

    except ValueError as error:
        # A missing key cannot be fixed by retrying; make the setup action clear.
        logger.error("Gemini vision configuration error: %s", error)
        if "GEMINI_API_KEY" in str(error):
            return False, [], "Gemini is not configured. Add GEMINI_API_KEY to .streamlit/secrets.toml, then restart the app."
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
    except json.JSONDecodeError as je:
        logger.error("Gemini vision response was not valid JSON: %s", je)
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
    except Exception as e:
        logger.error("Gemini vision request failed: %s", type(e).__name__)
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
