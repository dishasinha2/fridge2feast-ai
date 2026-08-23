import streamlit as st
import pandas as pd
from utils.calculations import calculate_waste_score
from utils.pandas_utils import get_use_first_ingredients

def render_recipe_dashboard_component():
    """
    Renders the editorial Recipe Decision Deck and Cookbook Detail view.
    Human, calm, trustworthy presentation of culinary recommendations and explainability.
    """
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; margin: 0 0 6px 0;">
                Recipes
            </h1>
            <p style="color: #cbd5e1; font-size: 15px; margin: 0;">
                Tailored to what you have on hand and what you're craving.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    recipes = st.session_state.get("generated_recipes", [])
    meal_context = st.session_state.get("meal_context", {})
    detected_ingredients = st.session_state.get("detected_ingredients", [])

    if not recipes:
        st.markdown(
            """
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 24px; text-align: center; margin: 20px 0;">
                <p style="color: #cbd5e1; font-size: 15px; margin: 0 0 16px 0;">
                    No recipes yet. Tell us what you’d like to make.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("What’s cooking tonight?", type="primary", width="stretch"):
            st.session_state.active_tab = "Kitchen Agent"
            st.rerun()
        return

    # Identify urgent items
    use_first_items = get_use_first_ingredients(detected_ingredients)
    urgent_item_names = [i.get("name", "").lower() for i in use_first_items if i.get("urgency_level") == "HIGH"]

    standard_roles = ["BEST MATCH", "QUICK FEAST", "CREATIVE PICK"]

    # 3-Card Editorial Recipe Deck
    r_cols = st.columns(3)
    
    for idx, recipe in enumerate(recipes[:3]):
        with r_cols[idx]:
            role = standard_roles[idx] if idx < len(standard_roles) else "SUGGESTION"
            role_color = "#10b981" if idx == 0 else ("#38bdf8" if idx == 1 else "#fbbf24")
            utilization = int(recipe.get("ingredient_utilization_percentage", 85))
            time_m = recipe.get("cooking_time_minutes", 20)
            servings = recipe.get("servings", 2)
            diet_label = recipe.get("diet", meal_context.get("diet", "Vegetarian"))

            st.markdown(
                f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 18px; min-height: 250px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 12px;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="background: {role_color}18; color: {role_color}; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px; letter-spacing: 0.5px;">
                                {role}
                            </span>
                            <span style="font-size: 12px; color: #94a3b8;">
                                ⏱️ {time_m}m • {servings}p
                            </span>
                        </div>
                        <h3 style="color: #ffffff; font-size: 18px; font-weight: 700; margin: 4px 0 6px 0; line-height: 1.3;">
                            {recipe.get('title')}
                        </h3>
                        <p style="color: #cbd5e1; font-size: 13px; line-height: 1.4; margin: 0 0 10px 0;">
                            {recipe.get('short_description')}
                        </p>
                    </div>
                    <div style="font-size: 12px; color: #10b981; font-weight: 600; padding-top: 6px; border-top: 1px solid #334155;">
                        ✓ Uses {utilization}% of your fridge items
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("Start cooking", key=f"deck_cook_{idx}", type="primary" if idx == 0 else "secondary", use_container_width=True):
                    st.session_state.cooking_recipe = recipe
                    st.session_state.cooking_step = 0
                    st.session_state.active_tab = "Cooking Mode"
                    st.rerun()
            with b_col2:
                if st.button("View recipe", key=f"deck_view_{idx}", use_container_width=True):
                    st.session_state.selected_recipe = recipe
                    st.rerun()

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Detailed Selected Recipe in Cookbook Layout
    selected = st.session_state.get("selected_recipe") or recipes[0]
    mo_data = selected.get("multi_objective_score", {})
    
    st.markdown("<div style='border-top: 1px solid #334155; padding-top: 24px;'></div>", unsafe_allow_html=True)
    
    # Cookbook Title & Quick Facts
    st.markdown(
        f"""
        <div style="margin-bottom: 18px;">
            <span style="font-size: 12px; color: #10b981; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px;">
                FEATURED RECIPE
            </span>
            <h2 style="color: #ffffff; font-size: 26px; font-weight: 800; margin: 4px 0 8px 0;">
                {selected.get('title')}
            </h2>
            <p style="color: #cbd5e1; font-size: 15px; line-height: 1.5; margin: 0 0 14px 0;">
                {selected.get('short_description')}
            </p>
            <div style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 13px; color: #94a3b8; background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 10px 16px;">
                <span>⏱️ <strong>Time:</strong> {selected.get('cooking_time_minutes', 20)} minutes</span>
                <span>🍽️ <strong>Servings:</strong> {selected.get('servings', 2)} people</span>
                <span>🥗 <strong>Diet:</strong> {selected.get('diet', 'Custom')}</span>
                <span>♻️ <strong>Fridge utilization:</strong> {int(selected.get('ingredient_utilization_percentage', 85))}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # "Why we picked this" (Natural Human Explainability)
    natural_points = [
        f"Uses your available kitchen items ({int(selected.get('ingredient_utilization_percentage', 85))}% on-hand)",
        f"Fits your {meal_context.get('craving', 'current')} craving and meal preference",
        f"Prepares in under {selected.get('cooking_time_minutes', 25)} minutes for {selected.get('servings', 2)} people",
    ]
    if selected.get("ingredients_missing"):
        missing_cost = selected.get("estimated_missing_cost_inr", 0)
        natural_points.append(f"Requires minimal shopping (~₹{missing_cost:.0f})")
    else:
        natural_points.append("Requires zero extra grocery purchases")

    # High-priority ingredients mention
    sel_avail_names = [i.get("name", "").lower() for i in selected.get("ingredients_available", [])]
    rescued_urgent = [u.title() for u in urgent_item_names if any(u in av for av in sel_avail_names)]
    if rescued_urgent:
        natural_points.insert(0, f"Uses high-priority perishable items: {', '.join(rescued_urgent)}")

    st.markdown(
        f"""
        <div style="background: #1e293b; border: 1px solid #334155; border-left: 3px solid #10b981; border-radius: 12px; padding: 16px 20px; margin-bottom: 22px;">
            <div style="font-size: 15px; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                Why we picked this
            </div>
            <ul style="margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 13px; line-height: 1.6;">
                {''.join([f'<li>✓ {p}</li>' for p in natural_points])}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Expandable technical score breakdown (for evaluation/power users)
    with st.expander("See score breakdown", expanded=False):
        u_score = mo_data.get("utilization_score", int(selected.get("ingredient_utilization_percentage", 85)))
        w_score = mo_data.get("urgent_score", 90)
        c_score = mo_data.get("craving_score", 88)
        b_score = mo_data.get("budget_score", 95)
        d_score = mo_data.get("diet_score", 100)
        t_score = mo_data.get("time_score", 90)
        overall_win = mo_data.get("overall_score", 90)

        st.caption(f"Overall Multi-Objective Optimization Score: **{overall_win}/100**")
        sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
        with sc1: st.metric("Fridge Match", f"{u_score}%")
        with sc2: st.metric("Waste Rescue", f"{w_score}%")
        with sc3: st.metric("Craving Match", f"{c_score}%")
        with sc4: st.metric("Budget Fit", f"{b_score}%")
        with sc5: st.metric("Diet Fit", f"{d_score}%")
        with sc6: st.metric("Time Fit", f"{t_score}%")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Cookbook Content Layout: Ingredients & Steps
    ing_col, steps_col = st.columns([1.1, 1.7])

    with ing_col:
        st.markdown("<h3 style='color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 12px;'>Ingredients</h3>", unsafe_allow_html=True)
        
        avail_list = selected.get("ingredients_available", [])
        if avail_list:
            st.markdown("<span style='font-size: 12px; color: #10b981; font-weight: 700; text-transform: uppercase;'>From your kitchen</span>", unsafe_allow_html=True)
            for item in avail_list:
                st.markdown(f"- **{item.get('name')}**: {item.get('quantity', 'as needed')}")
        
        miss_list = selected.get("ingredients_missing", [])
        if miss_list:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("<span style='font-size: 12px; color: #f59e0b; font-weight: 700; text-transform: uppercase;'>From the pantry / store</span>", unsafe_allow_html=True)
            for item in miss_list:
                price = item.get("estimated_price_inr", 0)
                st.markdown(f"- **{item.get('name')}**: ~₹{price:.0f}")

    with steps_col:
        st.markdown("<h3 style='color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 12px;'>Preparation Steps</h3>", unsafe_allow_html=True)
        steps = selected.get("preparation_steps", [])
        for idx, step in enumerate(steps):
            st.markdown(
                f"""
                <div style="margin-bottom: 12px; line-height: 1.5; color: #cbd5e1; font-size: 14px;">
                    <strong style="color: #ffffff;">{idx + 1}.</strong> {step}
                </div>
                """,
                unsafe_allow_html=True
            )

        tips = selected.get("cooking_tips", [])
        if tips:
            st.markdown(
                f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 12px 16px; margin-top: 16px;">
                    <div style="font-size: 12px; color: #fbbf24; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">Chef's Note</div>
                    <p style="color: #cbd5e1; font-size: 13px; margin: 0; line-height: 1.4;">
                        "{tips[0]}"
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Action Bar at bottom
    st.markdown("<div style='border-top: 1px solid #334155; margin-top: 24px; padding-top: 18px;'></div>", unsafe_allow_html=True)
    act_col1, act_col2, act_col3 = st.columns([1.5, 1.2, 1.2])

    with act_col1:
        if st.button("Start interactive cooking", type="primary", use_container_width=True):
            st.session_state.cooking_recipe = selected
            st.session_state.cooking_step = 0
            st.session_state.active_tab = "Cooking Mode"
            st.rerun()

    with act_col2:
        saved_list = st.session_state.get("saved_recipes", [])
        is_saved = any(s.get("title") == selected.get("title") for s in saved_list)
        btn_label = "❤️ Saved in Feastbook" if is_saved else "💾 Save to Feastbook"
        if st.button(btn_label, use_container_width=True):
            if not is_saved:
                st.session_state.saved_recipes.append(selected)
                taste = st.session_state.get("taste_profile", {})
                taste["recipes_cooked_count"] = taste.get("recipes_cooked_count", 0) + 1
                st.session_state.taste_profile = taste
                st.success("Saved to your Feastbook!")
                st.rerun()

    with act_col3:
        if st.button("🛒 View Shopping List", use_container_width=True):
            st.session_state.shopping_recipe = selected
            st.session_state.active_tab = "Shopping List"
            st.rerun()
