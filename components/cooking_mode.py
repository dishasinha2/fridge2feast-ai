import time
import streamlit as st

def render_cooking_mode_component():
    """
    Renders the interactive Step-by-Step Cooking Mode.
    """
    recipe = st.session_state.get("cooking_recipe") or st.session_state.get("selected_recipe")

    if not recipe:
        st.info("No recipe selected for cooking. Please select a recipe from the Dashboard!")
        if st.button("🍽️ View Recipes", type="primary"):
            st.session_state.active_tab = "Recipe Dashboard"
            st.rerun()
        return

    steps = recipe.get("preparation_steps", [])
    if not steps:
        st.warning("No preparation steps found for this recipe.")
        return

    current_step = st.session_state.get("cooking_step", 0)
    total_steps = len(steps)

    st.markdown("<h2 style='color: #ffffff; font-weight: 900;'>👨‍🍳 Interactive Cooking Mode</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #94a3b8;'>Cooking: <strong style='color: #10b981;'>{recipe.get('title')}</strong></p>", unsafe_allow_html=True)

    # Progress bar
    progress_val = min(1.0, (current_step + 1) / total_steps)
    st.progress(progress_val)
    st.markdown(
        f"<div style='text-align: right; font-size: 13px; color: #94a3b8; font-weight: 700; margin-bottom: 20px;'>"
        f"Step {min(current_step + 1, total_steps)} of {total_steps}"
        f"</div>",
        unsafe_allow_html=True
    )

    if current_step < total_steps:
        # Step Card Display
        step_text = steps[current_step]
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 2px solid #10b981; border-radius: 20px; padding: 30px; margin-bottom: 25px;">
                <span style="background: #10b981; color: #022c22; font-weight: 900; padding: 4px 12px; border-radius: 12px; font-size: 13px;">
                    STEP {current_step + 1}
                </span>
                <h3 style="color: #ffffff; margin-top: 15px; font-size: 22px; font-weight: 800; line-height: 1.5;">
                    {step_text}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Controls: Previous / Next Step
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if current_step > 0:
                if st.button("← Previous Step", key="cook_prev_step", use_container_width=True):
                    st.session_state.cooking_step = current_step - 1
                    st.rerun()

        with col3:
            if current_step < total_steps - 1:
                if st.button("Next Step →", key="cook_next_step", type="primary", use_container_width=True):
                    st.session_state.cooking_step = current_step + 1
                    st.rerun()
            else:
                if st.button("🎉 Complete Feast!", key="cook_finish_btn", type="primary", use_container_width=True):
                    st.session_state.cooking_step = total_steps
                    st.rerun()

    else:
        # Feast Completed Screen
        st.balloons()
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #064e3b, #022c22); border: 2px solid #10b981; border-radius: 24px; padding: 30px; text-align: center; margin-bottom: 25px;">
                <div style="font-size: 40px; margin-bottom: 10px;">🎉 🍽️</div>
                <h2 style="color: #ffffff; font-weight: 900; font-size: 28px;">Feast Completed!</h2>
                <p style="color: #a7f3d0; font-size: 15px; max-width: 500px; margin: 8px auto 15px auto;">
                    Congratulations! You've cooked <strong>{recipe.get('title')}</strong> while saving ingredients from going to waste.
                </p>
                <div style="display: inline-block; background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; padding: 8px 18px; border-radius: 14px; color: #34d399; font-weight: 800; font-size: 13px;">
                    ♻️ Waste Reduction Score: {recipe.get('ingredient_utilization_percentage', 85):.0f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Quick Post-Cooking Feedback Form (Section 11)
        st.markdown("### 💬 Quick Kitchen Feedback")
        st.caption("Your feedback helps AI Kitchen Decision Agent personalize future seasonings, portions, and recipes silently.")

        with st.form("cooking_feedback_form"):
            fb_col1, fb_col2 = st.columns(2)
            with fb_col1:
                rating = st.select_slider(
                    "How did it turn out?",
                    options=["Needs Work 😕", "Okay 😐", "Good 🙂", "Delicious! 😋", "Perfection! 🌟"],
                    value="Delicious! 😋"
                )
                what_worked = st.multiselect(
                    "What worked?",
                    ["Flavor balance", "Prep time speed", "Ingredient rescue", "Easy instructions", "Portion size"],
                    default=["Flavor balance", "Ingredient rescue"]
                )
            with fb_col2:
                what_change = st.multiselect(
                    "What would you change?",
                    ["More spice", "Less spice", "More sauce/gravy", "Quicker technique", "Fewer dishes", "Different protein"]
                )
                chef_note = st.text_input("Any extra notes?", placeholder="e.g. Loved the crispy texture, added a pinch of extra cumin")

            submit_feedback = st.form_submit_button("💾 Save Feedback & Update Taste Profile", type="primary", use_container_width=True)
            if submit_feedback:
                # Silently update taste profile in session state
                taste = st.session_state.get("taste_profile", {})
                taste["recipes_cooked_count"] = taste.get("recipes_cooked_count", 0) + 1
                cuisine = recipe.get("cuisine")
                if cuisine and cuisine not in taste.get("favorite_cuisines", []):
                    taste.setdefault("favorite_cuisines", []).append(cuisine)
                
                # Update spice preferences if mentioned
                if "More spice" in what_change:
                    taste["spice_preference"] = "High / Extra Spicy"
                elif "Less spice" in what_change:
                    taste["spice_preference"] = "Mild / Gentle"
                
                st.session_state.taste_profile = taste
                
                # Log feedback history
                feedback_entry = {
                    "recipe_title": recipe.get("title"),
                    "rating": rating,
                    "what_worked": what_worked,
                    "what_change": what_change,
                    "chef_note": chef_note,
                }
                st.session_state.setdefault("cooking_feedback_history", []).append(feedback_entry)
                st.success("✅ Feedback saved! Taste profile updated.")

        st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🍳 Cook Another Recipe", use_container_width=True):
                st.session_state.cooking_step = 0
                st.session_state.active_tab = "Recipe Dashboard"
                st.rerun()
        with c2:
            if st.button("📊 View Zero-Waste Analytics", use_container_width=True):
                st.session_state.active_tab = "Analytics"
                st.rerun()
