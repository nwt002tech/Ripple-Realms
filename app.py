import streamlit as st
from dashboard import show_dashboard
from supabase_client import init_supabase

st.set_page_config(page_title="Ripple Realms", layout="wide")

if "user_id" not in st.session_state:
    st.session_state["user_id"] = "demo-user"
    st.session_state["display_name"] = "Adventurer"
    st.session_state["email"] = "demo@example.com"

init_supabase()

st.title("🌊 Ripple Realms")

if "realm_shown" not in st.session_state:
    st.session_state["realm_shown"] = False

if not st.session_state["realm_shown"]:
    if st.button("🚀 Start Game"):
        st.session_state["realm_shown"] = True
        st.rerun()
else:
    show_dashboard(st.session_state["user_id"])