import streamlit as st

from services.auth_service import authenticate_user, login_user, signup_user
from utils.validation import validate_email, validate_password


def _brand_header(eyebrow: str, title: str, description: str) -> None:
    st.markdown(f"<div class='auth-brand'><p>{eyebrow}</p><h1>{title}</h1><span>{description}</span></div>", unsafe_allow_html=True)


def render_login_page() -> None:
    _brand_header("Welcome back", "Your kitchen, beautifully in sync.", "Log in to see your inventory, saved feasts and personalised ideas.")
    _, center, _ = st.columns([1, 1.35, 1])
    with center:
        with st.container(border=True):
            st.subheader("Log in", anchor=False)
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email address", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submit = st.form_submit_button("Log in", type="primary", width="stretch")
            if submit:
                if not validate_email(email) or not password:
                    st.error("Enter your email address and password.")
                else:
                    authenticated, name = authenticate_user(email, password)
                    if authenticated:
                        login_user(email=email.strip().lower(), name=name)
                        st.rerun()
                    else:
                        st.error("Email or password is incorrect.")
            st.caption("New to Fridge2Feast?")
            if st.button("Create an account", width="stretch", key="goto_signup"):
                st.session_state.auth_view = "signup"
                st.rerun()
            if st.button("Back to home", width="stretch", key="login_back"):
                st.session_state.auth_view = "public_landing"
                st.rerun()


def render_signup_page() -> None:
    _brand_header("Start fresh", "Make every ingredient count.", "Create your private kitchen workspace in under a minute.")
    _, center, _ = st.columns([1, 1.35, 1])
    with center:
        with st.container(border=True):
            st.subheader("Create your account", anchor=False)
            with st.form("signup_form", clear_on_submit=False):
                name = st.text_input("Your name", placeholder="Chef Alex", key="signup_name")
                email = st.text_input("Email address", placeholder="you@example.com", key="signup_email")
                password = st.text_input("Password", type="password", help="At least 8 characters, with a letter and a number.", key="signup_password")
                confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")
                terms = st.checkbox("I agree to the Terms of Use and Privacy Policy.")
                submit = st.form_submit_button("Create my kitchen", type="primary", width="stretch")
            if submit:
                if not name.strip():
                    st.error("Please tell us your name.")
                elif not validate_email(email):
                    st.error("Enter a valid email address.")
                elif not validate_password(password):
                    st.error("Use at least 8 characters, including a letter and a number.")
                elif password != confirm_password:
                    st.error("The passwords don't match.")
                elif not terms:
                    st.error("Please accept the Terms of Use and Privacy Policy.")
                else:
                    created, message = signup_user(name, email, password)
                    if created:
                        st.rerun()
                    else:
                        st.error("We couldn't create that account. Please try a different email or log in.")
            st.caption("Already have an account?")
            if st.button("Log in", width="stretch", key="goto_login"):
                st.session_state.auth_view = "login"
                st.rerun()
            if st.button("Back to home", width="stretch", key="signup_back"):
                st.session_state.auth_view = "public_landing"
                st.rerun()
