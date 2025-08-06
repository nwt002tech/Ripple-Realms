import streamlit as st
import httpx
from supabase_client import SUPABASE_URL, HEADERS
from quests import run_quest
from zones import unlock_next_zone


def fetch_realm_by_user(user_id):
    url = f"{SUPABASE_URL}/rest/v1/realms?user_id=eq.{user_id}&select=*"
    response = httpx.get(url, headers=HEADERS)
    return response.json()[0] if response.status_code == 200 else None


def show_dashboard(user_id):
    st.header("🏰 Your Realm")

    realm = fetch_realm_by_user(user_id)
    if not realm:
        st.error("No realm found.")
        return

    zone = realm["realm_state"].get("zone", "unknown").capitalize()
    st.subheader(f"📍 Current Zone: {zone}")
    st.caption("Complete quests to unlock the next zone!")

    st.markdown("### 💠 Traits")
    for trait, value in realm["traits"].items():
        if value:
            st.markdown(f"✅ {trait.capitalize()}")

    st.markdown("### 👤 NPCs")
    for npc in realm["realm_state"].get("npc", []):
        st.markdown(f"- {npc['name']} ({npc['type']})")

    st.markdown("### 🗺️ Completed Quests")
    completed = realm["realm_state"].get("quests", [])
    if completed:
        for q in completed:
            st.markdown(f"- ✅ {q}")
    else:
        st.markdown("_None yet_")

    if st.button("➡️ Continue Adventure"):
        run_quest(user_id, zone)

    if st.button("🗺️ Unlock Next Zone"):
        unlock_next_zone(user_id)
        st.session_state["realm_shown"] = False  # safe trigger for refresh
        st.success("Zone unlocked! Click any button to refresh view.")