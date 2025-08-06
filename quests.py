import streamlit as st
import httpx
from supabase_client import SUPABASE_URL, HEADERS

def update_realm_state(user_id, update_data):
    # Fetch realm ID
    url_get = f"{SUPABASE_URL}/rest/v1/realms?user_id=eq.{user_id}&select=id,realm_state,traits"
    res = httpx.get(url_get, headers=HEADERS)
    realm = res.json()[0]
    realm_id = realm['id']
    current_state = realm['realm_state']
    current_traits = realm['traits']

    # Apply updates
    new_state = current_state.copy()
    new_traits = current_traits.copy()

    if update_data.get("npc"):
        new_state.setdefault("npc", []).append(update_data["npc"])

    if update_data.get("trait"):
        new_traits[update_data["trait"]] = True

    # Save
    url_patch = f"{SUPABASE_URL}/rest/v1/realms?id=eq.{realm_id}"
    patch_body = {
        "realm_state": new_state,
        "traits": new_traits
    }

    res = httpx.patch(url_patch, headers=HEADERS, json=patch_body)
    return res.status_code == 204


def run_first_quest(user_id):
    st.header("✨ Quest: The Flickering Orb")

    st.markdown("""
    A glowing orb appears in the sky above your realm.  
    It pulses gently and seems to watch you. What will you do?
    """)

    choice = st.radio("Choose your action:", [
        "🔍 Investigate the orb",
        "💬 Try to speak to it",
        "🚶 Walk away"
    ])

    if st.button("Confirm Choice"):
        result = True  # default
        if choice == "🔍 Investigate the orb":
            result = update_realm_state(user_id, {
                "npc": {"name": "Watcher Orb", "type": "mystic"}
            })
            st.success("You investigate the orb. It merges into the realm, silently watching.")
        elif choice == "💬 Try to speak to it":
            result = update_realm_state(user_id, {
                "trait": "clever"
            })
            st.success("You speak to the orb. It whispers riddles into your mind. You feel... smarter.")
        elif choice == "🚶 Walk away":
            st.info("You walk away. The orb vanishes.")

        if result:
            st.balloons()
            st.success("Your realm has been updated.")
        else:
            st.error("Failed to update your realm.")