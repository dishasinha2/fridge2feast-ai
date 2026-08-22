import re
from typing import Dict, Any, List, Tuple

def validate_email(email: str) -> bool:
    """
    Validates email format using regex.
    """
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))

def validate_password(password: str) -> bool:
    """
    Ensures passwords are suitable for an account login.
    """
    if not password or len(password) < 8:
        return False
    return any(char.isalpha() for char in password) and any(char.isdigit() for char in password)

def validate_preferences(preferences: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Strict validation of user preferences before dispatching to Gemini API:
    - diet, cuisine, meal_type, craving, hunger_level, household_size, servings, budget, max_time, difficulty, spice_level, restrictions, avoid_list
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []

    servings = preferences.get("servings") or preferences.get("household_size")
    if servings is not None:
        try:
            s_val = int(servings)
            if s_val < 1:
                errors.append("Servings must be at least 1.")
            elif s_val > 24:
                errors.append("Servings cannot exceed 24.")
        except (ValueError, TypeError):
            errors.append("Servings must be a valid positive integer.")

    budget = preferences.get("budgetINR")
    if budget is not None:
        try:
            b_val = float(budget)
            if b_val < 0:
                errors.append("Budget cannot be negative.")
            elif b_val > 10000:
                errors.append("Budget cannot exceed ₹10,000 INR.")
        except (ValueError, TypeError):
            errors.append("Budget must be a valid numeric value.")

    avoid_list = preferences.get("avoid_list") or preferences.get("dietaryRestrictions")
    if avoid_list is not None and not isinstance(avoid_list, list):
        errors.append("Restrictions and Avoid items must be provided as a list.")

    return len(errors) == 0, errors
