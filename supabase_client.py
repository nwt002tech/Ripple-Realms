from supabase import create_client, Client

SUPABASE_URL = "https://pyrhbcnriiavwtkedyby.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5cmhiY25yaWlhdnd0a2VkeWJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTAzOTgsImV4cCI6MjA3MDAyNjM5OH0.hzWWsEMe1GDPXRac-so2j9wu0aTHOZloRIg6u8wlggM"

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)