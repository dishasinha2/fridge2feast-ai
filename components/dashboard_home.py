import streamlit as st
import pandas as pd
from datetime import datetime
from utils.pandas_utils import ingredients_to_df, get_use_first_ingredients, calculate_fridge_potential

def render_dashboard_component():
    """
    Renders the human-centered, editorial Fridge2Feast AI Dashboard.
    Centered on a warm lifestyle greeting, clear next actions, and calm kitchen visibility.
    """
    user = st.session_state.get("user", {})
    user_name = user.get("name", "Chef")
    
    # Natural time-based greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        time_greeting = "Good morning"
        cook_prompt = "What should I cook today?"
    elif current_hour < 17:
        time_greeting = "Good afternoon"
        cook_prompt = "What should I cook for lunch?"
    else:
        time_greeting = "Good evening"
        cook_prompt = "What should I cook tonight?"

    ingredients = st.session_state.get("detected_ingredients", [])
    active_ingredients = [i for i in ingredients if i.get("included", True)]
    saved_recipes = st.session_state.get("saved_recipes", [])
    generated_recipes = st.session_state.get("generated_recipes", [])
    reminders = st.session_state.get("active_reminders", [])
    taste_profile = st.session_state.get("taste_profile", {})

    use_first = get_use_first_ingredients(active_ingredients) if active_ingredients else []
    urgent_items = [i for i in use_first if i.get("urgency_level") == "HIGH"]
    urgent_count = len(urgent_items)
    total_count = len(active_ingredients)

    # 1. Warm editorial header. Native Streamlit elements avoid HTML fragments leaking into the UI.
    st.title(f"{time_greeting}, {user_name} 👋")
    subtitle = f"You have {total_count} ingredients waiting in your kitchen."
    if urgent_count:
        subtitle += f" {urgent_count} ingredients are best used soon."
    st.caption(subtitle)

    # 2. Primary & Secondary Next Action CTAs
    cta_col1, cta_col2, cta_col3 = st.columns([1.8, 1.2, 1.0])
    with cta_col1:
        if st.button(f"✨ {cook_prompt}", type="primary", use_container_width=True):
            st.session_state.active_tab = "Kitchen Agent"
            st.rerun()
    with cta_col2:
        if st.button("📸 Scan my fridge", use_container_width=True):
            st.session_state.active_tab = "Scanner"
            st.rerun()
    with cta_col3:
        if st.button("🚨 Rescue items", use_container_width=True):
            st.session_state.active_tab = "Rescue"
            st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 3. Compact "YOUR KITCHEN TODAY" Strip (Not oversized cards)
    st.markdown(
        f"""
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 14px 20px; margin-bottom: 28px;">
            <div style="font-size: 11px; color: #94a3b8; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 8px;">
                YOUR KITCHEN TODAY
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; color: #f8fafc;">
                <div>
                    <span style="font-size: 20px; font-weight: 800; color: #ffffff;">{total_count}</span>
                    <span style="font-size: 13px; color: #94a3b8; margin-left: 4px;">ingredients</span>
                </div>
                <div style="border-left: 1px solid #334155; height: 24px; display: none;"></div>
                <div>
                    <span style="font-size: 20px; font-weight: 800; color: {'#f59e0b' if urgent_count > 0 else '#10b981'};">{urgent_count}</span>
                    <span style="font-size: 13px; color: #94a3b8; margin-left: 4px;">use soon</span>
                </div>
                <div>
                    <span style="font-size: 20px; font-weight: 800; color: #38bdf8;">{len(generated_recipes)}</span>
                    <span style="font-size: 13px; color: #94a3b8; margin-left: 4px;">recipes generated</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4. Two-Column Main Layout
    left_col, right_col = st.columns([1.6, 1.1])

    with left_col:
        # "Use these soon" Section
        st.markdown("<h2 style='color: #ffffff; font-weight: 800; font-size: 20px; margin: 0 0 14px 0;'>Use these soon</h2>", unsafe_allow_html=True)
        
        display_items = urgent_items if urgent_items else use_first[:3]

        if display_items and active_ingredients:
            for item in display_items[:3]:
                name = item.get("name", "Ingredient")
                qty = item.get("estimated_quantity", "1 item")
                window = item.get("estimated_use_window", "1–2 days")
                urgency = item.get("urgency_level", "HIGH")
                reason = item.get("reasoning", "Best used in your next meal to preserve peak freshness.")
                
                badge_bg = "#ef44441a" if urgency == "HIGH" else "#f59e0b1a"
                badge_color = "#ef4444" if urgency == "HIGH" else "#fbbf24"
                border_color = "#ef4444" if urgency == "HIGH" else "#f59e0b"

                card_c1, card_c2 = st.columns([3.2, 1.2])
                with card_c1:
                    st.markdown(
                        f"""
                        <div style="background: #1e293b; border: 1px solid #334155; border-left: 4px solid {border_color}; border-radius: 12px; padding: 14px 16px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 700; color: #ffffff; font-size: 15px;">{name} <span style="color: #94a3b8; font-size: 12px; font-weight: 400;">({qty})</span></span>
                                <span style="background: {badge_bg}; color: {badge_color}; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">
                                    {urgency} PRIORITY
                                </span>
                            </div>
                            <p style="color: #cbd5e1; font-size: 13px; margin: 2px 0 6px 0; line-height: 1.4;">
                                "{reason}"
                            </p>
                            <div style="font-size: 12px; color: #94a3b8;">
                                ⏱️ Estimated freshness: <strong style="color: #e2e8f0;">{window}</strong>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with card_c2:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.button("Find meal →", key=f"dash_cook_{name}_{item.get('id', '')}", use_container_width=True):
                        st.session_state.meal_context["craving"] = f"Using {name}"
                        st.session_state.active_tab = "Kitchen Agent"
                        st.rerun()

        elif active_ingredients:
            st.markdown(
                """
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; color: #cbd5e1; font-size: 14px;">
                    🌱 All current items have a stable freshness window.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; text-align: center;">
                    <p style="color: #cbd5e1; font-size: 14px; margin: 0 0 10px 0;">No ingredients yet. Scan your fridge and we'll help you figure out what to cook.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("📸 Scan my fridge", key="dash_empty_scan", type="primary"):
                st.session_state.active_tab = "Scanner"
                st.rerun()

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # 🍳 TODAY'S RECOMMENDATION
        st.markdown("<h2 style='color: #ffffff; font-weight: 800; font-size: 20px; margin: 0 0 14px 0;'>Today's recommendation</h2>", unsafe_allow_html=True)
        
        if generated_recipes:
            top_rec = generated_recipes[0]
            st.markdown(
                f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background: #064e3b; color: #34d399; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px;">
                            BEST MATCH
                        </span>
                        <span style="color: #94a3b8; font-size: 12px;">
                            ⏱️ {top_rec.get('cooking_time_minutes', 20)}m • 🍽️ {top_rec.get('servings', 2)} servings
                        </span>
                    </div>
                    <h3 style="color: #ffffff; font-size: 18px; font-weight: 800; margin: 4px 0 6px 0;">
                        {top_rec.get('title')}
                    </h3>
                    <p style="color: #cbd5e1; font-size: 13px; line-height: 1.5; margin: 0 0 12px 0;">
                        {top_rec.get('short_description')}
                    </p>
                    <div style="font-size: 12px; color: #10b981; font-weight: 600;">
                        ✓ Uses {int(top_rec.get('ingredient_utilization_percentage', 85))}% of available fridge ingredients
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            rec_col1, rec_col2 = st.columns(2)
            with rec_col1:
                if st.button("Start cooking", key="dash_start_cook_top", type="primary", use_container_width=True):
                    st.session_state.cooking_recipe = top_rec
                    st.session_state.cooking_step = 0
                    st.session_state.active_tab = "Cooking Mode"
                    st.rerun()
            with rec_col2:
                if st.button("View recipe", key="dash_view_rec_top", use_container_width=True):
                    st.session_state.selected_recipe = top_rec
                    st.session_state.active_tab = "Recipes"
                    st.rerun()
        else:
            st.markdown(
                """
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; text-align: center;">
                    <p style="color: #cbd5e1; font-size: 14px; margin: 0 0 10px 0;">
                        Ready for dinner? Tell us what you're craving to see personalized recipes.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("✨ What should I cook?", key="dash_gen_rec_btn", type="primary", use_container_width=True):
                st.session_state.active_tab = "Kitchen Agent"
                st.rerun()

    with right_col:
        # Kitchen Impact Summary
        df_inv = ingredients_to_df(active_ingredients) if active_ingredients else pd.DataFrame()

        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px;">
                    YOUR KITCHEN IMPACT
                </div>
                <div style="font-size: 24px; font-weight: 800; color: #10b981; margin-bottom: 2px;">
                    {len(saved_recipes)} saved recipes
                </div>
                <p style="color: #cbd5e1; font-size: 13px; margin: 0 0 12px 0;">
                    Recipes saved in this session.
                </p>
                <div style="border-top: 1px solid #334155; padding-top: 10px; font-size: 12px; color: #94a3b8; display: flex; justify-content: space-between;">
                    <span>Confirmed ingredients: <strong style="color: #ffffff;">{total_count}</strong></span>
                    <span>Recipes generated: <strong style="color: #ffffff;">{len(generated_recipes)}</strong></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("Food preferences", icon=":material/tune:"):
            st.caption("These preferences guide every recipe recommendation.")
            cuisine_choices = ["Indian", "Italian", "Chinese", "Mexican", "Thai", "Mediterranean", "Home-style"]
            preferred_cuisine = taste_profile.get("favorite_cuisines", ["Indian"])[0]
            cuisine_index = cuisine_choices.index(preferred_cuisine) if preferred_cuisine in cuisine_choices else 0
            diet_choices = ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian", "Jain"]
            current_diet = st.session_state.meal_context.get("diet", "Vegetarian")
            diet_index = diet_choices.index(current_diet) if current_diet in diet_choices else 0
            spice_choices = ["No Added Spice", "Mild", "Medium", "Spicy"]
            current_spice = st.session_state.meal_context.get("spice_level", "Medium")
            spice_index = spice_choices.index(current_spice) if current_spice in spice_choices else 2
            with st.form("dashboard_food_preferences"):
                first, second = st.columns(2)
                with first:
                    cuisine = st.selectbox("Favourite cuisine", cuisine_choices, index=cuisine_index)
                    diet = st.selectbox("Diet type", diet_choices, index=diet_index)
                with second:
                    spice = st.select_slider("Spice level", spice_choices, value=spice_choices[spice_index])
                    allergies = st.text_input("Allergies or ingredients to avoid", value=", ".join(st.session_state.meal_context.get("avoid_list", [])))
                save_preferences = st.form_submit_button("Save preferences", type="primary", width="stretch")
            if save_preferences:
                st.session_state.taste_profile["favorite_cuisines"] = [cuisine]
                st.session_state.taste_profile["preferred_spice"] = spice
                st.session_state.meal_context["diet"] = diet
                st.session_state.meal_context["spice_level"] = spice
                st.session_state.meal_context["avoid_list"] = [item.strip() for item in allergies.split(",") if item.strip()]
                st.toast("Food preferences saved")
                st.rerun()

        # Freshness reminders if any
        if urgent_items:
            st.markdown("<h3 style='color: #ffffff; font-size: 16px; font-weight: 800; margin: 0 0 8px 0;'>Freshness reminders</h3>", unsafe_allow_html=True)
            for u_item in urgent_items[:2]:
                u_name = u_item.get("name", "Ingredient")
                u_win = u_item.get("estimated_use_window", "1–2 days")
                is_reminded = any(r.get("ingredient") == u_name for r in reminders)
                
                fa_col1, fa_col2 = st.columns([2.5, 1.2])
                with fa_col1:
                    st.markdown(
                        f"""
                        <div style="font-size: 13px; color: #cbd5e1; padding: 6px 0;">
                            🥬 <strong>{u_name}</strong> (Best within {u_win})
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with fa_col2:
                    if is_reminded:
                        st.caption("✓ Set")
                    else:
                        if st.button("Remind", key=f"dash_rem_btn_{u_name}", use_container_width=True):
                            st.session_state.active_reminders.append({
                                "ingredient": u_name,
                                "urgency": "HIGH",
                                "use_by": u_win
                            })
                            st.success(f"Reminder set!")
                            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # My Taste Profile (Compact & human)
        st.markdown("<h3 style='color: #ffffff; font-size: 16px; font-weight: 800; margin: 0 0 8px 0;'>Your taste profile</h3>", unsafe_allow_html=True)
        fav_cuisines = ", ".join(taste_profile.get("favorite_cuisines", ["Home-style", "Comfort"])) or "All Cuisines"
        spice_pref = taste_profile.get("spice_preference", "Medium")
        
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 14px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <div>🍲 <strong>Favorite flavors:</strong> <span style="color: #ffffff;">{fav_cuisines}</span></div>
                <div>🌶️ <strong>Spice level:</strong> <span style="color: #ffffff;">{spice_pref}</span></div>
                <div>⭐ <strong>Recipes cooked:</strong> <span style="color: #10b981; font-weight: 700;">{len(saved_recipes)}</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
