import streamlit as st
import pandas as pd
from utils.pandas_utils import (
    ingredients_to_df,
    df_to_ingredients,
    calculate_fridge_potential,
    get_use_first_ingredients,
)

def render_inventory_component():
    """
    Renders the customer's kitchen inventory and freshness guidance.
    """
    st.markdown("<h2 style='color: #ffffff; font-weight: 900;'>My Kitchen</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>"
        "Review detected ingredients, freshness windows, and what to use first."
        "</p>",
        unsafe_allow_html=True
    )

    ingredients = st.session_state.get("detected_ingredients", [])

    if not ingredients:
        st.info("Your fridge is empty. Scan your fridge to add confirmed ingredients.")
        if st.button("📸 Go to Camera Scanner", type="primary"):
            st.session_state.active_tab = "Scanner"
            st.rerun()
        return

    # Convert list of dicts to enriched Pandas DataFrame
    df = ingredients_to_df(ingredients)

    # Top KPI Metrics & Fridge Potential Bar
    potential = calculate_fridge_potential(df)
    use_first_list = get_use_first_ingredients(ingredients)
    urgent_count = sum(1 for i in use_first_list if i.get("urgency_level") == "HIGH")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Items", len(df))
    with kpi2:
        st.metric("🚨 High Urgency Items", urgent_count)
    with kpi3:
        cat_count = df["Category"].nunique() if "Category" in df.columns else 0
        st.metric("Categories", cat_count)
    with kpi4:
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 10px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; font-weight: 700;">FRIDGE POTENTIAL</span><br>
                <span style="font-size: 18px; font-weight: 900; color: {potential['color']};">{potential['tier']} ({potential['score']}%)</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border-color: #334155; margin: 15px 0;'>", unsafe_allow_html=True)

    # 🚨 USE FIRST PRIORITY SECTION
    st.markdown("<h3 style='color: #ffffff; font-weight: 800; font-size: 18px; margin-bottom: 12px;'>🚨 USE FIRST</h3>", unsafe_allow_html=True)
    urgent_display = [i for i in use_first_list if i.get("urgency_level") == "HIGH"]
    items_to_show = urgent_display if urgent_display else use_first_list[:2]

    if items_to_show:
        u_cols = st.columns(min(len(items_to_show), 3))
        for idx, item in enumerate(items_to_show[:3]):
            name = item.get("name", "Ingredient")
            qty = item.get("estimated_quantity", "1 item")
            urgency = item.get("urgency_level", "HIGH")
            waste_risk = item.get("waste_risk_score", 87)
            window = item.get("estimated_use_window", "1–2 days")
            reason = item.get("reasoning", "Highly perishable and currently not included in a planned meal.")
            
            badge_color = "#ef4444" if urgency == "HIGH" else "#fbbf24"
            badge_bg = "#ef444422" if urgency == "HIGH" else "#f59e0b22"

            with u_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-top: 4px solid {badge_color}; border-radius: 14px; padding: 14px; min-height: 185px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 800; color: #ffffff; font-size: 15px;">🥬 {name}</span>
                                <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}44; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 6px;">
                                    {urgency} PRIORITY
                                </span>
                            </div>
                            <span style="color: #94a3b8; font-size: 12px; font-weight: 600;">Qty: {qty}</span>
                            <p style="color: #cbd5e1; font-size: 12px; margin: 6px 0 6px 0; line-height: 1.3;">
                                "{reason}"
                            </p>
                        </div>
                        <div style="font-size: 11px; color: #94a3b8;">
                            <div>⏱️ Est. freshness: <strong>{window}</strong></div>
                            <div>⚠️ Waste risk: <strong style="color: {badge_color};">{waste_risk}/100</strong></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"🍳 Cook {name} First", key=f"inv_cook_{name}_{idx}", use_container_width=True):
                    st.session_state.meal_context["craving"] = f"Using {name}"
                    st.session_state.active_tab = "Kitchen Agent"
                    st.rerun()

    st.markdown("<hr style='border-color: #334155; margin: 15px 0;'>", unsafe_allow_html=True)

    # Category Filter
    all_categories = ["All Categories"] + sorted(df["Category"].unique().tolist())
    selected_category = st.selectbox("Filter Category", all_categories, key="inv_cat_filter")

    filtered_df = df if selected_category == "All Categories" else df[df["Category"] == selected_category]

    # Display & Edit Pandas DataFrame using Streamlit's native data_editor
    st.markdown("#### Review your ingredients")
    st.caption("Edit names, quantities, categories, or freshness details before cooking.")

    display_cols = [c for c in filtered_df.columns if c != "id"]
    
    edited_df = st.data_editor(
        filtered_df[display_cols],
        column_config={
            "Include": st.column_config.CheckboxColumn("Include", help="Include in recipe generation", default=True),
            "Ingredient": st.column_config.TextColumn("Ingredient Name", required=True),
            "Category": st.column_config.SelectboxColumn("Category", options=[
                "Vegetables", "Fruits", "Dairy & Eggs", "Proteins & Meat",
                "Grains & Pasta", "Condiments & Sauces", "Pantry & Spices", "Beverages"
            ]),
            "Quantity": st.column_config.TextColumn("Estimated Quantity"),
            "Urgency": st.column_config.SelectboxColumn("Urgency Level", options=["HIGH", "MEDIUM", "LOW"]),
            "Waste Risk": st.column_config.ProgressColumn("Waste Risk", min_value=0, max_value=100, format="%d"),
            "Est. Use-By": st.column_config.TextColumn("Est. Use Window", disabled=True),
            "Confidence": st.column_config.NumberColumn("AI Conf.", format="%.2f", disabled=True),
            "Confidence Label": st.column_config.TextColumn("Conf. Tag", disabled=True),
        },
        hide_index=True,
        num_rows="dynamic",
        key="inventory_data_editor"
    )

    # Save edits back to session state & track human-in-the-loop audit
    if st.button("Save inventory updates", type="primary"):
        updated_ingredients = df_to_ingredients(edited_df)
        
        # Track human-in-the-loop diff
        old_count = len(ingredients)
        new_count = len(updated_ingredients)
        hitl = st.session_state.get("hitl_vision_audit", {
            "initial_detected_count": old_count, "confirmed_count": old_count, "edited_count": 0, "removed_count": 0, "added_count": 0
        })
        
        if new_count < old_count:
            hitl["removed_count"] += (old_count - new_count)
        elif new_count > old_count:
            hitl["added_count"] += (new_count - old_count)
        else:
            hitl["edited_count"] += 1
            
        hitl["confirmed_count"] = new_count
        st.session_state.hitl_vision_audit = hitl
        st.session_state.detected_ingredients = updated_ingredients
        
        st.success("Human verification saved! Freshness intelligence and audit metrics updated.")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Add Item Form
    with st.expander("➕ Add Single Ingredient Manually"):
        with st.form("add_item_form"):
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                new_name = st.text_input("Ingredient Name", placeholder="e.g. Spinach, Paneer")
            with ac2:
                new_cat = st.selectbox("Category", [
                    "Vegetables", "Fruits", "Dairy & Eggs", "Proteins & Meat",
                    "Grains & Pasta", "Condiments & Sauces", "Pantry & Spices", "Beverages"
                ])
            with ac3:
                new_qty = st.text_input("Quantity", placeholder="e.g. 1 bunch, 200g")

            add_submit = st.form_submit_button("Add Ingredient")
            if add_submit and new_name.strip():
                new_item = {
                    "id": f"manual-{len(ingredients)+1}",
                    "name": new_name.strip(),
                    "category": new_cat,
                    "estimated_quantity": new_qty.strip() or "1 item",
                    "confidence": 1.0,
                    "confidence_label": "High",
                    "included": True,
                }
                st.session_state.detected_ingredients.append(new_item)
                hitl = st.session_state.get("hitl_vision_audit", {})
                hitl["added_count"] = hitl.get("added_count", 0) + 1
                hitl["confirmed_count"] = hitl.get("confirmed_count", 0) + 1
                st.session_state.hitl_vision_audit = hitl
                st.success(f"Added {new_name} to inventory!")
                st.rerun()

    # Call to action to proceed to Kitchen Agent
    st.markdown("<hr style='border-color: #334155; margin: 25px 0;'>", unsafe_allow_html=True)
    if st.button("🤖 Proceed to AI Kitchen Decision Agent →", type="primary", use_container_width=True):
        st.session_state.active_tab = "Kitchen Agent"
        st.rerun()
