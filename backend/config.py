
import os
from pathlib import Path
from dotenv import load_dotenv

# Always load E:\kalasetu\backend\.env relative to this file.
BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=False)


class Config:
    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # EmailJS
    EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID")
    EMAILJS_TEMPLATE_ID = os.getenv("EMAILJS_TEMPLATE_ID")
    EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY")
    EMAILJS_PRIVATE_KEY = os.getenv("EMAILJS_PRIVATE_KEY")

    # OTP
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
    OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    OTP_RESEND_COOLDOWN_SECONDS = int(
        os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "60")
    )

    # Session
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    )
    DEBUG = os.getenv("FLASK_DEBUG", "false").strip().lower() in {
        "1", "true", "yes", "on"
    }


if not Config.SECRET_KEY:
    raise RuntimeError("FLASK_SECRET_KEY is missing")

if not Config.SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not Config.SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is missing")
