import httpx
import os

SUPABASE_URL = "https://pyrhbcnriiavwtkedyby.supabase.co"
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY") or "YOUR_SERVICE_ROLE_KEY_HERE"

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def get_user_by_email(email):
    url = f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}&select=*"
    response = httpx.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

def insert_user(user_id, email, display_name):
    url = f"{SUPABASE_URL}/rest/v1/users"
    payload = {"id": user_id, "email": email, "display_name": display_name}
    response = httpx.post(url, headers=HEADERS, json=payload)
    return {"debug": {"status": response.status_code, "payload": payload, "raw": response.text}}

def insert_realm(realm_data):
    url = f"{SUPABASE_URL}/rest/v1/realms"
    response = httpx.post(url, headers=HEADERS, json=realm_data)
    debug_info = {"status": response.status_code, "payload": realm_data, "raw": response.text}
    try:
        return {"data": response.json(), "debug": debug_info}
    except:
        return {"error": "Invalid response", "debug": debug_info}