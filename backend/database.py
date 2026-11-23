
from supabase import create_client
from backend.config import Config


def get_supabase():
    """
    Creates a fresh Supabase client.
    """
    return create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_SERVICE_ROLE_KEY
    )
