"""Saved Recipes Component for Fridge2Feast AI."""
import streamlit as st
from services.recipe_service import get_saved_recipes, unsave_recipe

def render_saved():
    """Render the user's saved recipes collection."""
    user = st.session_state.authenticated_user
    if not user:
        st.session_state.current_page = "landing"
        st.rerun()

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.4rem; color: #2D3425; margin-bottom: 0.2rem; font-style: italic;">
                📖 Saved Recipes & Cookbook
            </h1>
            <p style="font-size: 1.05rem; color: #5A644D; margin: 0;">
                Your favorite zero-waste creations saved for quick kitchen reference.
            </p>
        </div>
    """, unsafe_allow_html=True)

    saved_list = get_saved_recipes(user.id)

    if not saved_list:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px dashed #D3CABA; border-radius: 20px; padding: 3.5rem 2rem; text-align: center; margin: 2rem 0;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📚</div>
                <h3 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.5rem; color: #2D3425; margin-bottom: 0.5rem;">
                    No saved recipes yet.
                </h3>
                <p style="color: #68735A; max-width: 450px; margin: 0 auto 1.5rem auto;">
                    Generate your first zero-waste recipe and save it to build your personal smart cookbook.
                </p>
            </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            if st.button("🍳 Generate Recipes", type="primary", use_container_width=True):
                st.session_state.current_page = "recipes"
                st.rerun()
        return

    for recipe in saved_list:
        with st.container():
            st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(45,52,37,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="background: #F3EEDF; color: #5A644D; font-size: 0.8rem; font-weight: 600; padding: 3px 8px; border-radius: 6px;">
                                {recipe.cuisine} • {recipe.meal_type}
                            </span>
                            <h3 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem; color: #2D3425; margin: 0.4rem 0;">
                                {recipe.title}
                            </h3>
                            <p style="color: #5A644D; font-size: 0.95rem; line-height: 1.5; margin: 0 0 0.5rem 0;">
                                {recipe.description}
                            </p>
                            <div style="font-size: 0.85rem; color: #7B856E;">
                                ⏱️ {recipe.cooking_time_minutes} mins | 👥 {recipe.servings} servings | 🌶️ {recipe.spice_level} | ♻️ {recipe.waste_saved_score}% waste rescued
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            with c1:
                if st.button("🍳 Cook Step-by-Step", key=f"cook_{recipe.id}", type="primary", use_container_width=True):
                    st.session_state.cooking_recipe = recipe
                    st.session_state.current_page = "cooking"
                    st.rerun()
            with c2:
                if st.button("📖 View Full Recipe", key=f"view_{recipe.id}", use_container_width=True):
                    st.session_state.active_recipe = recipe
                    st.session_state.current_page = "recipes"
                    st.rerun()
            with c3:
                if st.button("🗑️ Remove", key=f"unsave_{recipe.id}", use_container_width=True):
                    unsave_recipe(user.id, recipe.id)
                    st.success(f"Removed '{recipe.title}' from saved recipes.")
                    st.rerun()
