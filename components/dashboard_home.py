from datetime import datetime

import streamlit as st

from utils.pandas_utils import get_use_first_ingredients


def _open_recipes(ingredient_name: str | None = None) -> None:
    if ingredient_name:
        st.session_state.meal_context["craving"] = f"Using {ingredient_name}"
    st.session_state.active_tab = "Kitchen Agent"
    st.rerun()


def render_dashboard_component() -> None:
    """The focused home screen for scan → verify → decide → cook."""
    user_name = st.session_state.get("user", {}).get("name", "Chef")
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    ingredients = [item for item in st.session_state.get("detected_ingredients", []) if item.get("included", True)]
    use_first = get_use_first_ingredients(ingredients) if ingredients else []
    urgent_items = [item for item in use_first if item.get("urgency_level") == "HIGH"]

    st.title(f"{greeting}, {user_name}")
    st.caption("Turn what’s left into what’s next.")

    if not ingredients:
        st.subheader("My Kitchen is empty", anchor=False)
        st.write("Scan your fridge and we’ll help you decide what to cook.")
        if st.button("Scan my fridge", icon=":material/photo_camera:", type="primary", key="home_empty_scan"):
            st.session_state.active_tab = "Scanner"
            st.rerun()
        return

    st.subheader("Your kitchen", anchor=False)
    summary_left, summary_right = st.columns(2)
    with summary_left:
        st.metric("Ingredients", len(ingredients))
    with summary_right:
        st.metric("Need using soon", len(urgent_items))

    with st.container(horizontal=True):
        if st.button("What’s cooking tonight?", icon=":material/restaurant:", type="primary", key="home_decide"):
            _open_recipes()
        if st.button("Scan my fridge", icon=":material/photo_camera:", key="home_scan"):
            st.session_state.active_tab = "Scanner"
            st.rerun()

    st.subheader("Use soon", anchor=False)
    items_to_show = urgent_items or use_first[:3]
    if not items_to_show:
        st.caption("Everything in your kitchen has a comfortable freshness window.")
        return

    for index, item in enumerate(items_to_show[:3]):
        name = item.get("name", "Ingredient")
        quantity = item.get("estimated_quantity", "As needed")
        window = item.get("estimated_use_window", "the next few days")
        left, right = st.columns([4, 1], vertical_alignment="center")
        with left:
            st.write(f"**{name}** · {quantity}")
            st.caption(f"Best used in {window}")
        with right:
            if st.button("Cook with this", key=f"home_cook_{index}_{name}", width="stretch"):
                _open_recipes(name)
