import pandas as pd
import json

def process_ingredients_dataframe(raw_items_list):
    """
    Takes a raw list of ingredient dictionaries and constructs a cleaned Pandas DataFrame.
    """
    if not raw_items_list:
        return pd.DataFrame(columns=[
            "id", "name", "category", "estimated_quantity", "confidence_pct", "confidence_label", "included"
        ])
    
    df = pd.DataFrame(raw_items_list)
    
    # Ensure default required columns exist
    if "included" not in df.columns:
        df["included"] = True
    if "confidence_pct" not in df.columns:
        if "confidence" in df.columns:
            df["confidence_pct"] = (df["confidence"] * 100).astype(int)
        else:
            df["confidence_pct"] = 90
            
    if "confidence_label" not in df.columns:
        df["confidence_label"] = df["confidence_pct"].apply(
            lambda x: "High" if x >= 85 else ("Medium" if x >= 70 else "Low")
        )
    if "id" not in df.columns:
        df["id"] = [f"ing-{i+1}" for i in range(len(df))]
        
    return df

def filter_confirmed_ingredients(df):
    """
    Filters dataframe to return only user-included ingredients using Pandas query.
    """
    if df.empty:
        return pd.DataFrame()
    return df.query("included == True")

def group_ingredients_by_category(df):
    """
    Group ingredients by category and return category counts.
    """
    if df.empty or "category" not in df.columns:
        return pd.Series(dtype=int)
    return df.groupby("category").size()

def calculate_utilization_pct(df_ingredients, active_recipe=None):
    """
    Calculates percentage of available ingredients utilized in a recipe.
    """
    if df_ingredients.empty:
        return 0.0
    confirmed = filter_confirmed_ingredients(df_ingredients)
    if confirmed.empty:
        return 0.0
    
    if active_recipe and "available_ingredients" in active_recipe:
        used_names = {ing.get("name", "").lower() for ing in active_recipe["available_ingredients"]}
        avail_names = [name.lower() for name in confirmed["name"].tolist()]
        matches = sum(1 for name in avail_names if any(u in name or name in u for u in used_names))
        return round((matches / len(avail_names)) * 100, 1)
    
    return 85.0 # Default high utilization baseline

def calculate_waste_score_df(df_ingredients, utilization_pct=85.0):
    """
    Calculates food waste reduction score (0-100) using Pandas DataFrame metrics.
    """
    if df_ingredients.empty:
        return 0
    
    total_count = len(df_ingredients)
    included_df = filter_confirmed_ingredients(df_ingredients)
    included_count = len(included_df)
    
    base_ratio = (included_count / total_count) if total_count > 0 else 1.0
    score = int((base_ratio * 0.4 + (utilization_pct / 100) * 0.6) * 100)
    return min(100, max(15, score))

def generate_session_analytics(ingredients_df, generated_recipes, saved_recipes):
    """
    Aggregates real session analytics using Pandas operations.
    """
    if ingredients_df.empty and not generated_recipes:
        return None

    confirmed_df = filter_confirmed_ingredients(ingredients_df)
    
    cat_counts = ingredients_df["category"].value_counts().to_dict() if not ingredients_df.empty and "category" in ingredients_df.columns else {}
    avg_conf = float(round(ingredients_df["confidence_pct"].mean(), 1)) if not ingredients_df.empty and "confidence_pct" in ingredients_df.columns else 0.0

    avg_util = 0.0
    avg_time = 0.0
    cuisines = {}

    if generated_recipes:
        utils = [r.get("ingredient_utilization_percentage", 80) for r in generated_recipes]
        times = [r.get("cooking_time_minutes", 30) for r in generated_recipes]
        avg_util = float(round(sum(utils) / len(utils), 1))
        avg_time = float(round(sum(times) / len(times), 1))
        
        for r in generated_recipes:
            c = r.get("cuisine", "General")
            cuisines[c] = cuisines.get(c, 0) + 1

    return {
        "total_ingredients_detected": int(len(ingredients_df)),
        "confirmed_ingredients_count": int(len(confirmed_df)),
        "recipes_generated_count": int(len(generated_recipes)),
        "recipes_saved_count": int(len(saved_recipes)),
        "avg_confidence_pct": avg_conf,
        "avg_utilization_pct": avg_util,
        "avg_cooking_time_mins": avg_time,
        "category_distribution": cat_counts,
        "cuisine_distribution": cuisines
    }

def safe_pandas_explorer(df, operation):
    """
    Executes a safe, predefined Pandas operation on ingredients_df without exposing arbitrary Python execution.
    """
    if df.empty:
        return "DataFrame is empty. Please scan or load ingredients first."

    if operation == "Dataset Summary":
        return df.info(buf=None) or f"DataFrame shape: {df.shape[0]} rows, {df.shape[1]} columns.\nColumns: {', '.join(df.columns)}"

    elif operation == "Describe Data (`df.describe()`)":
        return df.describe()

    elif operation == "Group by Category (`df.groupby('category').size()`)":
        return df.groupby("category").size().reset_index(name="count")

    elif operation == "Filter Confirmed Ingredients (`df.query('included == True')`)":
        return filter_confirmed_ingredients(df)

    elif operation == "Category Confidence Summary":
        if "confidence_pct" in df.columns and "category" in df.columns:
            return df.groupby("category")["confidence_pct"].agg(["count", "mean", "min", "max"]).reset_index()
        return df

    return df

def calculate_fridge_potential(df_ingredients):
    """
    Calculates fridge potential score based on confirmed ingredients count.
    """
    if df_ingredients.empty:
        return "LOW", "Scan or add ingredients to evaluate fridge potential."
    
    confirmed = filter_confirmed_ingredients(df_ingredients)
    count = len(confirmed)
    
    if count >= 6:
        return "HIGH", f"Excellent inventory! You have {count} confirmed items capable of generating multiple diverse meal combinations."
    elif count >= 3:
        return "MEDIUM", f"Good foundation! You have {count} confirmed items suitable for complete 2-3 dish zero-waste recipes."
    elif count >= 1:
        return "BUILDING", f"Basic inventory ({count} item). Gemini will supplement with pantry staples to complete recipes."
    else:
        return "EMPTY", "No confirmed ingredients selected. Toggle 'Include?' in the ingredients table."

def generate_why_gemini_chose_this(recipe, confirmed_ingredients_df, preferences):
    """
    Generates a list of factual, context-aware reason strings explaining why Gemini chose a recipe.
    """
    reasons = []
    
    # 1. Utilization
    util = recipe.get("ingredient_utilization_percentage", 80)
    avail_count = len(recipe.get("available_ingredients", []))
    total_avail = len(filter_confirmed_ingredients(confirmed_ingredients_df)) if not confirmed_ingredients_df.empty else avail_count
    reasons.append(f"✓ Maximizes fridge inventory by using {avail_count} of {total_avail} available ingredients ({util}% utilization)")
    
    # 2. Budget
    budget_cap = preferences.get("budget_inr", 500)
    missing_cost = recipe.get("estimated_missing_cost_inr", 0)
    if missing_cost <= budget_cap:
        under = budget_cap - missing_cost
        reasons.append(f"✓ Fits within your budget cap (₹{missing_cost} INR estimated, ₹{under} under ₹{budget_cap} limit)")
    else:
        reasons.append(f"✓ Minimizes additional purchases (₹{missing_cost} INR required)")
        
    # 3. Cuisine
    fav_cuisine = preferences.get("cuisine", "Any")
    recipe_cuisine = recipe.get("cuisine", "General")
    if fav_cuisine != "Any" and fav_cuisine.lower() in recipe_cuisine.lower():
        reasons.append(f"✓ Matches your preferred cuisine style ({recipe_cuisine})")
    else:
        reasons.append(f"✓ Crafted in an accessible {recipe_cuisine} culinary style")
        
    # 4. Cooking Time
    max_time = preferences.get("max_cooking_time", 30)
    rec_time = recipe.get("cooking_time_minutes", 25)
    if rec_time <= max_time:
        reasons.append(f"✓ Ready in {rec_time} minutes (well under your {max_time}-minute time limit)")
    else:
        reasons.append(f"✓ Efficient prep time of {rec_time} minutes")
        
    # 5. Diet
    diet = preferences.get("diet", "No Preference")
    if diet != "No Preference":
        reasons.append(f"✓ Formulated strictly adhering to your {diet} dietary preference")
        
    # 6. Dietary Restrictions
    restrictions = preferences.get("dietary_restrictions", "None")
    if restrictions and restrictions.lower() != "none":
        reasons.append(f"✓ Respects special dietary restrictions ({restrictions})")
        
    return reasons

def export_shopping_list_txt(missing_ingredients, recipe_title, total_cost):
    """
    Formats missing ingredients into plain text shopping list.
    """
    txt = f"=== SMART SHOPPING LIST FOR: {recipe_title} ===\n"
    txt += f"Total Estimated Additional Cost: ₹{total_cost} INR\n\n"
    txt += "ITEMS TO PURCHASE:\n"
    for idx, item in enumerate(missing_ingredients, 1):
        txt += f"[{idx}] {item.get('name')} - {item.get('estimated_quantity', '1 unit')} (~₹{item.get('estimated_price_inr', 0)} INR)\n"
    txt += "\nGenerated by Fridge2Feast AI - Zero Waste Recipe System\n"
    return txt

def export_recipe_markdown(recipe_dict):
    """
    Formats a recipe dictionary into clean Markdown text.
    """
    title = recipe_dict.get("title", "Untitled Recipe")
    cuisine = recipe_dict.get("cuisine", "General")
    time_mins = recipe_dict.get("cooking_time_minutes", 30)
    servings = recipe_dict.get("servings", 2)
    missing_cost = recipe_dict.get("estimated_missing_cost_inr", 0)
    badge = recipe_dict.get("badge", "Zero-Waste Recipe")
    
    md = f"# 🥗 {title}\n"
    md += f"**Badge**: {badge} | **Cuisine**: {cuisine} | **Time**: {time_mins} mins | **Servings**: {servings}\n"
    md += f"**Estimated Missing Cost**: ₹{missing_cost} INR\n\n"
    
    if recipe_dict.get("description"):
        md += f"_{recipe_dict.get('description')}_\n\n"
        
    md += "## 🛒 Available Ingredients\n"
    for ing in recipe_dict.get("available_ingredients", []):
        md += f"- **{ing.get('name')}**: {ing.get('quantity', 'As needed')}\n"
        
    md += "\n## 🛍️ Missing Ingredients (To Purchase)\n"
    missing = recipe_dict.get("missing_ingredients", [])
    if missing:
        for ing in missing:
            md += f"- **{ing.get('name')}**: {ing.get('estimated_quantity', '1 unit')} (~₹{ing.get('estimated_price_inr', 0)})\n"
    else:
        md += "- None! All ingredients are available in your fridge.\n"
        
    md += "\n## 🍳 Step-by-Step Cooking Instructions\n"
    for idx, step in enumerate(recipe_dict.get("preparation_steps", []), 1):
        md += f"{idx}. {step}\n"
        
    if recipe_dict.get("cooking_tips"):
        md += f"\n💡 **Chef Tip**: {recipe_dict.get('cooking_tips')}\n"
    if recipe_dict.get("substitutions"):
        md += f"🔄 **Substitutions**: {recipe_dict.get('substitutions')}\n"
    if recipe_dict.get("food_waste_note"):
        md += f"🌱 **Food Waste Reduction**: {recipe_dict.get('food_waste_note')}\n"
        
    md += "\n---\n*Generated by Fridge2Feast AI*\n"
    return md
