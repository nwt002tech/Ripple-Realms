import streamlit as st
import uuid
import json
from supabase_client import get_supabase_client

supabase = get_supabase_client()

st.set_page_config(page_title="Ripple Realms", layout="centered")
st.title("🌍 Ripple Realms")

# ---------------------------
# Authentication (Demo version – not secure for production)
# ---------------------------
st.subheader("Login / Sign Up")

email = st.text_input("Enter your email")
display_name = st.text_input("Choose a display name")

if st.button("Start Game"):
    if not email or not display_name:
        st.error("Please enter both email and display name.")
    else:
        # Check if user exists
        user_check = supabase.table("users").select("*").eq("email", email).execute()
        if user_check.data:
            user_id = user_check.data[0]['id']
            st.success("Welcome back!")
        else:
            # Register new user
            user_id = str(uuid.uuid4())
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "display_name": display_name
            }).execute()
            st.success("Account created!")

        st.session_state['user_id'] = user_id
        st.session_state['display_name'] = display_name
        st.session_state['signed_in'] = True

# ---------------------------
# Character + Realm Setup
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

            result = supabase.table("realms").insert({
                "id": realm_id,
                "user_id": st.session_state['user_id'],
                "realm_type": realm_type,
                "traits": json.dumps(trait_dict),
                "realm_state": json.dumps({"starting_zone": "village", "npc": []})
            }).execute()

            if result.status_code == 201:
                st.success("🎉 Realm Created!")
                st.json(result.data[0])
            else:
                st.error("Error creating realm. Please try again.")