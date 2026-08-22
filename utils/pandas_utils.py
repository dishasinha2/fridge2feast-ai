import pandas as pd
from typing import List, Dict, Any, Optional
import datetime

# Shelf-life assumptions in days based on typical kitchen/refrigerator pantry storage
SHELF_LIFE_DAYS = {
    # Perishable - High Risk
    "spinach": 3,
    "lettuce": 4,
    "coriander": 4,
    "cilantro": 4,
    "mint": 4,
    "mushrooms": 4,
    "berries": 4,
    "strawberries": 4,
    "milk": 5,
    "paneer": 5,
    "tofu": 5,
    "fish": 2,
    "chicken": 3,
    "meat": 3,
    "yogurt": 7,
    "curd": 5,
    "cream": 6,
    "bread": 5,
    
    # Moderate Perishable - Medium Risk
    "tomato": 7,
    "tomatoes": 7,
    "cucumber": 7,
    "bell pepper": 7,
    "capsicum": 7,
    "broccoli": 6,
    "cauliflower": 7,
    "zucchini": 6,
    "green beans": 7,
    "cheese": 14,
    "butter": 30,
    "eggs": 21,
    "apple": 14,
    "banana": 5,
    "lemon": 14,
    "lime": 14,
    "ginger": 21,
    "garlic": 30,
    
    # Stable Pantry / Roots - Low Risk
    "onion": 30,
    "onions": 30,
    "potato": 30,
    "potatoes": 30,
    "carrot": 21,
    "carrots": 21,
    "rice": 180,
    "pasta": 180,
    "flour": 180,
    "lentils": 180,
    "dal": 180,
    "oil": 180,
    "spices": 365,
    "sauce": 60,
    "soy sauce": 180,
}

def estimate_ingredient_freshness(name: str, category: str = "", estimated_quantity: str = "") -> Dict[str, Any]:
    """
    Deterministically computes estimated freshness status, urgency, use-by window, and waste risk score.
    Clearly indicates that this is an AI-estimated approximate shelf-life window based on category & item type.
    """
    clean_name = name.lower().strip()
    
    # Find matching base shelf life
    base_shelf_life = 7  # default fallback
    for key, days in SHELF_LIFE_DAYS.items():
        if key in clean_name:
            base_shelf_life = days
            break
    else:
        # Category based heuristic
        cat_lower = category.lower()
        if "vegetable" in cat_lower or "fruit" in cat_lower:
            base_shelf_life = 6
        elif "dairy" in cat_lower or "egg" in cat_lower or "protein" in cat_lower:
            base_shelf_life = 5
        elif "grain" in cat_lower or "pantry" in cat_lower or "spice" in cat_lower:
            base_shelf_life = 90

    # Calculate waste risk score (0 to 100)
    # Shorter shelf life -> Higher waste risk
    if base_shelf_life <= 3:
        risk_score = 90
        urgency = "HIGH"
        freshness_status = "Use Soon"
        use_window = "1–2 days"
        priority_label = "🚨 CRITICAL"
    elif base_shelf_life <= 5:
        risk_score = 75
        urgency = "HIGH"
        freshness_status = "High Priority"
        use_window = "2–3 days"
        priority_label = "⚠️ HIGH"
    elif base_shelf_life <= 10:
        risk_score = 45
        urgency = "MEDIUM"
        freshness_status = "Moderate"
        use_window = "4–7 days"
        priority_label = "🟡 MEDIUM"
    else:
        risk_score = 15
        urgency = "LOW"
        freshness_status = "Stable / Shelf-Safe"
        use_window = "2+ weeks"
        priority_label = "🟢 STABLE"

    return {
        "shelf_life_days": base_shelf_life,
        "waste_risk_score": risk_score,
        "urgency_level": urgency,
        "freshness_status": freshness_status,
        "estimated_use_window": use_window,
        "priority_label": priority_label,
        "reasoning": f"{name.capitalize()} is naturally perishable (est. window: {use_window}). Prioritize to prevent kitchen waste."
    }

def ingredients_to_df(ingredients: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Converts a list of ingredient dictionaries into an enriched Pandas DataFrame.
    Includes freshness status, waste risk, and urgency columns.
    """
    if not ingredients:
        return pd.DataFrame(columns=[
            "id", "Ingredient", "Category", "Quantity", "Confidence", "Confidence Label",
            "Urgency", "Waste Risk", "Est. Use-By", "Include"
        ])

    data = []
    for item in ingredients:
        name = item.get("name", item.get("Ingredient", ""))
        cat = item.get("category", item.get("Category", "Pantry & Spices"))
        qty = item.get("estimated_quantity", item.get("Quantity", "1 item"))
        
        # Calculate freshness metadata if not already present
        freshness_meta = estimate_ingredient_freshness(name, cat, qty)
        
        urgency = item.get("urgency_level", freshness_meta["urgency_level"])
        waste_risk = item.get("waste_risk_score", freshness_meta["waste_risk_score"])
        use_window = item.get("estimated_use_window", freshness_meta["estimated_use_window"])
        
        data.append({
            "id": item.get("id", f"ing-{len(data)+1}"),
            "Ingredient": name,
            "Category": cat,
            "Quantity": qty,
            "Confidence": float(item.get("confidence", 0.85)),
            "Confidence Label": item.get("confidence_label", "High"),
            "Urgency": urgency,
            "Waste Risk": int(waste_risk),
            "Est. Use-By": use_window,
            "Include": bool(item.get("included", item.get("Include", True))),
        })

    df = pd.DataFrame(data)
    return df

def df_to_ingredients(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Converts an enriched Pandas DataFrame back into a list of ingredient dictionaries.
    """
    if df is None or df.empty:
        return []

    ingredients = []
    for idx, row in df.iterrows():
        name = str(row.get("Ingredient", "Ingredient"))
        cat = str(row.get("Category", "Pantry & Spices"))
        qty = str(row.get("Quantity", "1 item"))
        freshness_meta = estimate_ingredient_freshness(name, cat, qty)
        
        ingredients.append({
            "id": str(row.get("id", f"ing-{idx+1}")),
            "name": name,
            "category": cat,
            "estimated_quantity": qty,
            "confidence": float(row.get("Confidence", 0.85)),
            "confidence_label": str(row.get("Confidence Label", "High")),
            "urgency_level": str(row.get("Urgency", freshness_meta["urgency_level"])),
            "waste_risk_score": int(row.get("Waste Risk", freshness_meta["waste_risk_score"])),
            "estimated_use_window": str(row.get("Est. Use-By", freshness_meta["estimated_use_window"])),
            "included": bool(row.get("Include", True)),
        })
    return ingredients

def get_category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns category breakdown count for chart visualization.
    """
    if df is None or df.empty or "Category" not in df.columns:
        return pd.DataFrame(columns=["Category", "Count"])

    included_df = df[df["Include"] == True] if "Include" in df.columns else df
    counts = included_df["Category"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    return counts

def calculate_fridge_potential(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates Fridge Potential tier (HIGH, MEDIUM, BUILDING) based on ingredient variety and counts.
    """
    if df is None or df.empty:
        return {
            "tier": "BUILDING",
            "score": 25,
            "description": "Add more ingredients or scan your fridge to build potential.",
            "color": "#f59e0b"
        }

    included_df = df[df["Include"] == True] if "Include" in df.columns else df
    total_count = len(included_df)
    categories_count = included_df["Category"].nunique() if "Category" in included_df.columns else 1

    if total_count >= 8 and categories_count >= 4:
        return {
            "tier": "HIGH",
            "score": 94,
            "description": "Superb ingredient variety! Ready for zero-waste gourmet meals.",
            "color": "#10b981"
        }
    elif total_count >= 4:
        return {
            "tier": "MEDIUM",
            "score": 72,
            "description": "Good foundation. Multiple delicious recipes possible.",
            "color": "#3b82f6"
        }
    else:
        return {
            "tier": "BUILDING",
            "score": 35,
            "description": "Basic inventory. Perfect for quick 15-minute feasts.",
            "color": "#f59e0b"
        }

def get_use_first_ingredients(ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks ingredients by estimated waste urgency score (highest risk first).
    """
    if not ingredients:
        return []
    
    # Filter only included items
    active_items = [i for i in ingredients if i.get("included", True)]
    
    enriched = []
    for item in active_items:
        name = item.get("name", "")
        cat = item.get("category", "")
        qty = item.get("estimated_quantity", "")
        meta = estimate_ingredient_freshness(name, cat, qty)
        
        enriched.append({
            **item,
            "urgency_level": item.get("urgency_level") or meta["urgency_level"],
            "waste_risk_score": item.get("waste_risk_score") or meta["waste_risk_score"],
            "estimated_use_window": item.get("estimated_use_window") or meta["estimated_use_window"],
            "priority_label": meta["priority_label"],
            "reasoning": meta["reasoning"],
        })
        
    # Sort descending by waste risk score
    return sorted(enriched, key=lambda x: x.get("waste_risk_score", 0), reverse=True)
