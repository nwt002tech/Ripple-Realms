import os
import json
import uuid

"""
This module provides a simple local persistence layer for the Ripple Realms
game. It emulates a backend by storing users and realms in a JSON file.
If the environment variables `SUPABASE_URL` and `SUPABASE_API_KEY` are
present the module can be extended to interact with a remote Supabase
instance, but in this offline build we rely exclusively on the local
storage.  The JSON file lives in the same directory as this module and
is named `data.json`.

Each user record has the fields:
    id (str)            – unique identifier (UUID)
    email (str)         – user's email address
    display_name (str)  – name displayed in game
    age_mode (str)      – age group chosen by the player (child/teen/adult)

Each realm record has the fields:
    id (str)            – unique identifier (UUID)
    user_id (str)       – id of the owner user
    realm_type (str)    – theme chosen by the player (village/forest/etc.)
    traits (dict)       – a dictionary of trait flags
    realm_state (dict)  – persistent state of the realm (zone, npc list,
                           quests completed, resources etc.)

The helper functions defined below load and write the JSON file on each
operation.  This design is adequate for a single‑user session, but you
could improve it further by caching or adding proper file locking if
multiple sessions need to write concurrently.
"""

# Path to the JSON file used as a data store
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def _load_data():
    """Internal helper to load the data from the JSON file.

    Returns a dictionary with two lists: ``users`` and ``realms``.  If
    the file does not exist it will be created with empty lists.
    """
    if not os.path.exists(DATA_FILE):
        # Initialize the file with empty lists
        data = {"users": [], "realms": []}
        _save_data(data)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted start fresh
            return {"users": [], "realms": []}


def _save_data(data: dict) -> None:
    """Internal helper to persist data to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_user_by_email(email: str):
    """Return a user dictionary matching the email or ``None`` if not found."""
    data = _load_data()
    for user in data.get("users", []):
        if user.get("email") == email:
            return user
    return None


def insert_user(user_id: str, email: str, display_name: str, age_mode: str):
    """Create and persist a new user record.

    Returns the created user dictionary.
    """
    data = _load_data()
    new_user = {
        "id": user_id,
        "email": email,
        "display_name": display_name,
        "age_mode": age_mode,
    }
    data.setdefault("users", []).append(new_user)
    _save_data(data)
    return new_user


def get_realm_by_user(user_id: str):
    """Return the realm belonging to the given user or ``None``."""
    data = _load_data()
    for realm in data.get("realms", []):
        if realm.get("user_id") == user_id:
            return realm
    return None


def insert_realm(realm: dict):
    """Create and persist a new realm record.

    Returns the created realm dictionary.
    """
    data = _load_data()
    data.setdefault("realms", []).append(realm)
    _save_data(data)
    return realm


def update_realm(realm: dict):
    """Update an existing realm record or append it if missing.

    Returns the updated realm dictionary.
    """
    data = _load_data()
    found = False
    for idx, existing in enumerate(data.get("realms", [])):
        if existing.get("id") == realm.get("id"):
            data["realms"][idx] = realm
            found = True
            break
    if not found:
        data.setdefault("realms", []).append(realm)
    _save_data(data)
    return realm