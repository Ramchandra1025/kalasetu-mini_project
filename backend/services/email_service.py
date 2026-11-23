import requests

from backend.config import Config


EMAILJS_URL = "https://api.emailjs.com/api/v1.0/email/send"


def send_verification_email(
    name: str,
    email: str,
    otp: str
) -> bool:

    expiry = f"{Config.OTP_EXPIRY_MINUTES} minutes"

    template_params = {
        "name": name,
        "email": email,
        "otp": otp,
        "expiry": expiry
    }

    payload = {
        "service_id": Config.EMAILJS_SERVICE_ID,
        "template_id": Config.EMAILJS_TEMPLATE_ID,
        "user_id": Config.EMAILJS_PUBLIC_KEY,
        "template_params": template_params
    }

    # Add private key only if configured
    if Config.EMAILJS_PRIVATE_KEY:
        payload["accessToken"] = Config.EMAILJS_PRIVATE_KEY

    try:

        response = requests.post(
            EMAILJS_URL,
            json=payload,
            timeout=15
        )

        if response.status_code == 200:
            return True

        print("EmailJS error:", response.text)
        return False

    except requests.RequestException as error:

        print("EmailJS request failed:", error)

        return False