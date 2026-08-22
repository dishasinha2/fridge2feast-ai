import streamlit as st
from services.recipe_service import generate_recipes

def render_recipe_studio_component():
    """
    Renders the AI Recipe Studio preference form & generator.
    """
    st.markdown("<h2 style='color: #ffffff; font-weight: 900;'>🍳 AI Recipe Studio</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>"
        "Customize your cooking preferences to receive three tailored zero-waste recipes: Best Match, Quick Feast, and Creative Pick."
        "</p>",
        unsafe_allow_html=True
    )

    ingredients = st.session_state.get("detected_ingredients", [])
    active_ingredients = [i for i in ingredients if i.get("included", True)]

    if not active_ingredients:
        st.warning("You don't have any confirmed ingredients in your inventory. Please scan your fridge or add items first.")
        if st.button("📸 Go to Camera Scanner"):
            st.session_state.active_tab = "Scanner"
            st.rerun()
        return

    st.markdown(
        f"""
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 12px 18px; margin-bottom: 20px;">
            <span style="color: #10b981; font-weight: 800;">Confirmed Active Ingredients ({len(active_ingredients)}):</span><br>
            <span style="color: #cbd5e1; font-size: 13px;">
                {', '.join([i['name'] for i in active_ingredients[:12]])}{'...' if len(active_ingredients) > 12 else ''}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Preferences Form
    with st.form("recipe_preferences_form"):
        st.markdown("#### ⚙️ Culinary Preferences")

        c1, c2, c3 = st.columns(3)
        with c1:
            diet = st.selectbox("Dietary Preference", [
                "Non-Vegetarian", "Vegetarian", "Vegan", "Eggetarian", "No Preference"
            ], index=1)
            cuisine = st.selectbox("Cuisine Style", [
                "Indian", "Italian", "Mexican", "Asian", "Mediterranean", "American", "Fusion", "Any"
            ], index=0)

        with c2:
            cooking_time = st.selectbox("Maximum Cooking Time", [
                "Under 15 minutes", "Under 30 minutes", "Under 60 minutes", "No limit"
            ], index=1)
            difficulty = st.selectbox("Preferred Difficulty", [
                "Easy", "Medium", "Advanced"
            ], index=0)

        with c3:
            servings = st.slider("Servings Count", min_value=1, max_value=8, value=2)
            spice_level = st.selectbox("Spice Level", ["Mild", "Medium", "Spicy"], index=1)

        b1, b2 = st.columns(2)
        with b1:
            budget_inr = st.number_input("Max Missing Cost Budget (INR ₹)", min_value=0, max_value=2000, value=300, step=50)
        with b2:
            restrictions = st.multiselect("Dietary Restrictions / Allergies", [
                "Gluten-Free", "Nut-Free", "Dairy-Free", "Jain", "Low Sodium", "Keto"
            ])

        st.markdown("<br>", unsafe_allow_html=True)
        generate_submit = st.form_submit_button("Generate 3 zero-waste recipes", type="primary", width="stretch")

        if generate_submit:
            prefs = {
                "diet": diet,
                "cuisine": cuisine,
                "cookingTime": cooking_time,
                "difficulty": difficulty,
                "servings": servings,
                "spiceLevel": spice_level,
                "budgetINR": budget_inr,
                "dietaryRestrictions": restrictions,
            }
            st.session_state.preferences = prefs

            with st.spinner("Creating your recipe ideas…"):
                try:
                    recipes = generate_recipes(active_ingredients, prefs)
                    if recipes:
                        # Deterministic ranking & scoring via Python calculation
                        from utils.calculations import calculate_recipe_multi_objective_score
                        from utils.pandas_utils import get_use_first_ingredients
                        
                        use_first = get_use_first_ingredients(active_ingredients)
                        urgent_names = [i.get("name") for i in use_first if i.get("urgency_level") == "HIGH"]
                        
                        for r in recipes:
                            mo_score = calculate_recipe_multi_objective_score(
                                recipe=r,
                                meal_context=prefs,
                                urgent_ingredients=urgent_names,
                                objective_profile="Balanced"
                            )
                            r["multi_objective_score"] = mo_score

                        recipes = sorted(recipes, key=lambda x: x.get("multi_objective_score", {}).get("overall_score", 0), reverse=True)
                        st.session_state.generated_recipes = recipes
                        st.session_state.selected_recipe = recipes[0]
                        st.success("Successfully generated 3 tailored recipes!")
                        st.session_state.active_tab = "Recipe Dashboard"
                        st.rerun()
                    else:
                        st.error("Could not generate recipes. Please try again.")
                except Exception as err:
                    st.error(f"Recipe Generation Failed: {str(err)}")
