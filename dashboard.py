import streamlit as st
from PIL import Image
from pathlib import Path
import random

def show_dashboard(user_id):
    st.subheader("🌍 Your Realm")

    realm_type = random.choice(["Tech", "Nature", "Mystic"])
    zone = st.session_state.get("zone", "village")
    st.session_state["zone"] = zone

    zone_image = Path(f"assets/zones/{zone}.png")
    if zone_image.exists():
        st.image(zone_image, use_container_width=True)

    st.write(f"🧭 Current Zone: **{zone.capitalize()}**")

    st.markdown("### 🤖 You encounter an NPC!")
    col1, col2 = st.columns(2)
    with col1:
        st.image("assets/characters/watcher_orb.png", caption="Watcher Orb", width=200)
    with col2:
        st.image("assets/characters/tree_sprite.png", caption="Tree Sprite", width=200)

    if st.button("🗺️ Unlock Next Zone"):
        next_zone = "forest" if zone == "village" else "village"
        st.session_state["zone"] = next_zone
        st.success("Zone unlocked!")