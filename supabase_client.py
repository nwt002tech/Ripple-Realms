import httpx
import os

SUPABASE_URL = "https://pyrhbcnriiavwtkedyby.supabase.co"
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5cmhiY25yaWlhdnd0a2VkeWJ5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQ1MDM5OCwiZXhwIjoyMDcwMDI2Mzk4fQ.t3rT6XJse6mqHiXldtbBqm8lq6omf4dDjIpYzzikuhs"

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}


def get_user_by_email(email):
    url = f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}&select=*"
    response = httpx.get(url, headers=HEADERS)
    try:
        return response.json()
    except Exception:
        print("❌ Failed to parse user query response:", response.text)
        return []


def insert_user(user_id, email, display_name):
    url = f"{SUPABASE_URL}/rest/v1/users"
    payload = {
        "id": user_id,
        "email": email,
        "display_name": display_name
    }
    response = httpx.post(url, headers=HEADERS, json=payload)

    # Debugging info
    print("🔄 Insert User Response Code:", response.status_code)
    print("🔍 Response Text:", response.text)

    try:
        return response.json()
    except Exception:
        return {"error": response.text}


def insert_realm(realm_data):
    url = f"{SUPABASE_URL}/rest/v1/realms"
    response = httpx.post(url, headers=HEADERS, json=realm_data)

    debug_info = {
        "status": response.status_code,
        "raw": response.text
    }

    try:
        data = response.json()
        return {"data": data, "debug": debug_info}
    except Exception:
        return {"error": response.text, "debug": debug_info}