"""Authentication UI Component for Fridge2Feast AI."""
import streamlit as st
from services.auth_service import login_user, signup_user

def render_auth():
    """Render the login and signup forms in a floating card matching Reference Image 3."""
    is_signup = st.session_state.get("auth_view", "login") == "signup"

    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        # Card container
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E5DECE; border-radius: 20px; padding: 2rem; box-shadow: 0 8px 24px rgba(45,52,37,0.06); text-align: center; margin-bottom: 1.5rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: #556B2F; border-radius: 14px; margin-bottom: 0.75rem; color: #FFFFFF; font-size: 26px;">
                    🍃
                </div>
                <div style="font-family: serif; font-size: 1.1rem; color: #556B2F; font-weight: 600; margin-bottom: 0.25rem;">
                    Fridge2Feast AI
                </div>
                <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.8rem; color: #2D3425; margin-bottom: 1.5rem; font-style: italic;">
                    {title}
                </h2>
            </div>
        """.format(title="Join Fridge2Feast" if is_signup else "Welcome Back"), unsafe_allow_html=True)

        if is_signup:
            with st.form("signup_form", clear_on_submit=False):
                name = st.text_input("Full Name", placeholder="Your Name")
                email = st.text_input("Email Address", placeholder="name@example.com")
                password = st.text_input("Password", type="password", placeholder="At least 8 chars with letter & number")
                submit = st.form_submit_button("Create Account →", width="stretch", type="primary")

                if submit:
                    user, err = signup_user(email, name, password)
                    if err:
                        st.error(err)
                    elif user:
                        st.session_state.authenticated_user = user
                        st.session_state.current_page = "dashboard"
                        st.success("Account created successfully!")
                        st.rerun()

            st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
            if st.button("Already have an account? Log In", width="stretch"):
                st.session_state.auth_view = "login"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="name@example.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Log In →", width="stretch", type="primary")

                if submit:
                    user, err = login_user(email, password)
                    if err:
                        st.error(err)
                    elif user:
                        st.session_state.authenticated_user = user
                        st.session_state.current_page = "dashboard"
                        st.success("Logged in successfully!")
                        st.rerun()

            st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
            if st.button("Don't have an account? Sign Up", width="stretch"):
                st.session_state.auth_view = "signup"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("🏠 Back to Home", width="stretch"):
            st.session_state.current_page = "landing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
