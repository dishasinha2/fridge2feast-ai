"""Authenticated kitchen analytics rendered from SQLite-backed user data."""
import streamlit as st
import plotly.express as px

from services.kitchen_service import get_user_ingredients
from services.recipe_service import get_cooking_history, get_saved_recipes
from utils.pandas_utils import inventory_to_freshness_df, kitchen_insight_frames


def load_analytics_data(user_id: int):
    """Load and transform analytics data for one authenticated user."""
    ingredients = get_user_ingredients(user_id)
    inventory_df = inventory_to_freshness_df(ingredients)
    insights = kitchen_insight_frames(inventory_df)
    saved_recipes = get_saved_recipes(user_id)
    cooking_history = get_cooking_history(user_id)
    return {
        "inventory": inventory_df,
        "insights": insights,
        "saved_recipes": saved_recipes,
        "cooking_history": cooking_history,
    }


def render_analytics_component():
    """Render real, user-scoped kitchen impact analytics."""
    user = st.session_state.get("authenticated_user")
    if not user:
        st.info("Log in to view your kitchen analytics.")
        return

    data = load_analytics_data(user.id)
    inventory_df = data["inventory"]
    insights = data["insights"]
    saved_recipes = data["saved_recipes"]
    cooking_history = data["cooking_history"]

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="color: #2D3425; font-family: 'Playfair Display', Georgia, serif; font-size: 28px; margin: 0 0 6px 0;">
                Your Kitchen Impact
            </h1>
            <p style="color: #5A644D; font-size: 15px; margin: 0;">
                Track your real ingredients, freshness, recipes, and cooking activity.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if inventory_df.empty and not saved_recipes and not cooking_history:
        st.info("Not enough data yet. Scan your fridge, add ingredients, or cook a recipe to build your kitchen insights.")
        return

    use_soon_count = int((inventory_df["days_remaining"] <= 2).sum()) if not inventory_df.empty else 0
    kcol1, kcol2, kcol3, kcol4 = st.columns(4)
    with kcol1:
        st.metric("Pantry Items Tracked", len(inventory_df))
    with kcol2:
        st.metric("Use Soon", use_soon_count)
    with kcol3:
        st.metric("Meals Cooked", len(cooking_history))
    with kcol4:
        st.metric("Saved Recipes", len(saved_recipes))

    if inventory_df.empty:
        st.info("Add or scan ingredients to see freshness and category charts.")
        return

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("### Freshness distribution")
        freshness_df = insights["freshness"]
        figure = px.bar(
            freshness_df,
            x="Freshness",
            y="Ingredients",
            color="Freshness",
            color_discrete_map={
                "USE TODAY": "#A6382A",
                "USE SOON": "#E8935A",
                "FRESH": "#6B7A45",
            },
        )
        figure.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(figure, width="stretch")

    with chart_col2:
        st.markdown("### Ingredient categories")
        category_df = insights["categories"]
        figure = px.pie(
            category_df,
            names="Category",
            values="Ingredients",
            color_discrete_sequence=["#6B7A45", "#E8935A", "#A6382A", "#8B9670", "#C9B98A"],
            hole=0.45,
        )
        figure.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(figure, width="stretch")

    if not cooking_history:
        st.info("No cooking history yet. Complete a recipe to build your cooking activity.")
