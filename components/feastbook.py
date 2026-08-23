import streamlit as st

def render_feastbook_component():
    """
    Renders the Feastbook — Personal Cookbook Library.
    Editorial cookbook grid with search, recipe cards, notes, and Cook Again actions.
    """
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; margin: 0 0 6px 0;">
                Saved recipes
            </h1>
            <p style="color: #cbd5e1; font-size: 15px; margin: 0;">
                The recipes you want to make again.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    saved_recipes = st.session_state.get("saved_recipes", [])

    if not saved_recipes:
        st.markdown(
            """
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 28px; text-align: center; margin: 24px 0;">
                <div style="font-size: 28px; margin-bottom: 8px;">📖</div>
                <h3 style="color: #ffffff; font-size: 18px; font-weight: 700; margin: 0 0 6px 0;">
                    Your cookbook is empty
                </h3>
                <p style="color: #cbd5e1; font-size: 14px; margin: 0 0 16px 0;">
                    When you find a recipe you enjoy, save it to build your customized kitchen collection.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🍳 Explore recipe suggestions", type="primary", use_container_width=True):
            st.session_state.active_tab = "Recipe Dashboard"
            st.rerun()
        return

    # Search bar & stats
    s_col1, s_col2 = st.columns([3, 1])
    with s_col1:
        search_query = st.text_input("Search recipes", placeholder="Search by name, cuisine, or ingredient...", label_visibility="collapsed")
    with s_col2:
        st.markdown(f"<div style='color: #10b981; font-weight: 700; font-size: 14px; text-align: right; padding-top: 8px;'>{len(saved_recipes)} saved recipe(s)</div>", unsafe_allow_html=True)

    filtered_recipes = [
        r for r in saved_recipes
        if not search_query or (search_query.lower() in r.get("title", "").lower() or search_query.lower() in r.get("cuisine", "").lower())
    ]

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2-Column Editorial Grid for Saved Recipes
    cols = st.columns(2)
    for idx, r in enumerate(filtered_recipes):
        col_idx = idx % 2
        with cols[col_idx]:
            title = r.get("title", "Delicious Meal")
            time_m = r.get("cooking_time_minutes", 25)
            servings = r.get("servings", 2)
            cuisine = r.get("cuisine", "Home-style")
            desc = r.get("short_description", "")
            util = int(r.get("ingredient_utilization_percentage", 85))

            st.markdown(
                f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 18px; min-height: 220px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 16px;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="color: #10b981; font-size: 11px; font-weight: 700; text-transform: uppercase;">
                                {cuisine}
                            </span>
                            <span style="font-size: 12px; color: #94a3b8;">
                                ⏱️ {time_m} mins • {servings} servings
                            </span>
                        </div>
                        <h3 style="color: #ffffff; font-size: 17px; font-weight: 700; margin: 4px 0 6px 0; line-height: 1.3;">
                            {title}
                        </h3>
                        <p style="color: #cbd5e1; font-size: 13px; margin: 0 0 12px 0; line-height: 1.4;">
                            {desc}
                        </p>
                    </div>
                    <div style="font-size: 12px; color: #94a3b8; padding-top: 8px; border-top: 1px solid #334155;">
                        ♻️ {util}% fridge items utilized
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            btn_col1, btn_col2 = st.columns([2, 1])
            with btn_col1:
                if st.button("Cook again", key=f"fb_cook_{r.get('id', idx)}", type="primary", use_container_width=True):
                    st.session_state.cooking_recipe = r
                    st.session_state.cooking_step = 0
                    st.session_state.active_tab = "Cooking Mode"
                    st.rerun()
            with btn_col2:
                if st.button("Remove", key=f"fb_del_{r.get('id', idx)}", use_container_width=True):
                    st.session_state.saved_recipes = [item for item in saved_recipes if item.get("title") != r.get("title")]
                    st.success("Removed from Feastbook")
                    st.rerun()
