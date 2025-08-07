import streamlit as st

try:
    from .zones import ZONE_ORDER  # type: ignore
except ImportError:
    from zones import ZONE_ORDER  # type: ignore

# Emoji representations for each zone.  These help players quickly
# identify their progress on the map.
ZONE_EMOJIS = {
    "village": "🏡",
    "forest": "🌲",
    "temple": "⛩️",
    "tower": "🗼",
    "ruins": "🏚️",
}


def display_map(current_zone: str) -> None:
    """Render a simple map showing the player's progress.

    The map lists all zones in order with an emoji and colour-coded
    indicator.  Zones already visited (including the current one) are
    marked with a green dot, while those ahead remain grey.
    """
    st.markdown("### 🗺️ World Map")
    reached = True
    for zone in ZONE_ORDER:
        if zone == current_zone:
            indicator = "🟢"
            reached = False
        elif reached:
            indicator = "🟢"
        else:
            indicator = "⚪"
        emoji = ZONE_EMOJIS.get(zone, "⬜")
        st.markdown(f"{indicator} {emoji} **{zone.capitalize()}**")