import streamlit as st
import uuid
import json
from supabase_client import get_user_by_email, insert_user, insert_realm

st.set_page_config(page_title="Ripple Realms", layout="centered")
st.title("🌍 Ripple Realms")

# ---------------------------
# Authentication (demo login)
# ---------------------------
st.subheader("Login or Sign Up")

email = st.text_input("Enter your email")
display_name = st.text_input("Choose a display name")

if st.button("Start Game"):
    if not email or not display_name:
        st.error("Please enter both email and display name.")
    else:
        existing = get_user_by_email(email)
        if existing:
            user_id = existing[0]['id']
            st.success(f"Welcome back, {display_name}!")
        else:
            user_id = str(uuid.uuid4())
            result = insert_user(user_id, email, display_name)
            st.success("Account created!")

        st.session_state['user_id'] = user_id
        st.session_state['display_name'] = display_name
        st.session_state['signed_in'] = True

# ---------------------------
# Realm Creation
# ---------------------------
if st.session_state.get('signed_in'):
    st.header("🧙 Choose Your Realm")

    realm_type = st.selectbox("Realm Type", ["Forest", "Tech", "Shadow", "Fantasy"])
    traits = st.multiselect("Pick 3 traits", ["Kind", "Bold", "Curious", "Mysterious", "Clever"])

    if st.button("Create Realm"):
        if len(traits) != 3:
            st.error("Please select exactly 3 traits.")
        else:
            trait_dict = {trait.lower(): True for trait in traits}
            realm_id = str(uuid.uuid4())

            realm_data = {
    "id": realm_id,
    "user_id": st.session_state['user_id'],
    "realm_type": realm_type,
    "traits": trait_dict,  # native dict
    "realm_state": {"starting_zone": "village", "npc": []}  # native dict
}

            result = insert_realm(realm_data)

            if isinstance(result, list) and result:
                st.success("🎉 Realm created successfully!")
                st.json(result[0])
            else:
                st.error("Something went wrong creating the realm.")