"""Interactive Step-by-Step Cooking Mode Component."""
import streamlit as st
from services.recipe_service import record_cooking_history

def render_cooking():
    """Render the focused step-by-step cooking experience with timer and audio guidance."""
    user = st.session_state.authenticated_user
    recipe = st.session_state.get("cooking_recipe", None)

    if not user or not recipe:
        st.info("No recipe is currently loaded for cooking.")
        if st.button("Browse Recipes"):
            st.session_state.current_page = "recipes"
            st.rerun()
        return

    # Track current cooking step in session state
    if "current_step_idx" not in st.session_state:
        st.session_state.current_step_idx = 0

    step_idx = st.session_state.current_step_idx
    total_steps = len(recipe.instructions)

    st.markdown(f"""
        <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <span style="background: #EBF3E6; color: #556B2F; font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 8px;">
                    COOKING MODE 🍳
                </span>
                <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.2rem; color: #2D3425; margin: 0.3rem 0 0 0; font-weight: 700;">
                    {recipe.title}
                </h1>
            </div>
            <div style="font-size: 0.95rem; color: #7B856E;">
                ⏱️ {recipe.cooking_time_minutes} mins total
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Top Overview Container: Ingredients quick checklist
    with st.expander("📝 Recipe Ingredients Reference", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**From Kitchen:**")
            for item in recipe.available_ingredients:
                if isinstance(item, dict):
                    st.write(f"• {item.get('name')}: {item.get('quantity', '')} {item.get('unit', '')}")
                else:
                    st.write(f"• {item}")
        with c2:
            st.markdown("**Additional Staples:**")
            for item in recipe.additional_ingredients:
                if isinstance(item, dict):
                    st.write(f"• {item.get('name')}: {item.get('quantity', '')} {item.get('unit', '')}")
                else:
                    st.write(f"• {item}")

    # Progress bar for steps
    progress_val = min(1.0, (step_idx + 1) / max(1, total_steps))
    st.progress(progress_val)
    st.caption(f"Step {step_idx + 1} of {total_steps}")

    current_instruction = recipe.instructions[step_idx] if step_idx < total_steps else "All steps complete!"

    # Active Step Display Box
    st.markdown(f"""
        <div style="background: #FFFFFF; border: 2px solid #556B2F; border-radius: 20px; padding: 2.5rem 2rem; margin: 1.5rem 0; box-shadow: 0 8px 24px rgba(85,107,47,0.08); text-align: center;">
            <div style="font-size: 0.95rem; font-weight: 700; color: #556B2F; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 1rem;">
                STEP {step_idx + 1}
            </div>
            <div style="font-size: 1.4rem; color: #2D3425; line-height: 1.6; font-weight: 500; max-width: 700px; margin: 0 auto;">
                {current_instruction}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Next step sneak peek
    if step_idx + 1 < total_steps:
        st.markdown(f"""
            <div style="background: #F8F6EF; border-radius: 12px; padding: 0.85rem 1.25rem; margin-bottom: 1.5rem; color: #7B856E; font-size: 0.9rem;">
                <strong>Up Next:</strong> {recipe.instructions[step_idx + 1]}
            </div>
        """, unsafe_allow_html=True)

    # Timer Widget
    t_col1, t_col2 = st.columns([2, 1])
    with t_col1:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 16px; padding: 1rem 1.25rem;">
                <strong style="color: #2D3425;">⏱️ Kitchen Timer Guide</strong>
                <div style="color: #68735A; font-size: 0.85rem;">Keep track of boiling, simmering, or sautéing duration.</div>
            </div>
        """, unsafe_allow_html=True)
    with t_col2:
        timer_min = st.number_input("Timer Minutes", min_value=1, max_value=120, value=5, step=1)

    # Navigation Buttons
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    n_col1, n_col2, n_col3 = st.columns([1, 1.5, 1])

    with n_col1:
        if st.button("◀ Previous Step", disabled=(step_idx == 0), use_container_width=True):
            st.session_state.current_step_idx = max(0, step_idx - 1)
            st.rerun()

    with n_col2:
        if step_idx + 1 < total_steps:
            if st.button("Next Step ▶", type="primary", use_container_width=True):
                st.session_state.current_step_idx = step_idx + 1
                st.rerun()
        else:
            if st.button("🎉 Finish & Log to History", type="primary", use_container_width=True):
                record_cooking_history(
                    user_id=user.id,
                    recipe_title=recipe.title,
                    cuisine=recipe.cuisine,
                    servings=recipe.servings,
                    notes=f"Cooked in {recipe.cooking_time_minutes} minutes with {recipe.waste_saved_score}% waste rescue score.",
                    rating=5
                )
                st.session_state.cooking_recipe = None
                st.session_state.current_step_idx = 0
                st.session_state.current_page = "dashboard"
                st.success("Congratulations! Meal completed and logged to your cooking history.")
                st.rerun()

    with n_col3:
        if st.button("Exit Cooking", use_container_width=True):
            st.session_state.cooking_recipe = None
            st.session_state.current_step_idx = 0
            st.session_state.current_page = "recipes"
            st.rerun()
