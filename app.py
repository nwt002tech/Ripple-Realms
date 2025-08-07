"""
Main entry point for the Ripple Realms game.

This module provides the user interface for logging in or registering
new players, creating new realms and launching the game dashboard.
It makes use of Streamlit for rendering interactive forms and
maintains player information in session state to persist across
interactions.  The module works in concert with the local
persistence layer implemented in ``supabase_client.py`` and the
presentation functions in ``dashboard.py``.
"""

from __future__ import annotations

import uuid
import streamlit as st

# When executed as a script (e.g. via ``streamlit run app.py``) the module
# is not part of a package so relative imports won't work.  In that
# scenario we fall back to absolute imports which assume all files
# reside in the same directory.  When imported as part of the
# ``ripple_realms_full_game`` package the relative imports are valid.
try:
    from . import supabase_client  # type: ignore
    from .dashboard import show_dashboard  # type: ignore
except ImportError:
    import supabase_client  # type: ignore
    from dashboard import show_dashboard  # type: ignore


def main() -> None:
    """Render the landing page and handle user login/registration.

    The landing page asks for the player's email and display name and
    allows them to select an age mode (child, teen or adult).  When
    the user submits the form a new account is created if one does not
    already exist.  Once signed in the player either creates a new
    realm or proceeds directly to the dashboard.  This implementation
    avoids the deprecated ``st.experimental_rerun`` call by
    conditionally rendering the appropriate view based on session
    variables.
    """
    st.title("🌊 Ripple Realms")
    st.write(
        "Welcome to Ripple Realms, a dynamic story‑driven adventure where every choice "
        "shapes your world. Create your hero, choose your destiny and watch your realm evolve."
    )

    # If already signed in, determine whether to show the dashboard or
    # prompt for realm creation.  This branch will run on every
    # execution once the session_state has been populated by the
    # login/registration flow below.
    if st.session_state.get("signed_in"):
        user_id = st.session_state.get("user_id")
        # If no user ID, reset sign‑in state and return to login
        if not user_id:
            st.session_state["signed_in"] = False
        else:
            # Determine if the user already has a realm
            existing_realm = supabase_client.get_realm_by_user(user_id)
            if existing_realm:
                show_dashboard(user_id)
            else:
                create_realm_form(user_id)
            return

    # Collect player information for a new session.  This form is
    # displayed when the user is not yet signed in.
    st.subheader("Log In or Create an Account")
    email = st.text_input("Email")
    display_name = st.text_input("Display Name")
    age_mode = st.selectbox("Select your age group", ["child", "teen", "adult"])

    if st.button("Start Adventure"):
        if not email or not display_name:
            st.error("Please enter both an email and display name.")
        else:
            # Look up existing user or create a new one
            user = supabase_client.get_user_by_email(email)
            if not user:
                user_id = str(uuid.uuid4())
                supabase_client.insert_user(user_id, email, display_name, age_mode)
                st.success("Account created! Let's set up your realm.")
            else:
                user_id = user["id"]
                display_name = user.get("display_name", display_name)
                age_mode = user.get("age_mode", age_mode)
                st.success("Welcome back! Loading your realm...")
            # Persist login info in session_state
            st.session_state["user_id"] = user_id
            st.session_state["display_name"] = display_name
            st.session_state["age_mode"] = age_mode
            st.session_state["signed_in"] = True
            # Decide what to display next on the same run
            existing_realm = supabase_client.get_realm_by_user(user_id)
            if existing_realm:
                show_dashboard(user_id)
            else:
                create_realm_form(user_id)




def create_realm_form(user_id: str) -> None:
    """Render a form for creating a new realm.

    The player selects a realm type (theme) and chooses up to three
    starting traits.  When submitted a new realm record is created
    and persisted in the local data store.  After creation the
    dashboard is shown.
    """
    st.subheader("Create Your Realm")
    st.write(
        "Choose a theme for your realm and pick three traits that describe your "
        "character.  These initial traits may influence your starting quests."
    )
    realm_type = st.selectbox(
        "Realm Theme",
        ["Nature", "Mystic", "Shadow", "Tech"],
    )
    trait_options = [
        "kind",
        "bold",
        "curious",
        "mysterious",
        "clever",
    ]
    selected_traits = st.multiselect(
        "Select exactly 3 starting traits", trait_options, max_selections=3
    )
    if st.button("Create Realm"):
        if len(selected_traits) != 3:
            st.error("Please select exactly three traits to begin.")
        else:
            # Initialize traits dict with all known traits set to False
            traits = {name: False for name in trait_options + [
                "confident", "hothead", "wise", "humble", "agile", "legendary"
            ]}
            # Mark selected traits as true
            for t in selected_traits:
                traits[t] = True
            realm_id = str(uuid.uuid4())
            realm = {
                "id": realm_id,
                "user_id": user_id,
                "realm_type": realm_type,
                "traits": traits,
                "realm_state": {
                    "zone": "village",
                    "npc": [],
                    "quests": [],
                    "resources": {},
                },
            }
            supabase_client.insert_realm(realm)
            st.success("Your realm has been created! Enjoy your adventure.")
            # Mark the realm as created so the next render knows to show the dashboard
            st.session_state["realm_created"] = True
            # Immediately show the dashboard in the same run.  Avoid
            # deprecated experimental_rerun by directly calling the
            # dashboard function.
            show_dashboard(user_id)


if __name__ == "__main__":
    main()