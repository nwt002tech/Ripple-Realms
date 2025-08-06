import streamlit as st
import httpx
from supabase_client import SUPABASE_URL, HEADERS

def fetch_realm_by_user(user_id):
    url = f"{SUPABASE_URL}/rest/v1/realms?user_id=eq.{user_id}&select=*"
    response = httpx.get(url, headers=HEADERS)
    try:
        return response.json()[0]
    except:
        return None

def show_dashboard(user_id):
    st.header("🏰 Your Realm")

    realm = fetch_realm_by_user(user_id)

    if not realm:
        st.error("No realm found for this user.")
        return

    # Display zone
    zone = realm["realm_state"].get("starting_zone", "unknown").capitalize()
    st.subheader(f"📍 Current Zone: {zone}")

    # Traits
    st.markdown("### 💠 Traits")
    for trait, value in realm["traits"].items():
        if value:
            st.markdown(f"✅ {trait.capitalize()}")

    # NPCs
    st.markdown("### 👤 NPCs in Your Realm")
    npcs = realm["realm_state"].get("npc", [])
    if not npcs:
        st.markdown("_No NPCs present yet_")
    else:
        for npc in npcs:
            st.markdown(f"- {npc.get('name', 'Unknown')} ({npc.get('type', '')})")

    # Continue
    if st.button("➡️ Continue Adventure"):
        from quests import run_first_quest
        run_first_quest(user_id)