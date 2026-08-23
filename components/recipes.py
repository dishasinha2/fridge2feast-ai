"""Personalized recipe preference and result workflow."""
import streamlit as st
from services.kitchen_service import get_user_ingredients
from services.recipe_service import generate_recipe, save_recipe
from services.voice_service import parse_voice_recipe_query

TIME_OPTIONS = {"Under 15 minutes": 15, "Under 30 minutes": 30, "Under 45 minutes": 45, "Under 60 minutes": 60, "No limit": 90}
MEALS = ["Breakfast", "Lunch", "Dinner", "Snack"]
DIETS = ["Vegetarian", "Non-Vegetarian", "Vegan", "No Preference"]
CUISINES = ["Indian", "Italian", "Mexican", "Mediterranean", "Asian", "American", "Middle Eastern", "Any Cuisine"]
SPICES = ["Mild", "Medium", "Spicy", "Very Spicy"]

def render_recipes():
    user = st.session_state.authenticated_user
    if not user:
        st.session_state.current_page = "landing"; st.rerun()
    if not get_user_ingredients(user.id):
        st.info("Your kitchen is empty. Scan your fridge or add ingredients first.")
        a, b = st.columns(2)
        with a:
            if st.button("Scan Your Fridge", type="primary", width="stretch"):
                st.session_state.current_page = "scanner"; st.rerun()
        with b:
            if st.button("Add Ingredients", width="stretch"):
                st.session_state.current_page = "kitchen"; st.rerun()
        return
    if st.session_state.get("recipe_flow_stage") == "scan_complete":
        st.title("What's cooking tonight?")
        st.write("Use what you just scanned to create a meal that fits your taste.")
        a, b = st.columns(2)
        with a:
            if st.button("Generate a Recipe", type="primary", width="stretch"):
                st.session_state.recipe_flow_stage = "preferences"; st.rerun()
        with b:
            if st.button("View My Kitchen", width="stretch"):
                st.session_state.current_page = "kitchen"; st.rerun()
        return
    recipe = st.session_state.get("generated_recipe") or st.session_state.get("active_recipe")
    if recipe:
        render_recipe_card(user.id, recipe)
    else:
        render_preferences(user.id)

def render_preferences(user_id: int):
    st.title("What's cooking tonight?")
    st.caption("Choose a few details and we’ll prioritize the ingredients that need using first.")
    saved = st.session_state.get("recipe_preferences", {})
    voice = st.text_input("Optional voice request", value=saved.get("voice_request", ""), placeholder="Type a request to use the existing voice assistant")
    parsed = parse_voice_recipe_query(voice) if voice else {}
    with st.form("recipe_preferences_form"):
        a, b = st.columns(2)
        with a:
            meal = st.selectbox("Meal Type", MEALS, index=MEALS.index(parsed.get("meal_type", saved.get("meal_type", "Dinner"))) if parsed.get("meal_type", saved.get("meal_type", "Dinner")) in MEALS else 2)
            diet = st.selectbox("Diet", DIETS, index=DIETS.index(parsed.get("diet", saved.get("diet", "No Preference"))) if parsed.get("diet", saved.get("diet", "No Preference")) in DIETS else 3)
            servings = st.number_input("Servings", min_value=1, max_value=12, value=int(parsed.get("servings", saved.get("servings", 2))))
        with b:
            cuisine = st.selectbox("Cuisine", CUISINES, index=CUISINES.index(parsed.get("cuisine", saved.get("cuisine", "Any Cuisine"))) if parsed.get("cuisine", saved.get("cuisine", "Any Cuisine")) in CUISINES else 7)
            spice_level = st.selectbox("Spice Level", SPICES, index=SPICES.index(parsed.get("spice_level", saved.get("spice_level", "Medium"))) if parsed.get("spice_level", saved.get("spice_level", "Medium")) in SPICES else 1)
            time_label = st.selectbox("Cooking Time", list(TIME_OPTIONS), index=list(TIME_OPTIONS).index(saved.get("cooking_time", "Under 30 minutes")))
        request = st.text_input("Craving or special request", value=saved.get("special_request", ""))
        submit = st.form_submit_button("Generate a Recipe", type="primary", width="stretch")
    if submit:
        prefs = {"meal_type": meal, "diet": diet, "cuisine": cuisine, "spice_level": spice_level, "servings": int(servings), "cooking_time": time_label, "special_request": request, "voice_request": voice}
        st.session_state.recipe_preferences = prefs
        with st.spinner("Creating a recipe from your kitchen..."):
            recipe, error = generate_recipe(user_id, servings=int(servings), meal_type=meal, cuisine=cuisine, diet=diet, spice_level=spice_level, cooking_time_minutes=TIME_OPTIONS[time_label], custom_prompt=request, latest_scanned_ingredients=st.session_state.get("last_scan_ingredients", []))
        if error or not recipe:
            st.error("Recipe generation is temporarily unavailable. Please try again.")
        else:
            st.session_state.generated_recipe = recipe
            st.session_state.active_recipe = recipe
            st.rerun()

def render_recipe_card(user_id: int, recipe):
    st.title(recipe.title)
    st.caption(f"{recipe.cuisine} · {', '.join(recipe.dietary_tags)} · {recipe.servings} servings · {recipe.cooking_time_minutes} minutes · {recipe.spice_level}")
    st.write(recipe.description)
    st.subheader("Why this recipe?")
    st.write(recipe.tips[0] if recipe.tips else "It prioritizes the ingredients that need using first.")
    a, b = st.columns(2)
    with a:
        st.subheader("From Your Kitchen")
        for item in recipe.available_ingredients: st.write(f"• {item.get('name', item)} — {item.get('quantity', '')} {item.get('unit', '')}")
    with b:
        st.subheader("You May Need")
        for item in recipe.additional_ingredients: st.write(f"• {item.get('name', item)} — {item.get('quantity', '')} {item.get('unit', '')}")
    st.subheader("How to Make It")
    for number, step in enumerate(recipe.instructions, 1): st.write(f"{number}. {step}")
    a, b, c, d = st.columns(4)
    with a:
        if st.button("Save Recipe", width="stretch"):
            st.success("Saved to your recipes.") if save_recipe(user_id, recipe.id) else st.info("This recipe is already saved.")
    with b:
        if st.button("Start Cooking", type="primary", width="stretch"):
            st.session_state.cooking_recipe = recipe; st.session_state.current_step_idx = 0; st.session_state.current_page = "cooking"; st.rerun()
    with c:
        if st.button("Generate Another", width="stretch"):
            st.session_state.generated_recipe = None; st.session_state.active_recipe = None; st.session_state.recipe_flow_stage = "preferences"; st.rerun()
    with d:
        if st.button("Back to Preferences", width="stretch"):
            st.session_state.generated_recipe = None; st.session_state.active_recipe = None; st.session_state.recipe_flow_stage = "preferences"; st.rerun()
