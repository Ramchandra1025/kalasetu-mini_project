
import logging

from flask import Blueprint, jsonify, request, session
from backend.database import get_supabase

enquiry_bp = Blueprint(
    "enquiries",
    __name__,
    url_prefix="/api/enquiries",
)

VALID_STATUSES = {"new", "in_progress", "replied", "closed"}


def require_artisan():
    """Resolve and validate the current artisan account."""
    account_id = session.get("account_id")

    if not account_id:
        return None, (jsonify({
            "success": False,
            "message": "Please log in to continue.",
        }), 401)

    try:
        result = (
            get_supabase()
            .table("accounts")
            .select("id,account_type,email_verified")
            .eq("id", account_id)
            .limit(1)
            .execute()
        )
        account = result.data[0] if result.data else None
    except Exception:
        logging.exception("Unable to verify enquiry session")
        return None, (jsonify({
            "success": False,
            "message": "Unable to verify your session.",
        }), 503)

    if not account:
        session.clear()
        return None, (jsonify({
            "success": False,
            "message": "Please log in again.",
        }), 401)

    if account.get("account_type") != "artisan":
        return None, (jsonify({
            "success": False,
            "message": "An artisan account is required.",
        }), 403)

    if not account.get("email_verified"):
        return None, (jsonify({
            "success": False,
            "message": "Please verify your email first.",
        }), 403)

    # Your existing schema uses artisans.id = accounts.id.
    try:
        profile = (
            get_supabase()
            .table("artisans")
            .select("id")
            .eq("id", account["id"])
            .limit(1)
            .execute()
        )
        if not profile.data:
            return None, (jsonify({
                "success": False,
                "message": "Artisan profile not found.",
            }), 404)
    except Exception:
        logging.exception("Unable to verify artisan profile")
        return None, (jsonify({
            "success": False,
            "message": "Unable to verify artisan profile.",
        }), 503)

    return account, None


def owned_enquiry(supabase, artisan_id, enquiry_id):
    """Never return an enquiry belonging to another artisan."""
    result = (
        supabase.table("enquiries")
        .select("*")
        .eq("id", enquiry_id)
        .eq("artisan_id", artisan_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def safe_product(supabase, product_id, artisan_id):
    if not product_id:
        return None

    result = (
        supabase.table("products")
        .select("id,name,image_url,base_price,craft_category")
        .eq("id", product_id)
        .eq("artisan_id", artisan_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


@enquiry_bp.get("")
def list_enquiries():
    account, error = require_artisan()
    if error:
        return error

    try:
        supabase = get_supabase()
        query = (
            supabase.table("enquiries")
            .select("*")
            .eq("artisan_id", account["id"])
        )

        status = (request.args.get("status") or "all").strip().lower()
        if status != "all":
            if status not in VALID_STATUSES:
                return jsonify({
                    "success": False,
                    "message": "Invalid enquiry status.",
                }), 400
            query = query.eq("status", status)

        result = query.order("last_message_at", desc=True).execute()
        enquiries = result.data or []

        product_ids = {
            item.get("product_id")
            for item in enquiries
            if item.get("product_id")
        }

        product_map = {}
        for product_id in product_ids:
            product = safe_product(
                supabase, product_id, account["id"]
            )
            if product:
                product_map[product_id] = product

        for item in enquiries:
            item["product"] = product_map.get(item.get("product_id"))

        return jsonify({
            "success": True,
            "enquiries": enquiries,
            "count": len(enquiries),
        }), 200

    except Exception:
        logging.exception("Unable to list enquiries")
        return jsonify({
            "success": False,
            "message": "Unable to load enquiries.",
        }), 500


@enquiry_bp.get("/<enquiry_id>")
def get_enquiry(enquiry_id):
    account, error = require_artisan()
    if error:
        return error

    try:
        supabase = get_supabase()
        enquiry = owned_enquiry(
            supabase, account["id"], enquiry_id
        )

        if not enquiry:
            return jsonify({
                "success": False,
                "message": "Enquiry not found.",
            }), 404

        messages_result = (
            supabase.table("enquiry_messages")
            .select("*")
            .eq("enquiry_id", enquiry_id)
            .order("created_at")
            .execute()
        )

        enquiry["messages"] = messages_result.data or []
        enquiry["product"] = safe_product(
            supabase, enquiry.get("product_id"), account["id"]
        )

        return jsonify({
            "success": True,
            "enquiry": enquiry,
        }), 200

    except Exception:
        logging.exception("Unable to load enquiry conversation")
        return jsonify({
            "success": False,
            "message": "Unable to load this conversation.",
        }), 500


@enquiry_bp.post("/<enquiry_id>/messages")
def reply_to_enquiry(enquiry_id):
    account, error = require_artisan()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    message = str(data.get("message") or "").strip()

    if not message:
        return jsonify({
            "success": False,
            "message": "Reply message is required.",
        }), 400

    if len(message) > 5000:
        return jsonify({
            "success": False,
            "message": "Replies must be 5,000 characters or fewer.",
        }), 400

    try:
        supabase = get_supabase()
        enquiry = owned_enquiry(
            supabase, account["id"], enquiry_id
        )

        if not enquiry:
            return jsonify({
                "success": False,
                "message": "Enquiry not found.",
            }), 404

        if enquiry["status"] == "closed":
            return jsonify({
                "success": False,
                "message": "Reopen this enquiry before replying.",
            }), 409

        inserted = (
            supabase.table("enquiry_messages")
            .insert({
                "enquiry_id": enquiry_id,
                "sender_account_id": account["id"],
                "sender_type": "artisan",
                "message": message,
            })
            .execute()
        )

        if not inserted.data:
            return jsonify({
                "success": False,
                "message": "Reply was not saved.",
            }), 500

        # A separate update is used because the current database schema
        # has no transaction/RPC configured for these two operations.
        updated = (
            supabase.table("enquiries")
            .update({
                "status": "replied",
                "last_message_at": inserted.data[0]["created_at"],
                "updated_at": inserted.data[0]["created_at"],
            })
            .eq("id", enquiry_id)
            .eq("artisan_id", account["id"])
            .execute()
        )

        if not updated.data:
            logging.error(
                "Reply saved but enquiry metadata update failed: %s",
                enquiry_id,
            )
            return jsonify({
                "success": False,
                "message": (
                    "The reply was saved, but the enquiry status "
                    "could not be updated. Refresh and check the conversation."
                ),
            }), 500

        return jsonify({
            "success": True,
            "message": "Reply saved successfully.",
            "reply": inserted.data[0],
            "enquiry": updated.data[0],
        }), 201

    except Exception:
        logging.exception("Unable to save enquiry reply")
        return jsonify({
            "success": False,
            "message": "Unable to save the reply.",
        }), 500


@enquiry_bp.patch("/<enquiry_id>/status")
def update_enquiry_status(enquiry_id):
    account, error = require_artisan()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    status = str(data.get("status") or "").strip().lower()

    if status not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "message": "Choose a valid enquiry status.",
        }), 400

    try:
        supabase = get_supabase()
        enquiry = owned_enquiry(
            supabase, account["id"], enquiry_id
        )

        if not enquiry:
            return jsonify({
                "success": False,
                "message": "Enquiry not found.",
            }), 404

        result = (
            supabase.table("enquiries")
            .update({"status": status})
            .eq("id", enquiry_id)
            .eq("artisan_id", account["id"])
            .execute()
        )

        if not result.data:
            return jsonify({
                "success": False,
                "message": "Status update was not confirmed.",
            }), 500

        return jsonify({
            "success": True,
            "message": "Enquiry status updated.",
            "enquiry": result.data[0],
        }), 200

    except Exception:
        logging.exception("Unable to update enquiry status")
        return jsonify({
            "success": False,
            "message": "Unable to update enquiry status.",
        }), 500
