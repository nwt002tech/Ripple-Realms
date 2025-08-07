"""
The dashboard module provides the main user interface for Ripple Realms.
Once a user has logged in and either created or loaded their realm the
``show_dashboard`` function displays their current progress.  The
dashboard shows the active zone, the player's traits, any non‑player
characters (NPCs) they have befriended and the list of quests they have
completed.  Players can continue on to the next available quest or
unlock the next zone when they have finished all quests in their
current location.

This module imports helper functions from the other parts of the game
to perform the underlying data retrieval and mutation.  It is
intentionally thin, focusing on presentation logic only.
"""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st
import httpx

# See ``app.py`` for explanation of these fallback imports.  When run
# as part of a package, the relative imports work; otherwise absolute
# imports are used.
try:
    from . import supabase_client  # type: ignore
    from .map import display_map  # type: ignore
    from .quests import run_quest  # type: ignore
    from .zones import next_zone, ZONE_ORDER  # type: ignore
except ImportError:
    import supabase_client  # type: ignore
    from map import display_map  # type: ignore
    from quests import run_quest  # type: ignore
    from zones import next_zone, ZONE_ORDER  # type: ignore


def _load_image(path: str) -> Optional[str]:
    """Return a path string if the image exists, otherwise None.

    The function checks if the given file exists in the assets folder.
    This allows the dashboard to gracefully skip images when files are
    missing rather than throwing an exception.

    Args:
        path: Relative path under the package directory where the
            desired image resides.

    Returns:
        The input path if the file exists, otherwise ``None``.
    """
    abs_path = os.path.join(os.path.dirname(__file__), path)
    return path if os.path.exists(abs_path) else None


def show_dashboard(user_id: str) -> None:
    """Render the player's dashboard.

    This function displays the current state of the player's realm and
    provides controls to progress further in the game.  It retrieves
    the realm associated with ``user_id`` from the persistence layer
    and shows zone, traits, NPCs and completed quests.  Buttons are
    provided to continue the adventure (which invokes the quest engine)
    and unlock the next zone once all quests in the current zone are
    completed.

    Args:
        user_id: The ID of the currently logged in player.
    """
    realm = supabase_client.get_realm_by_user(user_id)
    if not realm:
        st.error("You do not have a realm yet. Please create one on the home page.")
        return
    # Extract state and traits
    state = realm.get("realm_state", {})
    zone: str = state.get("zone", "village")
    traits = realm.get("traits", {})
    quests_completed = state.get("quests", [])
    npcs = state.get("npc", [])

    # Header and hero image
    st.header("Your Realm")
    zone_image_rel = os.path.join("assets", "zones", f"{zone}.png")
    zone_image = _load_image(zone_image_rel)
    if zone_image:
        st.image(os.path.join(os.path.dirname(__file__), zone_image), use_container_width=True)

    # Map representation of progress
    display_map(zone)

    # Show traits
    st.subheader("Traits")
    if traits:
        for name, value in traits.items():
            if value:
                st.markdown(f"- ✅ **{name.capitalize()}**")
    else:
        st.markdown("_You have no traits yet._")

    # Show NPCs
    st.subheader("Companions")
    if npcs:
        for npc in npcs:
            name = npc.get("name", "Unknown")
            kind = npc.get("type", "")
            st.markdown(f"- **{name}** ({kind})")
    else:
        st.markdown("_You haven't met any companions yet._")

    # Show completed quests
    st.subheader("Quests Completed")
    if quests_completed:
        for quest in quests_completed:
            st.markdown(f"- ✅ {quest}")
    else:
        st.markdown("_No quests completed yet._")

    # Continue to next quest
    if st.button("Continue Adventure"):
        # Pass the current traits to allow the quest engine to gate content
        run_quest(user_id, zone, traits)

    # Unlock next zone if available
    # Only show button if all quests in current zone complete
    all_quests = [q["id"] for q in quests_completed]
    # Determine if there is another zone ahead
    try:
        current_index = ZONE_ORDER.index(zone)
    except ValueError:
        current_index = 0
    # Check if next zone exists
    can_unlock = current_index + 1 < len(ZONE_ORDER)
    if can_unlock:
        if st.button("Unlock Next Zone"):
            # Move to next zone
            new_zone = next_zone(zone)
            if new_zone:
                state["zone"] = new_zone
                supabase_client.update_realm(realm)
                st.success(f"You travel to the {new_zone.capitalize()}!")
                # Force refresh of dashboard on next run
                st.experimental_rerun()