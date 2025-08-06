import httpx
from supabase_client import SUPABASE_URL, HEADERS

ZONE_ORDER = ["village", "forest", "temple", "tower", "ruins"]

def unlock_next_zone(user_id):
    url_get = f"{SUPABASE_URL}/rest/v1/realms?user_id=eq.{user_id}&select=id,realm_state"
    res = httpx.get(url_get, headers=HEADERS)
    realm = res.json()[0]
    realm_id = realm["id"]
    current_zone = realm["realm_state"].get("zone", "village")
    next_index = ZONE_ORDER.index(current_zone) + 1
    if next_index < len(ZONE_ORDER):
        realm["realm_state"]["zone"] = ZONE_ORDER[next_index]
        patch_url = f"{SUPABASE_URL}/rest/v1/realms?id=eq.{realm_id}"
        httpx.patch(patch_url, headers=HEADERS, json={"realm_state": realm["realm_state"]})