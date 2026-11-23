from datetime import datetime, timezone

from flask import (
    Blueprint,
    request,
    jsonify,
    session
)

from backend.database import get_supabase
from backend.config import Config

from backend.utils.security import (
    hash_password,
    verify_password,
    verify_otp
)

from backend.services.otp_service import (
    create_otp,
    get_latest_otp
)

from backend.services.email_service import (
    send_verification_email
)

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# =========================================================
# HELPERS
# =========================================================

def clean_email(email):
    return email.strip().lower()


def valid_email(email):

    return (
        "@" in email
        and "." in email.split("@")[-1]
        and len(email) <= 255
    )


def get_account_by_email(email):

    supabase = get_supabase()

    result = (
        supabase
        .table("accounts")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]


# =========================================================
# REGISTER
# =========================================================

@auth_bp.post("/register")
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = clean_email(str(data.get("email", "")))
    password = str(data.get("password", ""))
    account_type = str(
        data.get("account_type", "buyer")
    ).lower().strip()

    preferred_language = str(
        data.get("preferred_language", "English")
    ).strip()

    # -----------------------------
    # Validation
    # -----------------------------

    if not name:
        return jsonify({
            "success": False,
            "message": "Name is required."
        }), 400

    if not valid_email(email):
        return jsonify({
            "success": False,
            "message": "Enter a valid email address."
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters."
        }), 400

    if account_type not in ["buyer", "artisan"]:
        return jsonify({
            "success": False,
            "message": "Invalid account type."
        }), 400

    # -----------------------------
    # Check existing account
    # -----------------------------

    existing = get_account_by_email(email)

    if existing:

        if existing.get("email_verified"):

            return jsonify({
                "success": False,
                "message": "An account with this email already exists."
            }), 409

        # Existing but unverified:
        # resend OTP instead of creating duplicate account.

        account_id = existing["id"]

        otp = create_otp(account_id)

        email_sent = send_verification_email(
            existing["name"],
            email,
            otp
        )

        if not email_sent:
            return jsonify({
                "success": False,
                "message": "Account exists, but verification email could not be sent."
            }), 500

        return jsonify({
            "success": True,
            "requires_verification": True,
            "email": email,
            "message": "Verification OTP sent."
        })

    # -----------------------------
    # Create account
    # -----------------------------

    supabase = get_supabase()

    password_hash = hash_password(password)

    account_data = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "account_type": account_type,
        "preferred_language": preferred_language,
        "email_verified": False
    }

    result = (
        supabase
        .table("accounts")
        .insert(account_data)
        .execute()
    )

    if not result.data:

        return jsonify({
            "success": False,
            "message": "Failed to create account."
        }), 500

    account = result.data[0]

    account_id = account["id"]

    # -----------------------------
    # Generate OTP
    # -----------------------------

    try:

        otp = create_otp(account_id)

    except Exception as error:

        print("OTP creation error:", error)

        # Remove account if OTP setup failed
        supabase \
            .table("accounts") \
            .delete() \
            .eq("id", account_id) \
            .execute()

        return jsonify({
            "success": False,
            "message": "Unable to initialize email verification."
        }), 500

    # -----------------------------
    # Send email
    # -----------------------------

    email_sent = send_verification_email(
        name,
        email,
        otp
    )

    if not email_sent:

        supabase \
            .table("accounts") \
            .delete() \
            .eq("id", account_id) \
            .execute()

        return jsonify({
            "success": False,
            "message": "Account could not be created because verification email failed."
        }), 500

    return jsonify({
        "success": True,
        "requires_verification": True,
        "email": email,
        "message": "Account created. Verification OTP sent to your email."
    }), 201


# =========================================================
# VERIFY OTP
# =========================================================

@auth_bp.post("/verify-otp")
def verify_email():

    data = request.get_json(silent=True) or {}

    email = clean_email(str(data.get("email", "")))
    otp = str(data.get("otp", "")).strip()

    if not valid_email(email):

        return jsonify({
            "success": False,
            "message": "Invalid email."
        }), 400

    if not otp.isdigit() or len(otp) != 6:

        return jsonify({
            "success": False,
            "message": "Enter a valid 6-digit OTP."
        }), 400

    account = get_account_by_email(email)

    if not account:

        return jsonify({
            "success": False,
            "message": "Account not found."
        }), 404

    if account["email_verified"]:

        return jsonify({
            "success": True,
            "message": "Email is already verified."
        })

    otp_record = get_latest_otp(account["id"])

    if not otp_record:

        return jsonify({
            "success": False,
            "message": "OTP not found. Please request a new OTP."
        }), 400

    # -----------------------------
    # Attempts
    # -----------------------------

    attempts = otp_record.get("attempts", 0)

    if attempts >= Config.OTP_MAX_ATTEMPTS:

        return jsonify({
            "success": False,
            "message": "Too many incorrect attempts. Request a new OTP."
        }), 429

    # -----------------------------
    # Expiration
    # -----------------------------

    expires_at = datetime.fromisoformat(
        otp_record["expires_at"].replace("Z", "+00:00")
    )

    if datetime.now(timezone.utc) > expires_at:

        return jsonify({
            "success": False,
            "message": "OTP has expired. Request a new OTP."
        }), 400

    # -----------------------------
    # Verify
    # -----------------------------

    if not verify_otp(
        otp,
        otp_record["otp_hash"]
    ):

        supabase = get_supabase()

        (
            supabase
            .table("email_verification_otps")
            .update({
                "attempts": attempts + 1
            })
            .eq("id", otp_record["id"])
            .execute()
        )

        remaining = Config.OTP_MAX_ATTEMPTS - attempts - 1

        return jsonify({
            "success": False,
            "message": f"Incorrect OTP. {remaining} attempts remaining."
        }), 400

    # -----------------------------
    # Verify account
    # -----------------------------

    supabase = get_supabase()

    (
        supabase
        .table("accounts")
        .update({
            "email_verified": True
        })
        .eq("id", account["id"])
        .execute()
    )

    # Mark OTP used

    (
        supabase
        .table("email_verification_otps")
        .update({
            "used": True
        })
        .eq("id", otp_record["id"])
        .execute()
    )

    # -----------------------------
    # Create artisan profile
    # -----------------------------

    if account["account_type"] == "artisan":

        artisan_data = {
            "id": account["id"],
            "full_name": account["name"],
            "preferred_language": account.get(
                "preferred_language",
                "en"
            ),
            "onboarding_completed": False
        }

        try:

            (
                supabase
                .table("artisans")
                .insert(artisan_data)
                .execute()
            )

        except Exception as error:

            print(
                "Artisan profile creation warning:",
                error
            )

    return jsonify({
        "success": True,
        "message": "Email verified successfully.",
        "account_type": account["account_type"]
    })


# =========================================================
# RESEND OTP
# =========================================================

@auth_bp.post("/resend-otp")
def resend_otp():

    data = request.get_json(silent=True) or {}

    email = clean_email(str(data.get("email", "")))

    if not valid_email(email):

        return jsonify({
            "success": False,
            "message": "Invalid email."
        }), 400

    account = get_account_by_email(email)

    if not account:

        return jsonify({
            "success": False,
            "message": "Unable to process this request."
        }), 404

    if account["email_verified"]:

        return jsonify({
            "success": False,
            "message": "Email is already verified."
        }), 400

    # Check latest OTP cooldown

    latest = get_latest_otp(account["id"])

    if latest:

        created_at = datetime.fromisoformat(
            latest["created_at"].replace("Z", "+00:00")
        )

        elapsed = (
            datetime.now(timezone.utc) - created_at
        ).total_seconds()

        if elapsed < Config.OTP_RESEND_COOLDOWN_SECONDS:

            remaining = int(
                Config.OTP_RESEND_COOLDOWN_SECONDS - elapsed
            )

            return jsonify({
                "success": False,
                "message": f"Please wait {remaining} seconds before requesting another OTP."
            }), 429

    otp = create_otp(account["id"])

    sent = send_verification_email(
        account["name"],
        account["email"],
        otp
    )

    if not sent:

        return jsonify({
            "success": False,
            "message": "Unable to send verification email."
        }), 500

    return jsonify({
        "success": True,
        "message": "A new OTP has been sent."
    })


# =========================================================
# LOGIN
# =========================================================

@auth_bp.post("/login")
def login():

    data = request.get_json(silent=True) or {}

    email = clean_email(str(data.get("email", "")))
    password = str(data.get("password", ""))

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    account = get_account_by_email(email)

    if not account:

        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    if not verify_password(
        password,
        account["password_hash"]
    ):

        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    if not account["email_verified"]:

        return jsonify({
            "success": False,
            "requires_verification": True,
            "email": email,
            "message": "Please verify your email before logging in."
        }), 403

    # Flask signed session

    session.clear()

    session["account_id"] = account["id"]
    session["account_type"] = account["account_type"]
    session["email"] = account["email"]

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "account": {
            "id": account["id"],
            "name": account["name"],
            "email": account["email"],
            "account_type": account["account_type"],
            "preferred_language": account["preferred_language"]
        }
    })


# =========================================================
# CURRENT USER
# =========================================================

@auth_bp.get("/me")
def current_user():

    account_id = session.get("account_id")

    if not account_id:

        return jsonify({
            "authenticated": False
        })

    supabase = get_supabase()

    result = (
        supabase
        .table("accounts")
        .select(
            "id,name,email,account_type,"
            "preferred_language,email_verified,"
            "created_at"
        )
        .eq("id", account_id)
        .limit(1)
        .execute()
    )

    if not result.data:

        session.clear()

        return jsonify({
            "authenticated": False
        })

    account = result.data[0]

    return jsonify({
        "authenticated": True,
        "account": account
    })


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.post("/logout")
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })