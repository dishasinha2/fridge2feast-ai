"""Authenticated Dashboard Component for Fridge2Feast AI."""
import streamlit as st
from datetime import datetime
from services.kitchen_service import get_kitchen_summary, get_expiring_ingredients
from services.recipe_service import get_saved_recipes
from services.recommendation_service import get_personalized_recommendations
from services.notification_service import get_user_notifications, mark_notification_read
from services.auth_service import update_user_preferences
from textwrap import dedent

def get_greeting() -> str:
    """Return friendly time-of-day greeting."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def render_section_navigation():
    """Render the existing application sections in a touch-friendly row."""
    st.markdown("""
        <style>
        .st-key-section-navigation {
            width: 100%;
            max-width: 100%;
            overflow: hidden;
        }
        .st-key-section-navigation [data-testid="stPills"] {
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            overflow-x: auto;
            overflow-y: hidden;
            width: 100%;
            max-width: 100%;
            gap: 0.5rem;
            padding: 0.25rem 0 0.75rem;
            white-space: nowrap;
            scrollbar-width: none;
        }
        .st-key-section-navigation [data-testid="stPills"]::-webkit-scrollbar { display: none; }
        .st-key-section-navigation [data-testid="stPills"] > div {
            flex: 0 0 auto;
            white-space: nowrap;
            word-break: keep-all;
            overflow-wrap: normal;
            hyphens: none;
        }
        .dashboard-hero h1 {
            white-space: nowrap;
        }
        @media (max-width: 600px) {
            .dashboard-hero h1 {
                font-size: 1.85rem !important;
                white-space: normal;
                overflow-wrap: normal;
                word-break: keep-all;
            }
            .dashboard-hero p {
                font-size: 0.9rem !important;
            }
            [data-testid="stHorizontalBlock"]:has(.metric-card) {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.75rem;
            }
            [data-testid="stHorizontalBlock"]:has(.metric-card) > [data-testid="column"] {
                width: auto !important;
                min-width: 0 !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    pages = [("Home", "dashboard"), ("Scanner", "scanner"), ("Kitchen", "kitchen"), ("Recipes", "recipes"), ("Saved", "saved")]
    page_labels = [label for label, _ in pages]
    current_label = next(label for label, page in pages if page == st.session_state.current_page)
    with st.container(key="section-navigation"):
        selected_label = st.pills(
            "Sections",
            page_labels,
            default=current_label,
            label_visibility="collapsed",
            key="section_navigation_pills",
        )
    if selected_label and selected_label != current_label:
        st.session_state.current_page = dict(pages)[selected_label]
        st.rerun()

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
    st.markdown(dedent(f"""
        <div class="dashboard-hero" style="margin-bottom: 1.5rem;">
            <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.6rem; color: #2D3425; margin-bottom: 0.2rem; font-style: italic; font-weight: 700;">
                {greeting}, {first_name}
            </h1>
            <p style="font-size: 1.1rem; color: #5A644D; margin: 0;">
                Let's see what's fresh in your kitchen today.
            </p>
        </div>
    """), unsafe_allow_html=True)

    render_section_navigation()

    # 2. Action Pill Buttons
    b1, b2, b3 = st.columns([1.6, 1.3, 1.3])
    with b1:
        if summary["total_count"] and st.button("What should I cook?", width="stretch", type="primary"):
            st.session_state.current_page = "recipes"
            st.session_state.recipe_flow_stage = "preferences"
            st.rerun()
        elif not summary["total_count"]:
            st.info("Your kitchen is empty.")
    with b2:
        if st.button("📷 Scan my fridge", width="stretch"):
            st.session_state.current_page = "scanner"
            st.rerun()
    with b3:
        if not summary["total_count"]:
            if st.button("Add Ingredients", width="stretch"):
                st.session_state.current_page = "kitchen"
                st.rerun()
        elif st.button("♻️ Rescue items", width="stretch"):
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
    card_style = "background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 16px; padding: 1.25rem 0.75rem; text-align: center; height: 164px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(45,52,37,0.06); box-sizing: border-box;"

    def render_metric_card(icon, value, label):
        st.markdown(dedent(f"""
            <div class="metric-card" style="{card_style}">
                <div style="font-size: 1.25rem; line-height: 1.2; height: 1.5rem;">{icon}</div>
                <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.45rem; font-weight: 700; color: #A6382A; line-height: 1.05; margin-top: 0.35rem;">{value}</div>
                <div style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; color: #5A644D; margin-top: 0.45rem; text-transform: uppercase; white-space: nowrap;">{label}</div>
            </div>
        """), unsafe_allow_html=True)

    with m1:
        render_metric_card("🥕", summary["total_count"], "Ingredients")

    with m2:
        render_metric_card("⏳", summary["expiring_count"], "Use Soon")

    with m3:
        render_metric_card("📖", saved_count, "Saved Recipes")

    with m4:
        score = summary['zero_waste_score']
        render_metric_card("♻️", f"{score}%", "Zero-Waste Goal")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 5. Food Preferences Card
    st.markdown(dedent("""
        <div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 20px; padding: 1.75rem; box-shadow: 0 4px 16px rgba(45,52,37,0.03);">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                <span style="font-size: 1.2rem;">⚙️</span>
                <h3 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem; color: #2D3425; margin: 0;">
                    Food Preferences & Taste Profile
                </h3>
            </div>
        </div>
    """), unsafe_allow_html=True)

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
        st.markdown(dedent(f"""
            <div style="background: #F4EFE2; border: 1px solid #E2D9C5; border-radius: 16px; padding: 1.25rem 1.5rem; margin-top: 1rem;">
                <h4 style="font-family: 'Playfair Display', serif; color: #2D3425; margin: 0 0 0.5rem 0;">
                    💡 Chef's Zero-Waste Rescue Ideas
                </h4>
                <ul style="margin: 0; padding-left: 1.25rem; color: #4E593D; line-height: 1.6;">
                    {''.join(f'<li>{idea}</li>' for idea in recommendations['rescue_ideas'])}
                </ul>
            </div>
        """), unsafe_allow_html=True)
