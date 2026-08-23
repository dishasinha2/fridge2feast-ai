"""Landing Page Component for Fridge2Feast AI."""
import streamlit as st

def render_landing():
    """Render the premium zero-waste landing page."""
    st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem 1rem 1rem;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: #556B2F; border-radius: 16px; margin-bottom: 1rem; color: #FFFFFF; font-size: 32px;">
                🍃
            </div>
            <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.8rem; color: #2D3425; margin-bottom: 0.25rem; font-weight: 700; letter-spacing: -0.5px;">
                Fridge2Feast AI
            </h1>
            <p style="font-size: 1.25rem; color: #C84B31; font-weight: 600; margin-bottom: 1.5rem; font-style: italic;">
                "Turn What's Left Into What's Next"
            </p>
            <p style="max-width: 650px; margin: 0 auto 2rem auto; font-size: 1.05rem; color: #5A644D; line-height: 1.6;">
                An intelligent zero-waste kitchen assistant powered by Gemini Vision. Simply scan your refrigerator, automatically track ingredient shelf-life, and generate personalized chef-quality meals tailored to what needs rescuing first.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("🚀 Get Started / Sign Up", use_container_width=True, type="primary"):
                st.session_state.auth_view = "signup"
                st.session_state.current_page = "auth"
                st.rerun()
        with c_b:
            if st.button("🔑 Log In", use_container_width=True):
                st.session_state.auth_view = "login"
                st.session_state.current_page = "auth"
                st.rerun()

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 3 Pillars
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E5DECE; border-radius: 16px; padding: 1.5rem; height: 100%; box-shadow: 0 4px 12px rgba(45,52,37,0.03);">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">📷</div>
                <h3 style="font-family: serif; color: #2D3425; font-size: 1.2rem; margin-bottom: 0.5rem;">Gemini Refrigerator Vision</h3>
                <p style="color: #68735A; font-size: 0.92rem; line-height: 1.5;">
                    Point your camera or upload a fridge photo. Multimodal AI identifies ingredients, estimates quantities, and suggests proper storage.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E5DECE; border-radius: 16px; padding: 1.5rem; height: 100%; box-shadow: 0 4px 12px rgba(45,52,37,0.03);">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">⏳</div>
                <h3 style="font-family: serif; color: #2D3425; font-size: 1.2rem; margin-bottom: 0.5rem;">Deterministic Freshness Engine</h3>
                <p style="color: #68735A; font-size: 0.92rem; line-height: 1.5;">
                    Intelligent countdown tracking flags expiring items with <em>USE TODAY</em> and <em>USE SOON</em> alerts so nothing goes to waste.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E5DECE; border-radius: 16px; padding: 1.5rem; height: 100%; box-shadow: 0 4px 12px rgba(45,52,37,0.03);">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🍳</div>
                <h3 style="font-family: serif; color: #2D3425; font-size: 1.2rem; margin-bottom: 0.5rem;">Personalized Zero-Waste Recipes</h3>
                <p style="color: #68735A; font-size: 0.92rem; line-height: 1.5;">
                    Generate step-by-step recipes prioritized around your expiring pantry items, customized for your cuisine, spice, and dietary goals.
                </p>
            </div>
        """, unsafe_allow_html=True)
