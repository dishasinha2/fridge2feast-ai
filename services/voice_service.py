"""Voice and Audio Assistant Service for Fridge2Feast AI."""
import re
from typing import Dict, Any

def parse_voice_recipe_query(spoken_text: str) -> Dict[str, Any]:
    """
    Parse natural language / voice dictation into recipe generation parameters.
    Example: 'Make Indian dinner for 4 people mild spice'
    """
    if not spoken_text:
        return {}

    text_lower = spoken_text.lower()
    parsed: Dict[str, Any] = {
        "custom_prompt": spoken_text.strip()
    }

    # 1. Servings detection
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    servings_match = re.search(r"(?:for\s+)?(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:people|servings|guests|persons|portions)", text_lower)
    if not servings_match:
        servings_match = re.search(r"\bfor\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b", text_lower)

    if servings_match:
        val = servings_match.group(1)
        if val.isdigit():
            parsed["servings"] = int(val)
        elif val in word_to_num:
            parsed["servings"] = word_to_num[val]


    # 2. Meal type detection
    for meal in ["breakfast", "lunch", "dinner", "snack", "brunch", "dessert"]:
        if meal in text_lower:
            parsed["meal_type"] = meal.capitalize()
            break

    # 3. Cuisine detection
    for cuisine in ["indian", "italian", "mexican", "chinese", "mediterranean", "thai", "french", "japanese", "korean", "american"]:
        if cuisine in text_lower:
            parsed["cuisine"] = cuisine.capitalize()
            break

    # 4. Dietary detection
    if "vegan" in text_lower:
        parsed["diet"] = "Vegan"
    elif "vegetarian" in text_lower or "veg" in text_lower:
        parsed["diet"] = "Vegetarian"
    elif "gluten-free" in text_lower or "gluten free" in text_lower:
        parsed["diet"] = "Gluten-Free"
    elif "dairy-free" in text_lower or "dairy free" in text_lower:
        parsed["diet"] = "Dairy-Free"

    # 5. Spice level
    if "mild" in text_lower:
        parsed["spice_level"] = "Mild"
    elif "hot" in text_lower or "very spicy" in text_lower:
        parsed["spice_level"] = "Hot"
    elif "spicy" in text_lower:
        parsed["spice_level"] = "Spicy"
    elif "medium" in text_lower:
        parsed["spice_level"] = "Medium"

    # 6. Cooking time
    time_match = re.search(r"(\d+)\s*(?:minutes|mins|min)", text_lower)
    if time_match:
        parsed["cooking_time_minutes"] = int(time_match.group(1))

    return parsed
