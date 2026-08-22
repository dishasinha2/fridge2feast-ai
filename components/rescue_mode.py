import streamlit as st
from utils.pandas_utils import get_use_first_ingredients
from services.decision_services import generate_rescue_plan
from services.gemini_client import GeminiServiceException

def render_rescue_component():
    """
    Renders the Rescue Your Fridge sustainability experience.
    Helps users save food, prevent spoilage, and reduce unnecessary grocery spending.
    """
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; margin: 0 0 6px 0;">
                Rescue Your Fridge
            </h1>
            <p style="color: #cbd5e1; font-size: 15px; margin: 0;">
                Turn fresh, perishable ingredients into delicious meals before they go to waste.
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
                <p style="color: #cbd5e1; font-size: 15px; margin: 0 0 16px 0;">
                    Your inventory is currently empty. Take a photo or add items to see which need attention.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📸 Scan my fridge", type="primary", use_container_width=True):
            st.session_state.active_tab = "Scanner"
            st.rerun()
        return

    # Perishable ingredients
    use_first_list = get_use_first_ingredients(active_ingredients)
    urgent_items = [i for i in use_first_list if i.get("urgency_level") == "HIGH"]
    summary_items = urgent_items if urgent_items else use_first_list[:3]

    # Impact potential bar
    est_savings_inr = len(summary_items) * 65
    st.markdown(
        f"""
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 16px 20px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <span style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase; letter-spacing: 0.5px;">
                    POTENTIAL IMPACT
                </span>
                <div style="color: #ffffff; font-size: 16px; font-weight: 700; margin-top: 2px;">
                    {len(summary_items)} items ready for cooking (~₹{est_savings_inr} value saved)
                </div>
            </div>
            <div style="font-size: 13px; color: #94a3b8;">
                🌱 Save food • 💰 Save budget
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h3 style='color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 12px;'>Perishable items that need a home</h3>", unsafe_allow_html=True)

    reminders = st.session_state.get("active_reminders", [])

    for idx, item in enumerate(summary_items):
        name = item.get("name", "Ingredient")
        qty = item.get("estimated_quantity", "1 item")
        urgency = item.get("urgency_level", "HIGH")
        window = item.get("estimated_use_window", "1–2 days")
        reason = item.get("reasoning", "Best consumed soon for peak flavor and nutrition.")
        
        card_col1, card_col2 = st.columns([4, 1.2])
        with card_col1:
            st.markdown(
                f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-left: 3px solid {'#f59e0b' if urgency == 'HIGH' else '#10b981'}; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #ffffff; font-weight: 700; font-size: 14px;">{name} <span style="color: #94a3b8; font-weight: 400; font-size: 12px;">({qty})</span></span>
                        <span style="font-size: 12px; color: {'#fbbf24' if urgency == 'HIGH' else '#10b981'}; font-weight: 600;">
                            Cook within {window}
                        </span>
                    </div>
                    <p style="color: #cbd5e1; font-size: 12px; margin: 4px 0 0 0;">{reason}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with card_col2:
            is_reminded = any(r.get("ingredient") == name for r in reminders)
            if is_reminded:
                st.button("🔔 Reminded", key=f"rescue_rem_{item.get('id', idx)}", disabled=True, use_container_width=True)
            else:
                if st.button("Remind me", key=f"rescue_rem_{item.get('id', idx)}", use_container_width=True):
                    st.session_state.active_reminders.append({
                        "ingredient": name,
                        "urgency": urgency,
                        "use_by": window,
                    })
                    st.success(f"Reminder active for {name}")
                    st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # CTA: Create rescue plan
    if st.button("✨ Create zero-waste rescue plan", type="primary", use_container_width=True):
        with st.spinner("Finding the best recipe combination for your perishable items..."):
            try:
                plan = generate_rescue_plan(
                    urgent_ingredients=summary_items,
                    all_ingredients=active_ingredients,
                    meal_context=st.session_state.get("meal_context", {})
                )
                st.session_state.rescue_plan = plan
                st.rerun()
            except GeminiServiceException as ge:
                st.error(ge.user_message)
            except Exception:
                st.error("Could not generate rescue plan at this moment. Please try again.")

    # High-Efficiency Rescue Recipes Display
    plan = st.session_state.get("rescue_plan")
    if plan:
        st.markdown("<div style='border-top: 1px solid #334155; margin-top: 24px; padding-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #10b981; border-radius: 14px; padding: 18px 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <h3 style="color: #ffffff; font-size: 18px; font-weight: 800; margin: 0;">{plan.get('plan_title', 'Zero-Waste Rescue Menu')}</h3>
                    <span style="background: #10b98122; color: #10b981; font-weight: 700; font-size: 12px; padding: 3px 10px; border-radius: 8px;">
                        {plan.get('target_utilization_pct', 85)}% Waste Prevention
                    </span>
                </div>
                <p style="color: #cbd5e1; font-size: 13px; margin: 8px 0 0 0; line-height: 1.4;">
                    {plan.get('sustainability_note', 'Crafted to efficiently combine perishable ingredients.')}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        meals = plan.get("meals", [])
        m_cols = st.columns(len(meals) if meals else 1)
        for idx, meal in enumerate(meals):
            with m_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <span style="color: #10b981; font-weight: 700; font-size: 11px; text-transform: uppercase;">
                                {meal.get('day', f'Meal {idx+1}')}
                            </span>
                            <h4 style="color: #ffffff; font-weight: 700; font-size: 15px; margin: 4px 0 6px 0;">{meal.get('meal_name')}</h4>
                            <p style="color: #cbd5e1; font-size: 12px; margin-bottom: 10px; line-height: 1.4;">{meal.get('short_instructions')}</p>
                        </div>
                        <div style="padding-top: 8px; border-top: 1px solid #334155;">
                            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">
                                🥬 Rescues: <strong style="color: #ffffff;">{', '.join(meal.get('key_ingredients_rescued', []))}</strong>
                            </div>
                            <span style="color: #94a3b8; font-size: 11px;">⏱️ {meal.get('prep_time_minutes', 20)} mins</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
