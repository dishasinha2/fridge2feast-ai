import streamlit as st

from components.cooking_mode import render_cooking_mode_component
from components.dashboard_home import render_dashboard_component
from components.feastbook import render_feastbook_component
from components.inventory import render_inventory_component
from components.kitchen_agent import render_kitchen_agent_component
from components.recipe_dashboard import render_recipe_dashboard_component
from components.scanner import render_scanner_component
from components.shopping_list import render_shopping_list_component
from components.sous_chef import render_sous_chef_component
from services.auth_service import logout_user

NAVIGATION = {
    "Home": "Dashboard",
    "Scan": "Scanner",
    "My Kitchen": "Inventory",
    "Recipes": "Recipes",
    "Saved": "Feastbook",
}
SPECIAL_VIEWS = {"Cooking Mode", "Shopping List", "AI Sous-Chef"}


def _sync_navigation() -> None:
    st.session_state.active_tab = NAVIGATION[st.session_state.workspace_nav]


def render_authenticated_dashboard() -> None:
    """Render only customer-facing workspace views; diagnostics remain internal."""
    user = st.session_state.get("user")
    if not user:
        st.session_state.authenticated = False
        st.session_state.auth_view = "login"
        st.warning("Please log in to continue.")
        return
    user_name = user["name"]
    top_left, top_right = st.columns([4, 1], vertical_alignment="center")
    with top_left:
        st.markdown(f"<div class='brand-lockup'>Fridge<span>2</span>Feast <small>AI</small></div><p class='workspace-greeting'>Your zero-waste kitchen · Welcome back, {user_name}</p>", unsafe_allow_html=True)
    with top_right:
        with st.popover("Account", icon=":material/account_circle:"):
            st.write(user_name)
            st.caption(user["email"])
            st.caption("Your account details are kept private.")
            if st.button("Log out", icon=":material/logout:", width="stretch", key="dashboard_logout"):
                logout_user()
                st.rerun()

    current = st.session_state.get("active_tab", "Dashboard")
    if current not in SPECIAL_VIEWS:
        expected_label = next((label for label, view in NAVIGATION.items() if view == current), "Home")
        if st.session_state.get("workspace_nav") != expected_label:
            st.session_state.workspace_nav = expected_label
        st.segmented_control("Kitchen navigation", list(NAVIGATION), default=expected_label, selection_mode="single", label_visibility="collapsed", key="workspace_nav", on_change=_sync_navigation, width="stretch")
    elif st.button("Back to workspace", icon=":material/arrow_back:", key="back_to_workspace"):
        st.session_state.active_tab = "Recipes"
        st.rerun()

    views = {
        "Dashboard": render_dashboard_component, "Scanner": render_scanner_component,
        "Inventory": render_inventory_component, "Kitchen Agent": render_kitchen_agent_component,
        "Recipes": lambda: render_recipe_dashboard_component() if st.session_state.get("generated_recipes") else render_kitchen_agent_component(),
        "Cooking Mode": render_cooking_mode_component, "Shopping List": render_shopping_list_component,
        "AI Sous-Chef": render_sous_chef_component, "Feastbook": render_feastbook_component,
    }
    views.get(current, render_dashboard_component)()
