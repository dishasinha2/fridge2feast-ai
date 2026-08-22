import dotenv
dotenv.load_dotenv()

import streamlit as st
from services.auth_service import initialize_session_state
from components.landing import render_public_landing
from components.auth import render_login_page, render_signup_page
from components.dashboard import render_authenticated_dashboard

# Page Configuration
st.set_page_config(
    page_title="Fridge2Feast AI - Turn What's Left Into What's Next",
    page_icon=":material/restaurant:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Premium emerald-and-gold visual system. `st.html` keeps this style block out of page flow.
st.html("""
<style>
  :root { --bg-1:#0B2B26; --bg-2:#0F3D36; --card:rgba(255,255,255,.055); --line:rgba(255,255,255,.12); --ink:#F4EFE6; --soft:#B9C7C0; --gold:#E8B94E; --coral:#E8734E; }
  .stApp { background:radial-gradient(1100px 500px at 10% -10%,rgba(232,185,78,.14),transparent 60%),radial-gradient(900px 500px at 100% 0%,rgba(232,115,78,.1),transparent 55%),linear-gradient(180deg,var(--bg-1),var(--bg-2) 60%,#0A2320); color:var(--ink); }
  .block-container { max-width:1180px; padding-top:2rem; padding-bottom:3rem; }
  h1,h2,h3 { font-family:Fraunces,"Playfair Display",Georgia,serif !important; color:var(--ink) !important; letter-spacing:.01em; }
  p,span,label { color:var(--ink); }
  .brand-lockup { color:var(--ink); font-family:Fraunces,"Playfair Display",Georgia,serif; font-size:1.55rem; font-weight:700; letter-spacing:-.035em; }
  .brand-lockup span { color:var(--gold); } .brand-lockup small { color:var(--soft); font-family:Inter,sans-serif; font-size:.62rem; letter-spacing:.1em; margin-left:.25rem; }
  .workspace-greeting { color:var(--soft) !important; font-size:.82rem; margin:.25rem 0 1rem; }
  .auth-brand { max-width:560px; text-align:center; margin:2.4rem auto 1.6rem; }
  .auth-brand p { color:var(--gold) !important; font-size:.76rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin:0 0 .5rem; }
  .auth-brand h1 { font-size:2.35rem; line-height:1.1; margin:0 0 .7rem; }
  .auth-brand span { color:var(--soft) !important; font-size:1rem; }
  .stButton>button, .stDownloadButton>button { background:linear-gradient(135deg,var(--gold),var(--coral)) !important; color:#241505 !important; border:0 !important; border-radius:12px !important; font-weight:700 !important; box-shadow:0 6px 16px rgba(232,115,78,.25); }
  .stButton>button:hover { transform:translateY(-2px); box-shadow:0 10px 22px rgba(232,115,78,.4); }
  .stTextInput input, .stSelectbox select, .stNumberInput input, textarea { background:rgba(255,255,255,.06) !important; color:var(--ink) !important; border-color:var(--line) !important; }
  [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMetric"] { border-color:var(--line) !important; background:var(--card); border-radius:16px; backdrop-filter:blur(14px); }
  div[data-testid='stSegmentedControl'] { margin:1.1rem 0 1.7rem; }
  div[data-testid='stSegmentedControl'] button { color:var(--soft) !important; }
  div[data-testid='stSegmentedControl'] button[aria-pressed='true'] { color:var(--gold) !important; background:rgba(232,185,78,.14) !important; }
  div[style*="background: #1e293b"], div[style*="background:#1e293b"] { background:var(--card) !important; border-color:var(--line) !important; backdrop-filter:blur(14px); }
</style>
""")

# Initialize Session State with strict user isolation (no default sample data dumping)
initialize_session_state(force_reset=False)

# Router Logic
auth_view = st.session_state.get("auth_view", "public_landing")
is_authenticated = st.session_state.get("authenticated", False)

if is_authenticated:
    render_authenticated_dashboard()
elif auth_view == "login":
    render_login_page()
elif auth_view == "signup":
    render_signup_page()
else:
    render_public_landing()
