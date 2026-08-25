import streamlit as st
from services.decision_services import generate_ai_meal_planner, generate_leftover_transformations
from services.gemini_client import GeminiServiceException

def render_planner_component():
    """
    Renders the Meal Planner & Leftover Loop experience.
    Timeline-style schedule organizing meals across days to prevent waste and save time.
    """
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; margin: 0 0 6px 0;">
                Meal Planning & Leftovers
            </h1>
            <p style="color: #cbd5e1; font-size: 15px; margin: 0;">
                Plan out balanced meals using your on-hand ingredients or transform cooked leftovers.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    plan_subtab = st.radio(
        "Planner Subtab",
        ["🗓️ Multi-Day Schedule", "🍲 Leftover Transformations"],
        horizontal=True,
        label_visibility="collapsed"
    )

    ingredients = st.session_state.get("detected_ingredients", [])
    meal_context = st.session_state.get("meal_context", {})

    if "Schedule" in plan_subtab:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # Duration selector
        d_col1, d_col2, d_col3 = st.columns(3)
        current_days = st.session_state.get("planner_days", 3)
        
        with d_col1:
            if st.button("1 Day Plan", key="p_dur_1", type="primary" if current_days == 1 else "secondary", width="stretch"):
                st.session_state.planner_days = 1
                st.session_state.planner_goal = "Daily Smart Plan"
                st.rerun()
        with d_col2:
            if st.button("3 Days (Recommended)", key="p_dur_3", type="primary" if current_days == 3 else "secondary", width="stretch"):
                st.session_state.planner_days = 3
                st.session_state.planner_goal = "Zero-Waste Balanced"
                st.rerun()
        with d_col3:
            if st.button("7 Days Full Week", key="p_dur_7", type="primary" if current_days == 7 else "secondary", width="stretch"):
                st.session_state.planner_days = 7
                st.session_state.planner_goal = "Weekly Balanced"
                st.rerun()

        active_days = st.session_state.get("planner_days", 3)
        active_goal = st.session_state.get("planner_goal", "Zero-Waste Balanced")
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        if st.button(f"✨ Plan {active_days} days of meals", type="primary", width="stretch"):
            with st.spinner(f"Designing a {active_days}-day kitchen timeline for your pantry..."):
                try:
                    plan = generate_ai_meal_planner(
                        days=active_days,
                        goal=active_goal,
                        ingredients=ingredients,
                        meal_context=meal_context
                    )
                    st.session_state.meal_plan = plan
                    st.rerun()
                except GeminiServiceException as ge:
                    st.error(ge.user_message)
                except Exception:
                    st.error("Could not generate meal plan right now. Please try again.")

        plan_res = st.session_state.get("meal_plan")
        if plan_res:
            st.markdown("<div style='border-top: 1px solid #334155; margin: 24px 0 16px 0;'></div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="margin-bottom: 18px;">
                    <h3 style="color: #ffffff; font-size: 20px; font-weight: 700; margin: 0 0 4px 0;">
                        {plan_res.get('duration_days')}-Day Timeline
                    </h3>
                    <p style="color: #94a3b8; font-size: 13px; margin: 0;">
                        Organized to optimize fresh ingredient lifespans and minimize prep time.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            for day_idx, day in enumerate(plan_res.get("daily_schedule", [])):
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #334155;">
                            <span style="color: #10b981; font-weight: 800; font-size: 15px;">
                                {day.get('day_name', f'Day {day_idx + 1}')}
                            </span>
                            <span style="color: #cbd5e1; font-size: 12px;">
                                Focus: <strong>{', '.join(day.get('focus_ingredients', []))}</strong>
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px;">
                            <div>
                                <span style="font-size: 11px; color: #fbbf24; font-weight: 700; text-transform: uppercase;">Breakfast</span>
                                <div style="color: #ffffff; font-size: 13px; font-weight: 600; margin-top: 2px;">{day.get('breakfast')}</div>
                            </div>
                            <div>
                                <span style="font-size: 11px; color: #38bdf8; font-weight: 700; text-transform: uppercase;">Lunch</span>
                                <div style="color: #ffffff; font-size: 13px; font-weight: 600; margin-top: 2px;">{day.get('lunch')}</div>
                            </div>
                            <div>
                                <span style="font-size: 11px; color: #a78bfa; font-weight: 700; text-transform: uppercase;">Snack</span>
                                <div style="color: #ffffff; font-size: 13px; font-weight: 600; margin-top: 2px;">{day.get('snack')}</div>
                            </div>
                            <div>
                                <span style="font-size: 11px; color: #10b981; font-weight: 700; text-transform: uppercase;">Dinner</span>
                                <div style="color: #ffffff; font-size: 13px; font-weight: 600; margin-top: 2px;">{day.get('dinner')}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if plan_res.get("shopping_gap_items"):
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px 16px;">
                        <span style="color: #fbbf24; font-weight: 700; font-size: 13px;">Pantry staples to pick up:</span>
                        <p style="color: #cbd5e1; font-size: 13px; margin: 4px 0 0 0;">{', '.join(plan_res.get('shopping_gap_items', []))}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <p style="color: #cbd5e1; font-size: 14px; margin-bottom: 16px;">
                Got leftover cooked rice, dal, roasted veggies, or proteins? Turn them into a fresh, appealing dish.
            </p>
            """,
            unsafe_allow_html=True
        )

        l_dish = st.text_input("What cooked leftover do you have?", placeholder="e.g. Cooked rice, roasted chicken, yellow dal")
        l_extras = st.text_input("Any pantry items on hand?", placeholder="e.g. Eggs, onions, tortillas, cheese, herbs")

        if st.button("Transform leftovers into a new meal", type="primary", width="stretch"):
            if not l_dish:
                st.warning("Please enter a leftover dish to transform.")
            else:
                with st.spinner("Finding creative transformation recipes..."):
                    try:
                        res = generate_leftover_transformations(
                            dish_name=l_dish,
                            ingredients_left=l_extras or "Standard kitchen pantry staples",
                            meal_context=meal_context
                        )
                        st.session_state.leftover_suggestions = res
                        st.rerun()
                    except GeminiServiceException as ge:
                        st.error(ge.user_message)
                    except Exception:
                        st.error("Could not transform leftovers right now. Please try again.")

        leftover_res = st.session_state.get("leftover_suggestions")
        if leftover_res:
            st.markdown("<div style='border-top: 1px solid #334155; margin: 24px 0 16px 0;'></div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color: #ffffff; font-size: 18px; font-weight: 700;'>Ideas for {leftover_res.get('original_dish')}</h3>", unsafe_allow_html=True)
            
            ideas = leftover_res.get("ideas", [])
            for idx, idea in enumerate(ideas):
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-left: 3px solid #10b981; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="color: #ffffff; font-weight: 700; font-size: 16px; margin: 0;">{idea.get('transformation_name')}</h4>
                            <span style="font-size: 12px; color: #94a3b8;">
                                {idea.get('dish_type')} • ⏱️ {idea.get('time_minutes')}m
                            </span>
                        </div>
                        <p style="color: #cbd5e1; font-size: 13px; margin: 8px 0 6px 0; line-height: 1.4;">{idea.get('instructions')}</p>
                        <div style="font-size: 12px; color: #10b981; margin-top: 4px;">
                            Food safety: <span style="color: #cbd5e1;">{idea.get('food_safety_tip')}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
