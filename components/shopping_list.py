import streamlit as st
from utils.calculations import calculate_total_missing_cost
from utils.exports import export_shopping_list_csv, export_shopping_list_txt, export_shopping_list_markdown

def render_shopping_list_component():
    """
    Renders the Smart Shopping List with INR pricing & exports.
    """
    recipe = st.session_state.get("shopping_recipe") or st.session_state.get("selected_recipe")

    st.markdown("<h2 style='color: #ffffff; font-weight: 900;'>🛒 Smart Shopping List</h2>", unsafe_allow_html=True)

    if not recipe:
        st.info("No recipe selected for shopping list. Select a recipe from the Recipe Dashboard!")
        if st.button("🍽️ View Recipes", type="primary"):
            st.session_state.active_tab = "Recipe Dashboard"
            st.rerun()
        return

    missing_ingredients = recipe.get("ingredients_missing", [])
    recipe_title = recipe.get("title", "Selected Recipe")

    st.markdown(f"<p style='color: #94a3b8;'>Target Recipe: <strong style='color: #10b981;'>{recipe_title}</strong></p>", unsafe_allow_html=True)

    if not missing_ingredients:
        st.balloons()
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 16px; padding: 25px; text-align: center; margin-top: 15px;">
                <h3 style="color: #34d399; font-weight: 800; margin-bottom: 8px;">🎉 Zero Missing Ingredients!</h3>
                <p style="color: #cbd5e1; margin: 0;">You already have 100% of the required ingredients in your fridge. No shopping trip required!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Total Shopping Cost Banner
    total_cost = calculate_total_missing_cost(missing_ingredients)

    st.markdown(
        f"""
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <span style="font-size: 12px; color: #94a3b8; font-weight: 700;">TOTAL ESTIMATED SHOPPING COST</span><br>
                <span style="font-size: 28px; font-weight: 900; color: #10b981;">₹{total_cost:.2f} INR</span>
            </div>
            <div>
                <span style="background: #334155; color: #f8fafc; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 800;">
                    {len(missing_ingredients)} Items to Buy
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Interactive Checklist
    st.markdown("#### 📝 Items Checklist")
    for idx, item in enumerate(missing_ingredients):
        name = item.get("name", "Ingredient")
        qty = item.get("estimated_quantity", "1 item")
        price = float(item.get("estimated_price_inr", 0.0))

        st.checkbox(
            f"**{name}** — {qty} (Est. ₹{price:.2f} INR)",
            key=f"shop_chk_{idx}",
            value=False
        )

    st.markdown("<hr style='border-color: #334155; margin: 25px 0;'>", unsafe_allow_html=True)

    # Export Buttons
    st.markdown("#### 📥 Export & Share Shopping List")
    col1, col2, col3 = st.columns(3)

    csv_data = export_shopping_list_csv(missing_ingredients, recipe_title)
    txt_data = export_shopping_list_txt(missing_ingredients, recipe_title)
    md_data = export_shopping_list_markdown(missing_ingredients, recipe_title)

    with col1:
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name="fridge2feast_shopping_list.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="📝 Download TXT",
            data=txt_data,
            file_name="fridge2feast_shopping_list.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col3:
        st.download_button(
            label="📊 Download Markdown",
            data=md_data,
            file_name="fridge2feast_shopping_list.md",
            mime="text/markdown",
            use_container_width=True
        )
