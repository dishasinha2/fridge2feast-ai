import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pandas_utils import ingredients_to_df, get_category_distribution

def render_analytics_component():
    """
    Renders 'Your Kitchen Impact' dashboard.
    Shows real food-saving metrics, spending avoided, and environmental reduction.
    """
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; margin: 0 0 6px 0;">
                Your Kitchen Impact
            </h1>
            <p style="color: #cbd5e1; font-size: 15px; margin: 0;">
                Track how home cooking and zero-waste habits help your household and the planet.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    ingredients = st.session_state.get("detected_ingredients", [])
    df = ingredients_to_df(ingredients)

    saved_recipes = st.session_state.get("saved_recipes", [])
    generated_recipes = st.session_state.get("generated_recipes", [])

    # Top Impact Metrics
    kcol1, kcol2, kcol3, kcol4 = st.columns(4)
    with kcol1:
        st.metric("Pantry Items Tracked", len(df))
    with kcol2:
        st.metric("Meals Designed", len(generated_recipes))
    with kcol3:
        avg_util = None
        if generated_recipes:
            avg_util = sum(r["ingredient_utilization_percentage"] for r in generated_recipes) / len(generated_recipes)
        st.metric("Avg Fridge Utilization", f"{avg_util:.0f}%" if avg_util is not None else "No recipe data")
    with kcol4:
        st.metric("Saved Recipes", len(saved_recipes))

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Plotly Charts Section
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("<h3 style='color: #ffffff; font-size: 17px; font-weight: 700; margin-bottom: 8px;'>Inventory Categories</h3>", unsafe_allow_html=True)
        if not df.empty:
            cat_df = get_category_distribution(df)
            if not cat_df.empty:
                fig1 = px.pie(
                    cat_df,
                    names="Category",
                    values="Count",
                    color_discrete_sequence=["#10b981", "#38bdf8", "#fbbf24", "#a78bfa", "#f43f5e", "#64748b"],
                    hole=0.45
                )
                fig1.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#f8fafc", family="sans-serif"),
                    margin=dict(t=10, b=10, l=10, r=10),
                    showlegend=True
                )
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.write("No active categories found.")
        else:
            st.info("Add ingredients to see your pantry category distribution.")

    with chart_col2:
        st.markdown("<h3 style='color: #ffffff; font-size: 17px; font-weight: 700; margin-bottom: 8px;'>Kitchen Utilization Trend</h3>", unsafe_allow_html=True)
        if avg_util is not None:
            utilization_df = pd.DataFrame({"Recipe": [r["title"] for r in generated_recipes], "Utilization (%)": [r["ingredient_utilization_percentage"] for r in generated_recipes]})
            fig2 = px.bar(utilization_df, x="Recipe", y="Utilization (%)", color="Utilization (%)", color_continuous_scale=[[0, "#334155"], [0.5, "#059669"], [1, "#10b981"]])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc", family="sans-serif"), margin=dict(t=10, b=10, l=10, r=10), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Generate recipes to see utilization data.")

    st.info("Environmental impact estimates will appear after verified waste-reduction events are recorded.")
