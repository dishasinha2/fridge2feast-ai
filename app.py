"""Fridge2Feast AI - Primary Application Entry Point.
Turn What's Left Into What's Next.
"""
import streamlit as st
from utils.database import init_db
from components.landing import render_landing
from components.auth import render_auth
from components.dashboard import render_dashboard
from components.scanner import render_scanner
from components.kitchen import render_kitchen
from components.recipes import render_recipes
from components.saved import render_saved
from components.cooking import render_cooking

# Page Configuration
st.set_page_config(
    page_title="Fridge2Feast AI",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Warm Kitchen Aesthetic matching Reference Design
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #2D3425;
}

h1, h2, h3, .serif-heading {
    font-family: 'Playfair Display', Georgia, serif !important;
}

/* Base canvas */
.stApp {
    background-color: #FBF8F1;
}

/* Ensure no text in buttons or badges wraps mid-word */
.stButton > button,
button[kind="primary"],
button[kind="secondary"] {
    white-space: nowrap !important;
    word-break: keep-all !important;
    word-wrap: normal !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
    -webkit-hyphens: none !important;
    border-radius: 24px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.45rem 0.9rem !important;
    line-height: 1.2 !important;
    transition: all 0.2s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Primary buttons (Terracotta / Coral) */
button[kind="primary"], .stButton > button[kind="primary"] {
    background-color: #C84B31 !important;
    color: #FFFFFF !important;
    border: none !important;
}
button[kind="primary"]:hover {
    background-color: #B33E26 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(200,75,49,0.2) !important;
}

/* Secondary standard buttons */
.stButton > button {
    border: 1px solid #D5CDBC !important;
    background-color: #FFFFFF !important;
    color: #3B4430 !important;
}
.stButton > button:hover {
    border-color: #556B2F !important;
    color: #556B2F !important;
    background-color: #F8F6EF !important;
}

/* Form inputs & select boxes */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    border-radius: 12px !important;
    border: 1px solid #D5CDBC !important;
    background-color: #FFFFFF !important;
    color: #2D3425 !important;
}

/* Top header bar */
.top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #EAE4D5;
}

.st-key-top-navigation [data-testid="stHorizontalBlock"] {
    align-items: center;
    flex-wrap: nowrap;
}

.top-brand,
.top-greeting {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

@media (max-width: 600px) {
    .st-key-top-navigation [data-testid="stHorizontalBlock"] {
        gap: 0.35rem;
    }

    .top-brand span {
        font-size: 1rem !important;
    }

    .top-greeting {
        font-size: 0.78rem !important;
    }

    .st-key-top-navigation .stButton > button {
        width: auto !important;
        min-width: 0 !important;
        padding: 0.4rem 0.65rem !important;
    }
}

/* Remove streamlit footer and menu for clean aesthetic */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize database tables
init_db()

# Initialize Session State Variables
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"

# Journey state only; authenticated inventory remains in SQLite.
st.session_state.setdefault("last_scan_ingredients", [])
st.session_state.setdefault("recipe_preferences", {})
st.session_state.setdefault("generated_recipe", None)
st.session_state.setdefault("recipe_flow_stage", "preferences")

def render_top_navigation():
    """Render top application navigation bar with wide responsive layout."""
    user = st.session_state.authenticated_user
    if not user:
        return

    with st.container(key="top-navigation"):
        c_brand, c_user, c_out = st.columns([2.4, 1.2, 0.95])

        with c_brand:
            st.markdown("""<div class="top-brand" style="display: flex; align-items: center; gap: 0.5rem; padding-top: 6px;">
            <div style="width: 32px; height: 32px; background: #556B2F; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px;">🍃</div>
            <span style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #2D3425;">Fridge2Feast AI</span>
        </div>""", unsafe_allow_html=True)

        with c_user:
            first_name = user.name.split()[0] if user.name else "Account"
            st.markdown(f"""<div class="top-greeting" style="text-align: right; padding-top: 8px; font-weight: 600; color: #556B2F; font-size: 0.9rem;">Hello, {first_name}</div>""", unsafe_allow_html=True)

        with c_out:
            if st.button("Logout", key="top_logout", width="content"):
                st.session_state.authenticated_user = None
                st.session_state.current_page = "landing"
                st.session_state.active_recipe = None
                st.session_state.pending_scan_items = None
                st.session_state.last_scan_ingredients = []
                st.session_state.recipe_preferences = {}
                st.session_state.generated_recipe = None
                st.session_state.cooking_recipe = None
                st.session_state.current_step_idx = 0
                st.rerun()

    st.markdown("<div style='border-bottom: 1px solid #EAE4D5; margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

def main():
    """Main application router."""
    user = st.session_state.authenticated_user

    # If unauthenticated, restrict to landing or auth pages
    if not user:
        if st.session_state.current_page not in ["landing", "auth"]:
            st.session_state.current_page = "landing"

        if st.session_state.current_page == "auth":
            render_auth()
        else:
            render_landing()
        return

    # Authenticated user flow
    render_top_navigation()

    page = st.session_state.current_page

    if page == "dashboard":
        render_dashboard()
    elif page == "scanner":
        render_scanner()
    elif page == "kitchen":
        render_kitchen()
    elif page == "recipes":
        render_recipes()
    elif page == "saved":
        render_saved()
    elif page == "cooking":
        render_cooking()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
