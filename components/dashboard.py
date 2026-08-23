"""Authenticated Dashboard Component for Fridge2Feast AI."""
import streamlit as st
from datetime import datetime
from services.kitchen_service import get_kitchen_summary, get_expiring_ingredients
from services.recipe_service import get_saved_recipes
from services.recommendation_service import get_personalized_recommendations
from services.notification_service import get_user_notifications, mark_notification_read
from services.auth_service import update_user_preferences

def get_greeting() -> str:
    """Return friendly time-of-day greeting."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def render_dashboard():
    """Render the dashboard matching the visual craft of Reference Image 1."""
    user = st.session_state.authenticated_user
    if not user:
        st.session_state.current_page = "landing"
        st.rerun()

    greeting = get_greeting()
    first_name = user.name.split()[0] if user.name else "Chef"

    # Kitchen metrics from SQLite
    summary = get_kitchen_summary(user.id)
    saved_recipes = get_saved_recipes(user.id)
    saved_count = len(saved_recipes)
    expiring_items = get_expiring_ingredients(user.id)
    notifications = get_user_notifications(user.id, unread_only=True)
    recommendations = get_personalized_recommendations(user.id, user.preferences)

    # 1. Header & Greeting
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.6rem; color: #2D3425; margin-bottom: 0.2rem; font-style: italic; font-weight: 700;">
                {greeting}, {first_name}
            </h1>
            <p style="font-size: 1.1rem; color: #5A644D; margin: 0;">
                Let's see what's fresh in your kitchen today.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Action Pill Buttons
    b1, b2, b3 = st.columns([1.6, 1.3, 1.3])
    with b1:
        if summary["total_count"] and st.button("What should I cook?", use_container_width=True, type="primary"):
            st.session_state.current_page = "recipes"
            st.session_state.recipe_flow_stage = "preferences"
            st.rerun()
        elif not summary["total_count"]:
            st.info("Your kitchen is empty.")
    with b2:
        if st.button("📷 Scan my fridge", use_container_width=True):
            st.session_state.current_page = "scanner"
            st.rerun()
    with b3:
        if not summary["total_count"]:
            if st.button("Add Ingredients", use_container_width=True):
                st.session_state.current_page = "kitchen"
                st.rerun()
        elif st.button("♻️ Rescue items", use_container_width=True):
            st.session_state.current_page = "recipes"
            st.session_state.rescue_mode = True
            st.session_state.recipe_flow_stage = "preferences"
            st.rerun()

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 3. Notification alerts if expiring items exist
    if notifications:
        for notif in notifications[:2]:
            st.markdown(f"""<div style="background: #FFF4E5; border: 1px solid #FFD8A8; border-left: 5px solid #C84B31; border-radius: 12px; padding: 0.85rem 1.2rem; margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between;">
<div>
<strong style="color: #C84B31; font-size: 0.95rem;">⚠️ {notif['title']}</strong>
<div style="color: #664D3B; font-size: 0.88rem; margin-top: 0.15rem;">{notif['message']}</div>
</div>
</div>""", unsafe_allow_html=True)

    # 4. Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""<div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 20px; padding: 1.75rem 1.25rem; text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 16px rgba(45,52,37,0.03);">
<div style="font-family: 'Playfair Display', Georgia, serif; font-size: 3.2rem; font-weight: 700; color: #C84B31; line-height: 1;">{summary['total_count']}</div>
<div style="font-size: 0.82rem; font-weight: 700; letter-spacing: 1.5px; color: #5A644D; margin-top: 0.75rem; text-transform: uppercase;">INGREDIENTS</div>
</div>""", unsafe_allow_html=True)

    with m2:
        alert_badge = '<div style="position: absolute; top: 12px; right: 12px; background: #C84B31; color: white; font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 8px;">Alert</div>' if summary['expiring_count'] > 0 else ''
        st.markdown(f"""<div style="position: relative; background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 20px; padding: 1.75rem 1.25rem; text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 16px rgba(45,52,37,0.03);">
{alert_badge}
<div style="font-family: 'Playfair Display', Georgia, serif; font-size: 3.2rem; font-weight: 700; color: #C84B31; line-height: 1;">{summary['expiring_count']}</div>
<div style="font-size: 0.82rem; font-weight: 700; letter-spacing: 1.5px; color: #5A644D; margin-top: 0.75rem; text-transform: uppercase;">USE SOON</div>
</div>""", unsafe_allow_html=True)

    with m3:
        st.markdown(f"""<div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 20px; padding: 1.75rem 1.25rem; text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 16px rgba(45,52,37,0.03);">
<div style="font-family: 'Playfair Display', Georgia, serif; font-size: 3.2rem; font-weight: 700; color: #C84B31; line-height: 1;">{saved_count}</div>
<div style="font-size: 0.82rem; font-weight: 700; letter-spacing: 1.5px; color: #5A644D; margin-top: 0.75rem; text-transform: uppercase;">SAVED RECIPES</div>
</div>""", unsafe_allow_html=True)

    with m4:
        score = summary['zero_waste_score']
        rescue_msg = f"{summary['expiring_count']} items require rescue" if summary['expiring_count'] > 0 else "Pantry freshness is optimal!"
        st.markdown(f"""<div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 20px; padding: 1.5rem 1.25rem; height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 16px rgba(45,52,37,0.03);">
<div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 600; color: #2D3425;">Zero-Waste Goal</div>
<div>
<div style="background: #EBE5D6; border-radius: 10px; height: 10px; overflow: hidden; width: 100%;">
<div style="background: #556B2F; height: 100%; width: {score}%;"></div>
</div>
<div style="text-align: right; font-size: 0.85rem; font-weight: 600; color: #556B2F; margin-top: 0.4rem;">{score}% Utilized</div>
</div>
<div style="font-size: 0.8rem; color: #7B856E;">{rescue_msg}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 5. Food Preferences Card
    st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 20px; padding: 1.75rem; box-shadow: 0 4px 16px rgba(45,52,37,0.03);">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                <span style="font-size: 1.2rem;">⚙️</span>
                <h3 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem; color: #2D3425; margin: 0;">
                    Food Preferences & Taste Profile
                </h3>
            </div>
        </div>
    """, unsafe_allow_html=True)

    pref = user.preferences
    current_cuisines = pref.get("cuisines", ["Italian", "Indian", "Mexican"])
    current_diet = pref.get("dietary", ["Vegetarian"])
    current_spice = pref.get("spice_level", "Medium")

    with st.expander("✏️ Customize Your Culinary Preferences", expanded=False):
        all_cuisines = ["Indian", "Italian", "Mexican", "Thai", "Chinese", "Mediterranean", "Japanese", "French", "American"]
        selected_cuisines = st.multiselect("Favorite Cuisines", all_cuisines, default=[c for c in current_cuisines if c in all_cuisines])
        
        all_diets = ["Vegetarian", "Non-vegetarian", "Vegan", "Dairy-Free", "Gluten-Free", "Nut-Free", "Keto", "Halal", "Kosher"]
        selected_diets = st.multiselect("Dietary Requirements", all_diets, default=[d for d in current_diet if d in all_diets])
        
        selected_spice = st.select_slider("Preferred Spice Level", ["Mild", "Medium", "Spicy", "Hot"], value=current_spice if current_spice in ["Mild", "Medium", "Spicy", "Hot"] else "Medium")
        
        if st.button("Save Preferences", type="primary"):
            new_prefs = {
                "cuisines": selected_cuisines,
                "dietary": selected_diets,
                "spice_level": selected_spice,
                "default_servings": pref.get("default_servings", 2),
                "prioritized_ingredients": pref.get("prioritized_ingredients", []),
                "avoided_ingredients": pref.get("avoided_ingredients", [])
            }
            update_user_preferences(user.id, new_prefs)
            user.preferences = new_prefs
            st.session_state.authenticated_user = user
            st.success("Preferences updated!")
            st.rerun()

    # 6. Personalized Recommendations Section
    if recommendations.get("rescue_ideas"):
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background: #F4EFE2; border: 1px solid #E2D9C5; border-radius: 16px; padding: 1.25rem 1.5rem; margin-top: 1rem;">
                <h4 style="font-family: 'Playfair Display', serif; color: #2D3425; margin: 0 0 0.5rem 0;">
                    💡 Chef's Zero-Waste Rescue Ideas
                </h4>
                <ul style="margin: 0; padding-left: 1.25rem; color: #4E593D; line-height: 1.6;">
                    {''.join(f'<li>{idea}</li>' for idea in recommendations['rescue_ideas'])}
                </ul>
            </div>
        """, unsafe_allow_html=True)
