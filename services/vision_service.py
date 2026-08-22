import io
import json
import time
from typing import List, Optional
from PIL import Image
from pydantic import BaseModel, Field, ValidationError
from google.genai import types
from services.gemini_client import invoke_gemini_with_retry, GeminiServiceException, _record_telemetry_event
from prompts.ingredient_detection import (
    INGREDIENT_VISION_SYSTEM_INSTRUCTION,
    INGREDIENT_VISION_PROMPT,
)

# Pydantic Schemas for Structured JSON response from Gemini
class IngredientItemSchema(BaseModel):
    name: str = Field(description="Name of the food item")
    category: str = Field(description="Category: Vegetables, Fruits, Dairy & Eggs, Proteins & Meat, Grains & Pasta, Condiments & Sauces, Pantry & Spices, Beverages")
    estimated_quantity: str = Field(description="Estimated quantity or count")
    confidence: float = Field(description="Confidence value between 0.0 and 1.0")
    confidence_label: str = Field(description="High, Medium, or Low")
    freshness_hint: str = Field(description="Approximate freshness guidance, never an exact expiry date")

class VisionAnalysisResponseSchema(BaseModel):
    is_food_image: bool = Field(default=False)
    ingredients: List[IngredientItemSchema] = Field(default_factory=list)
    uncertain_items: List[str] = Field(default_factory=list)
    non_food_items_detected: List[str] = Field(default_factory=list)
    summary: str = Field(default="No usable food or fridge contents were detected.")

def analyze_fridge_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Calls Gemini Vision model with the in-memory fridge image and structured schema.
    Processes in memory only — never writes raw image bytes to disk.
    If analysis fails or structured validation fails, handles cleanly without dumping raw JSON.
    """
    if not image_bytes:
        raise GeminiServiceException("No image data provided. Please upload or take a photo.", is_transient=False)
    if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise GeminiServiceException("Please upload a supported JPG, PNG, or WEBP image.", is_transient=False)

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.verify()
        with Image.open(io.BytesIO(image_bytes)) as image:
            width, height = image.size
    except Exception:
        raise GeminiServiceException("This image could not be decoded. Please try another photo.", is_transient=False)

    if width < 64 or height < 64 or width > 10000 or height > 10000:
        raise GeminiServiceException("Please use an image with reasonable dimensions.", is_transient=False)

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )

    # Invoke centralized Gemini client with automatic bounded retry & error translation
    response_text = invoke_gemini_with_retry(
        contents=[image_part, INGREDIENT_VISION_PROMPT],
        system_instruction=INGREDIENT_VISION_SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=VisionAnalysisResponseSchema,
        temperature=0.2,
        max_retries=3,
    )

    try:
        data = json.loads(response_text)
        # Validate against Pydantic schema
        validated_obj = VisionAnalysisResponseSchema(**data)
        data = validated_obj.model_dump()
    except (json.JSONDecodeError, ValidationError) as ve:
        _record_telemetry_event(success=False, latency_ms=0, validation_error=True)
        raise GeminiServiceException(
            "We couldn't confidently interpret the scan. Please try another photo.",
            error_code=422,
            is_transient=False
            ,error_category="SCHEMA_VALIDATION_ERROR"
        )

    # Format ingredients with unique IDs and 'included' flag for pandas DataFrame use
    ingredients_list = []
    raw_ingredients = data.get("ingredients", [])

    if not data.get("is_food_image", False):
        return {
            "ingredients": [],
            "uncertain_items": [],
            "non_food_items_detected": data.get("non_food_items_detected", []),
            "summary": "No usable food or fridge contents were detected.",
            "is_food_image": False,
        }
    
    for idx, item in enumerate(raw_ingredients):
        name = item.get("name", "").strip()
        if not name:
            continue
        ingredients_list.append({
            "id": f"detected-{int(time.time())}-{idx}",
            "name": name,
            "category": item.get("category", "Pantry & Spices"),
            "estimated_quantity": item.get("estimated_quantity", "1 item"),
            "confidence": float(item.get("confidence", 0.85)),
            "confidence_label": item.get("confidence_label", "High"),
            "freshness_hint": item.get("freshness_hint", "AI-estimated freshness guidance — check package labels and food condition."),
            "included": True,
        })

    return {
        "ingredients": ingredients_list,
        "uncertain_items": data.get("uncertain_items", []),
        "non_food_items_detected": data.get("non_food_items_detected", []),
        "summary": data.get("summary", f"Detected {len(ingredients_list)} food items in your fridge photo."),
        "is_food_image": True,
    }
