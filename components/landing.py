import streamlit as st


def _go(view: str) -> None:
    st.session_state.auth_view = view
    st.rerun()


def render_public_landing() -> None:
    left, right = st.columns([4, 1], vertical_alignment="center")
    with left:
        st.markdown("<div class='brand-lockup'>Fridge<span>2</span>Feast <small>AI</small></div>", unsafe_allow_html=True)
    with right:
        if st.button("Log in", width="stretch", key="landing_login"):
            _go("login")

    hero, preview = st.columns([1.2, 0.8], vertical_alignment="center")
    with hero:
        st.badge("A calmer way to cook", icon=":material/auto_awesome:", color="green")
        st.title("Turn what you have into something worth serving.")
        st.write("Fridge2Feast reads your kitchen, protects ingredients that need attention, and turns them into meals you’ll actually want to make.")
        with st.container(horizontal=True):
            if st.button("Create your kitchen", type="primary", key="landing_signup"):
                _go("signup")
            if st.button("I already have an account", key="landing_login_hero"):
                _go("login")
        st.caption("Private by design · No guest mode · Your kitchen stays yours")
    with preview:
        with st.container(border=True):
            st.caption("Tonight’s kitchen brief")
            st.metric("Ingredients ready to use", "12", "+3 this week")
            st.badge("2 items to use soon", icon=":material/timer:", color="orange")
            st.write("Scan your fridge and get thoughtful recipe ideas from the food already at home.")

    st.space("medium")
    st.subheader("Everything you need to waste less and cook better", anchor=False)
    columns = st.columns(3)
    features = [
        (":material/photo_camera:", "Scan your fridge", "Upload a photo and review detected ingredients before anything is used."),
        (":material/menu_book:", "Cook with confidence", "Get personalised recipes, shopping gaps and guided cooking steps."),
        (":material/eco:", "Stay ahead of waste", "See what to use next, create rescue plans and track your impact."),
    ]
    for column, (icon, title, description) in zip(columns, features):
        with column:
            with st.container(border=True):
                st.markdown(icon)
                st.subheader(title, anchor=False)
                st.caption(description)

    st.space("medium")
    st.caption("Fridge2Feast AI · Your intelligent, zero-waste kitchen companion")
