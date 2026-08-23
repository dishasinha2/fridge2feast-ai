"""Gemini Vision Service for Fridge and Pantry Ingredient Recognition."""
import json
import re
import logging
from typing import List, Dict, Any, Tuple
from utils.validation import validate_image_bytes, validate_detected_ingredient
from services.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

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

def analyze_fridge_image(image_bytes: bytes, filename: str = "", mime_type: str = "") -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Validate image and send to Gemini Vision for structured ingredient detection.
    Returns (success, list_of_validated_ingredients, user_facing_error_message).
    """
    # 1. Strict image validation
    is_valid_img, img_err = validate_image_bytes(image_bytes, filename, mime_type)
    if not is_valid_img:
        return False, [], img_err

    # 2. Call Gemini
    try:
        client = get_gemini_client()
        detected_raw = None

        # Check client type (Google GenAI official SDK vs fallback)
        if hasattr(client, "models") and hasattr(client.models, "generate_content"):
            from google.genai import types
            
            # Detect mime type if not provided
            if not mime_type:
                if image_bytes.startswith(b"\xFF\xD8\xFF"):
                    mime_type = "image/jpeg"
                elif image_bytes.startswith(b"\x89PNG"):
                    mime_type = "image/png"
                elif image_bytes.startswith(b"RIFF"):
                    mime_type = "image/webp"
                else:
                    mime_type = "image/jpeg"

            part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            try:
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=[VISION_PROMPT, part],
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
            except Exception as model_err:
                logger.warning(f"Primary vision model failed, falling back to gemini-flash-lite-latest: {model_err}")
                response = client.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents=[VISION_PROMPT, part],
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
            detected_raw = response.text
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

    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing error from Gemini vision: {je}")
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
    except Exception as e:
        logger.error(f"Error in analyze_fridge_image: {e}")
        return False, [], "Ingredient scanning is temporarily unavailable. Please try again."
