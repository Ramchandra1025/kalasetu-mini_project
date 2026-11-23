from datetime import datetime, timedelta, timezone

from backend.database import get_supabase
from backend.config import Config
from backend.utils.security import generate_otp, hash_otp


def create_otp(account_id: str):
    supabase = get_supabase()

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=Config.OTP_EXPIRY_MINUTES
    )

    otp = generate_otp()

    otp_hash = hash_otp(otp)

    # Invalidate previous OTPs
    supabase \
        .table("email_verification_otps") \
        .update({"used": True}) \
        .eq("account_id", account_id) \
        .eq("used", False) \
        .execute()

    result = (
        supabase
        .table("email_verification_otps")
        .insert({
            "account_id": account_id,
            "otp_hash": otp_hash,
            "expires_at": expires_at.isoformat(),
            "attempts": 0,
            "used": False
        })
        .execute()
    )

    if not result.data:
        raise RuntimeError("Failed to create OTP")

    return otp


def get_latest_otp(account_id: str):

    supabase = get_supabase()

    result = (
        supabase
        .table("email_verification_otps")
        .select("*")
        .eq("account_id", account_id)
        .eq("used", False)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]