import httpx
import os

# Replace with your Supabase credentials
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
    if response.status_code == 200:
        return response.json()
    else:
        return []


def insert_user(user_id, email, display_name):
    url = f"{SUPABASE_URL}/rest/v1/users"
    payload = {
        "id": user_id,
        "email": email,
        "display_name": display_name
    }
    response = httpx.post(url, headers=HEADERS, json=payload)
    return response.json()


def insert_realm(realm_data):
    url = f"{SUPABASE_URL}/rest/v1/realms"
    response = httpx.post(url, headers=HEADERS, json=realm_data)
    return response.json()