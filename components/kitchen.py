"""Kitchen Inventory Component for Fridge2Feast AI."""
import streamlit as st
from services.kitchen_service import (
    get_user_ingredients, add_ingredient, update_ingredient, delete_ingredient
)
from utils.validation import VALID_CATEGORIES, VALID_UNITS

def render_kitchen():
    """Render My Kitchen inventory and freshness tracking interface."""
    user = st.session_state.authenticated_user
    if not user:
        st.session_state.current_page = "landing"
        st.rerun()

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.4rem; color: #2D3425; margin-bottom: 0.2rem; font-style: italic;">
                🌿 My Kitchen & Pantry
            </h1>
            <p style="font-size: 1.05rem; color: #5A644D; margin: 0;">
                Track food freshness, manage ingredients, and minimize kitchen waste.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Search & Category Filters
    f1, f2, f3 = st.columns([2, 1.5, 1.2])
    with f1:
        search_query = st.text_input("🔍 Search ingredients", placeholder="Filter by name...", label_visibility="collapsed")
    with f2:
        category_options = ["All"] + VALID_CATEGORIES
        selected_category = st.selectbox("Filter Category", category_options, label_visibility="collapsed")
    with f3:
        sort_by = st.selectbox("Sort By", ["freshness", "name", "category"], format_func=lambda x: {"freshness": "Urgency (Use Soon)", "name": "Name (A-Z)", "category": "Category"}.get(x, x), label_visibility="collapsed")

    # Fetch real user items from SQLite
    ingredients = get_user_ingredients(user.id, category=selected_category, search_query=search_query, sort_by=sort_by)

    # Top Actions: Add ingredient manually / Scan fridge
    with st.expander("➕ Add Ingredient Manually", expanded=False):
        with st.form("manual_add_form", clear_on_submit=True):
            a1, a2, a3, a4 = st.columns(4)
            with a1:
                new_name = st.text_input("Ingredient Name*", placeholder="e.g. Baby Spinach")
            with a2:
                new_cat = st.selectbox("Category", VALID_CATEGORIES)
            with a3:
                new_qty = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.5)
            with a4:
                new_unit = st.selectbox("Unit", VALID_UNITS)

            s1, s2 = st.columns(2)
            with s1:
                new_shelf = st.slider("Estimated Shelf Life (Days)", min_value=1, max_value=60, value=7)
            with s2:
                new_storage = st.text_input("Storage Advice", value="Keep in refrigerator crisper.")

            if st.form_submit_button("Add to Kitchen", type="primary"):
                if new_name.strip():
                    item_data = {
                        "name": new_name.strip(),
                        "category": new_cat,
                        "quantity": new_qty,
                        "unit": new_unit,
                        "estimated_shelf_life_days": new_shelf,
                        "storage_advice": new_storage,
                        "confidence": 1.0
                    }
                    add_ingredient(user.id, item_data)
                    st.success(f"Added {new_name.strip()} to My Kitchen!")
                    st.rerun()
                else:
                    st.error("Please enter an ingredient name.")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Empty State Handling (Section 25)
    if not ingredients:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px dashed #D3CABA; border-radius: 20px; padding: 3.5rem 2rem; text-align: center; margin: 2rem 0;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🥗</div>
                <h3 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.6rem; color: #2D3425; margin-bottom: 0.5rem;">
                    My Kitchen is empty.
                </h3>
                <p style="color: #68735A; max-width: 450px; margin: 0 auto 1.5rem auto; font-size: 1rem; line-height: 1.5;">
                    Scan your refrigerator shelves to automatically recognize ingredients, or add items manually to start tracking freshness.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1.5, 1])
        with btn_col2:
            if st.button("📷 Scan My Fridge", type="primary", width="stretch"):
                st.session_state.current_page = "scanner"
                st.rerun()
        return

    # Ingredients Grid / List
    for ing in ingredients:
        # Determine badge color based on status
        if ing.freshness_status == "USE TODAY":
            badge_bg = "#FFEBEB"
            badge_color = "#C84B31"
            badge_label = "USE TODAY 🚨"
        elif ing.freshness_status == "USE SOON":
            badge_bg = "#FFF4E5"
            badge_color = "#D97706"
            badge_label = f"USE SOON ({ing.days_remaining}d left) ⚠️"
        else:
            badge_bg = "#EBF3E6"
            badge_color = "#556B2F"
            badge_label = f"FRESH ({ing.days_remaining}d left) 🌿"

        with st.container():
            st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 2px 8px rgba(45,52,37,0.02); display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 600; color: #2D3425;">
                            {ing.name}
                        </div>
                        <span style="background: #F3EEDF; color: #5A644D; font-size: 0.78rem; font-weight: 600; padding: 3px 8px; border-radius: 6px;">
                            {ing.category}
                        </span>
                        <span style="font-size: 0.95rem; color: #4E593D; font-weight: 500;">
                            {ing.quantity} {ing.unit}
                        </span>
                    </div>
                    <div>
                        <span style="background: {badge_bg}; color: {badge_color}; font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 8px;">
                            {badge_label}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Details & Actions expander
            with st.expander(f"⚙️ Manage {ing.name}", expanded=False):
                e1, e2, e3, e4 = st.columns(4)
                with e1:
                    e_name = st.text_input("Name", value=ing.name, key=f"e_name_{ing.id}")
                with e2:
                    e_cat = st.selectbox("Category", VALID_CATEGORIES, index=VALID_CATEGORIES.index(ing.category) if ing.category in VALID_CATEGORIES else 0, key=f"e_cat_{ing.id}")
                with e3:
                    e_qty = st.number_input("Quantity", min_value=0.1, value=float(ing.quantity), step=0.5, key=f"e_qty_{ing.id}")
                with e4:
                    e_unit = st.selectbox("Unit", VALID_UNITS, index=VALID_UNITS.index(ing.unit) if ing.unit in VALID_UNITS else 0, key=f"e_unit_{ing.id}")

                e_shelf = st.slider("Estimated Shelf Life Days", min_value=1, max_value=60, value=int(ing.estimated_shelf_life_days), key=f"e_shelf_{ing.id}")
                e_storage = st.text_input("Storage Advice", value=ing.storage_advice, key=f"e_stor_{ing.id}")

                ac_1, ac_2, _ = st.columns([1, 1, 2])
                with ac_1:
                    if st.button("💾 Update", key=f"btn_upd_{ing.id}", type="primary"):
                        update_ingredient(user.id, ing.id, {
                            "name": e_name,
                            "category": e_cat,
                            "quantity": e_qty,
                            "unit": e_unit,
                            "estimated_shelf_life_days": e_shelf,
                            "storage_advice": e_storage
                        })
                        st.success(f"Updated {e_name}!")
                        st.rerun()
                with ac_2:
                    if st.button("🗑️ Delete", key=f"btn_del_{ing.id}"):
                        delete_ingredient(user.id, ing.id)
                        st.success(f"Deleted {ing.name}!")
                        st.rerun()
