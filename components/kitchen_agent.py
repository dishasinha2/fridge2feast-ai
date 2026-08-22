import streamlit as st
from services.recipe_service import generate_recipes
from services.gemini_client import GeminiServiceException
from utils.calculations import calculate_recipe_multi_objective_score, OPTIMIZATION_PROFILES
from utils.pandas_utils import get_use_first_ingredients

def render_kitchen_agent_component():
    """
    Renders the conversational AI Kitchen Assistant.
    Progressive, natural questions leading to personalized recipes without overwhelming forms.
    """
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; margin: 0 0 6px 0;">
                What are we cooking?
            </h1>
            <p style="color: #cbd5e1; font-size: 15px; margin: 0; line-height: 1.5;">
                I've checked what's in your kitchen. Answer a couple quick questions to get personalized recipes.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    ingredients = st.session_state.get("detected_ingredients", [])
    active_ingredients = [i for i in ingredients if i.get("included", True)]

    if not active_ingredients:
        st.markdown(
            """
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 24px; text-align: center; margin: 20px 0;">
                <h3 style="color: #ffffff; font-size: 18px; margin: 0 0 8px 0;">No ingredients in your kitchen yet</h3>
                <p style="color: #94a3b8; font-size: 14px; margin: 0 0 16px 0;">
                    Scan your fridge or add a few items first so we know what you have to work with.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📸 Scan my fridge", type="primary", use_container_width=True):
            st.session_state.active_tab = "Scanner"
            st.rerun()
        return

    # Use first priority notice (natural and calm)
    use_first = get_use_first_ingredients(active_ingredients)
    urgent_names = [i.get("name") for i in use_first if i.get("urgency_level") == "HIGH"]

    if urgent_names:
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #f59e0b44; border-left: 3px solid #f59e0b; border-radius: 10px; padding: 10px 14px; margin-bottom: 20px; font-size: 13px; color: #cbd5e1;">
                🌱 <strong style="color: #fbbf24;">Freshness tip:</strong> We'll automatically prioritize <strong>{', '.join(urgent_names[:3])}</strong> so they don't go to waste.
            </div>
            """,
            unsafe_allow_html=True
        )

    context = st.session_state.get("meal_context", {})

    # QUESTION 1: WHAT ARE YOU IN THE MOOD FOR?
    st.markdown("<div style='color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 10px;'>1. What are you in the mood for?</div>", unsafe_allow_html=True)
    c_options = [
        ("🌶️ Spicy", "Spicy"),
        ("🥗 Something light", "Light"),
        ("🍔 Comfort food", "Comfort Food"),
        ("🍬 Something sweet", "Sweet"),
        ("✨ Surprise me", "Surprise Me"),
    ]
    current_craving = context.get("craving", "Spicy")
    c_cols = st.columns(5)
    for idx, (label, val) in enumerate(c_options):
        with c_cols[idx]:
            is_sel = (val.lower() in current_craving.lower() or current_craving.lower() in val.lower())
            if st.button(label, key=f"crav_opt_{idx}", use_container_width=True, type="primary" if is_sel else "secondary"):
                st.session_state.meal_context["craving"] = val
                st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # QUESTION 2: WHAT KIND OF MEAL?
    st.markdown("<div style='color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 10px;'>2. What kind of meal?</div>", unsafe_allow_html=True)
    meal_options = [
        ("🌅 Breakfast", "Breakfast"),
        ("🍱 Lunch", "Lunch"),
        ("🌙 Dinner", "Dinner"),
        ("☕ Evening snack", "Evening Snack"),
    ]
    current_meal = context.get("meal_type", "Dinner")
    m_cols = st.columns(4)
    for idx, (label, val) in enumerate(meal_options):
        with m_cols[idx]:
            is_sel = (val.lower() in current_meal.lower() or current_meal.lower() in val.lower())
            if st.button(label, key=f"meal_opt_{idx}", use_container_width=True, type="primary" if is_sel else "secondary"):
                st.session_state.meal_context["meal_type"] = val
                st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # QUESTION 3: HOW HUNGRY ARE YOU?
    st.markdown("<div style='color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 10px;'>3. How hungry are you?</div>", unsafe_allow_html=True)
    hunger_options = ["Light", "Medium", "Very hungry"]
    current_hunger = context.get("hunger_level", "Medium")
    h_cols = st.columns(3)
    for idx, opt in enumerate(hunger_options):
        with h_cols[idx]:
            is_sel = (opt.lower() == current_hunger.lower())
            if st.button(opt, key=f"hunger_opt_{idx}", use_container_width=True, type="primary" if is_sel else "secondary"):
                st.session_state.meal_context["hunger_level"] = opt
                st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # COMPACT PREFERENCE CHIPS
    st.markdown("<div style='color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 10px;'>4. Preferences & household</div>", unsafe_allow_html=True)
    
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        diet_opts = ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"]
        current_diet = context.get("diet", "Vegetarian")
        diet_idx = diet_opts.index(current_diet) if current_diet in diet_opts else 0
        new_diet = st.selectbox("Diet", diet_opts, index=diet_idx)
        st.session_state.meal_context["diet"] = new_diet

    with p_col2:
        household_opts = [1, 2, 4, 6]
        current_size = context.get("household_size", 2)
        h_idx = household_opts.index(current_size) if current_size in household_opts else 1
        new_size = st.selectbox("People", household_opts, index=h_idx, format_func=lambda x: f"{x} {'person' if x==1 else 'people'}")
        st.session_state.meal_context["household_size"] = new_size

    with p_col3:
        spice_opts = ["No Added Spice", "Mild", "Medium", "Spicy"]
        current_spice = context.get("spice_level", "Medium")
        s_idx = spice_opts.index(current_spice) if current_spice in spice_opts else 2
        new_spice = st.selectbox("Spice", spice_opts, index=s_idx)
        st.session_state.meal_context["spice_level"] = new_spice

    with p_col4:
        budget_opts = [0, 100, 150, 300, 500]
        current_budget = context.get("budgetINR", 150)
        b_idx = budget_opts.index(current_budget) if current_budget in budget_opts else 2
        new_budget = st.selectbox("Extra Budget", budget_opts, index=b_idx, format_func=lambda x: "₹0 (Only Fridge)" if x==0 else f"₹{x} max")
        st.session_state.meal_context["budgetINR"] = new_budget

    with st.expander("More options (Allergens & Focus)", expanded=False):
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            avoid_list = st.session_state.meal_context.get("avoid_list", [])
            avoid_input = st.text_input("Ingredients to avoid (comma-separated):", value=", ".join(avoid_list), placeholder="e.g. peanuts, dairy, mushrooms")
            if avoid_input != ", ".join(avoid_list):
                st.session_state.meal_context["avoid_list"] = [x.strip() for x in avoid_input.split(",") if x.strip()]
        with exp_col2:
            obj_choices = ["Balanced", "Minimum Waste", "Lowest Cost", "Fastest", "Best Craving Match", "Nutrition"]
            current_obj = st.session_state.meal_context.get("optimization_objective", "Balanced")
            obj_idx = obj_choices.index(current_obj) if current_obj in obj_choices else 0
            new_obj = st.selectbox("Priority focus", obj_choices, index=obj_idx)
            st.session_state.meal_context["optimization_objective"] = new_obj

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # FINAL ACTION BUTTON: FIND MY MEAL
    if st.button("Find my meal →", type="primary", use_container_width=True):
        with st.spinner("Finding the best 3 recipe options for your kitchen..."):
            try:
                pref_payload = {
                    "diet": st.session_state.meal_context.get("diet", "Vegetarian"),
                    "cuisine": "Home-style / Custom",
                    "cookingTime": st.session_state.meal_context.get("cookingTime", "Under 30 minutes"),
                    "difficulty": st.session_state.meal_context.get("difficulty", "Easy"),
                    "servings": st.session_state.meal_context.get("household_size", 2),
                    "spiceLevel": st.session_state.meal_context.get("spice_level", "Medium"),
                    "budgetINR": st.session_state.meal_context.get("budgetINR", 150),
                    "dietaryRestrictions": st.session_state.meal_context.get("avoid_list", []),
                    "craving": st.session_state.meal_context.get("craving", "Spicy"),
                    "meal_type": st.session_context.get("meal_type", "Dinner") if "session_context" in locals() else st.session_state.meal_context.get("meal_type", "Dinner"),
                    "hunger_level": st.session_state.meal_context.get("hunger_level", "Medium"),
                }
                
                recipes = generate_recipes(active_ingredients, pref_payload)
                
                # Multi-objective application scoring
                active_obj = st.session_state.meal_context.get("optimization_objective", "Balanced")
                taste_prof = st.session_state.get("taste_profile", {})
                
                for r in recipes:
                    mo_score = calculate_recipe_multi_objective_score(
                        recipe=r,
                        meal_context=st.session_state.meal_context,
                        urgent_ingredients=urgent_names,
                        objective_profile=active_obj,
                        taste_profile=taste_prof
                    )
                    r["multi_objective_score"] = mo_score

                recipes = sorted(recipes, key=lambda x: x.get("multi_objective_score", {}).get("overall_score", 0), reverse=True)

                st.session_state.generated_recipes = recipes
                st.session_state.selected_recipe = recipes[0]
                st.session_state.active_tab = "Recipes"
                st.rerun()

            except GeminiServiceException as ge:
                st.error(f"⚠️ {ge.user_message}")
            except Exception as e:
                st.error(f"⚠️ We couldn't generate recipes right now. Please check your inventory and try again.")
