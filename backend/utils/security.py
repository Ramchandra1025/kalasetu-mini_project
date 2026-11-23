import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from backend.config import Config


password_hasher = PasswordHasher()


# =========================================================
# PASSWORD
# =========================================================

def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


# =========================================================
# OTP
# =========================================================

def generate_otp() -> str:
    """
    Generates a cryptographically secure 6-digit OTP.
    """
    return str(secrets.randbelow(900000) + 100000)


def hash_otp(otp: str) -> str:
    """
    HMAC-based OTP hash.

    We don't store the actual OTP in Supabase.
    """
    return hmac.new(
        Config.SECRET_KEY.encode("utf-8"),
        otp.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def verify_otp(otp: str, stored_hash: str) -> bool:
    calculated_hash = hash_otp(otp)

    return hmac.compare_digest(
        calculated_hash,
        stored_hash
    )