import streamlit as st
import httpx
from supabase_client import SUPABASE_URL, HEADERS

QUESTS = {
    "village": {
        "title": "The Flickering Orb",
        "description": "A glowing orb floats over your village...",
        "choices": {
            "Investigate it": {"npc": {"name": "Watcher Orb", "type": "mystic"}, "reward": "Gained a mysterious NPC"},
            "Speak to it": {"trait": "clever", "reward": "You feel smarter"},
            "Ignore it": {"reward": "Nothing happened"}
        }
    },
    "forest": {
        "title": "Whispers in the Trees",
        "description": "The trees seem to whisper secrets. What do you do?",
        "choices": {
            "Follow the whispers": {"trait": "curious", "reward": "Your curiosity grows"},
            "Climb a tree": {"npc": {"name": "Tree Sprite", "type": "guide"}, "reward": "Gained a sprite friend"},
            "Run away": {"reward": "You escaped safely"}
        }
    }
}

def run_quest(user_id, zone):
    quest = QUESTS.get(zone.lower())
    if not quest:
        st.info("No quests available here yet.")
        return

    st.subheader(f"🧭 Quest: {quest['title']}")
    st.markdown(quest['description'])

    choice = st.radio("What do you do?", list(quest["choices"].keys()))

    if st.button("Confirm Choice"):
        url_get = f"{SUPABASE_URL}/rest/v1/realms?user_id=eq.{user_id}&select=*"
        res = httpx.get(url_get, headers=HEADERS)
        realm = res.json()[0]
        realm_id = realm["id"]
        state = realm["realm_state"]
        traits = realm["traits"]

        outcome = quest["choices"][choice]

        if "npc" in outcome:
            state["npc"].append(outcome["npc"])
        if "trait" in outcome:
            traits[outcome["trait"]] = True
        state["quests"].append(quest["title"])

        # Save updates
        patch_url = f"{SUPABASE_URL}/rest/v1/realms?id=eq.{realm_id}"
        payload = {"realm_state": state, "traits": traits}
        httpx.patch(patch_url, headers=HEADERS, json=payload)

        st.success(outcome["reward"])