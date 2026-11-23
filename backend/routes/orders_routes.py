
from flask import Blueprint, jsonify, request, session
from backend.database import get_supabase

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


def get_current_buyer():
    account_id = session.get("account_id")

    if not account_id:
        return None, (
            jsonify({
                "success": False,
                "message": "Please log in to place or view orders."
            }),
            401
        )

    try:
        db = get_supabase()
        result = (
            db.table("accounts")
            .select("id, account_type, email_verified")
            .eq("id", account_id)
            .limit(1)
            .execute()
        )

        accounts = result.data or []

        if not accounts:
            session.clear()
            return None, (
                jsonify({
                    "success": False,
                    "message": "Your account could not be found."
                }),
                401
            )

        account = accounts[0]

        if account.get("account_type") != "buyer":
            return None, (
                jsonify({
                    "success": False,
                    "message": "A buyer account is required."
                }),
                403
            )

        if account.get("email_verified") is not True:
            return None, (
                jsonify({
                    "success": False,
                    "message": "Please verify your email first."
                }),
                403
            )

        return account, None

    except Exception:
        return None, (
            jsonify({
                "success": False,
                "message": "Unable to verify your account."
            }),
            500
        )


@orders_bp.get("/health")
def orders_health():
    return jsonify({
        "success": True,
        "module": "orders",
        "status": "ready"
    }), 200


@orders_bp.post("/checkout")
def checkout():
    account, error = get_current_buyer()
    if error:
        return error

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid checkout request is required."
        }), 400

    items = data.get("items")
    delivery = data.get("delivery")

    if not isinstance(items, list) or not items:
        return jsonify({
            "success": False,
            "message": "Your cart is empty."
        }), 400

    if not isinstance(delivery, dict):
        return jsonify({
            "success": False,
            "message": "Delivery details are required."
        }), 400

    # Only allow the fields needed by the SQL function.
    normalized_items = []

    for item in items:
        if not isinstance(item, dict):
            return jsonify({
                "success": False,
                "message": "Invalid cart item."
            }), 400

        product_id = str(item.get("product_id", "")).strip()
        quantity = item.get("quantity")

        if (
            len(product_id) != 36
            or not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity < 1
            or quantity > 100
        ):
            return jsonify({
                "success": False,
                "message": "Each item needs a valid product ID and quantity."
            }), 400

        normalized_items.append({
            "product_id": product_id,
            "quantity": quantity
        })

    if len(normalized_items) > 50:
        return jsonify({
            "success": False,
            "message": "You can order at most 50 product lines at once."
        }), 400

    if len({
        item["product_id"] for item in normalized_items
    }) != len(normalized_items):
        return jsonify({
            "success": False,
            "message": "Duplicate products must be combined in your cart."
        }), 400

    clean_delivery = {
        "name": str(delivery.get("name", "")).strip(),
        "phone": str(delivery.get("phone", "")).strip(),
        "address": str(delivery.get("address", "")).strip(),
        "city": str(delivery.get("city", "")).strip(),
        "state": str(delivery.get("state", "")).strip(),
        "pincode": str(delivery.get("pincode", "")).strip()
    }

    if (
        not clean_delivery["name"]
        or len(clean_delivery["name"]) > 100
        or not clean_delivery["phone"]
        or len(clean_delivery["phone"]) > 20
        or not clean_delivery["address"]
        or len(clean_delivery["address"]) > 1000
        or not clean_delivery["city"]
        or len(clean_delivery["city"]) > 100
        or not clean_delivery["state"]
        or len(clean_delivery["state"]) > 100
        or not clean_delivery["pincode"].isdigit()
        or len(clean_delivery["pincode"]) != 6
    ):
        return jsonify({
            "success": False,
            "message": "Please enter valid delivery details."
        }), 400

    try:
        db = get_supabase()

        result = db.rpc(
            "create_buyer_orders",
            {
                "p_buyer_id": account["id"],
                "p_items": normalized_items,
                "p_delivery": clean_delivery
            }
        ).execute()

        payload = result.data

        # Supabase RPC responses may be wrapped differently depending
        # on the client/version; normalize the common response shapes.
        if isinstance(payload, list) and payload:
            payload = payload[0]

        if not isinstance(payload, dict) or payload.get("success") is not True:
            raise RuntimeError("The database did not confirm order creation.")

        return jsonify(payload), 201

    except Exception as exc:
        # Log details server-side; don't expose SQL or internal errors.
        print("Checkout error:", repr(exc))

        return jsonify({
            "success": False,
            "message": (
                "Checkout could not be completed. "
                "Check product availability and try again."
            )
        }), 400


@orders_bp.get("")
def get_my_orders():
    account, error = get_current_buyer()
    if error:
        return error

    try:
        db = get_supabase()
        result = (
            db.table("orders")
            .select(
                "id, order_reference, status, total_amount, "
                "payment_status, created_at, updated_at"
            )
            .eq("buyer_id", account["id"])
            .order("created_at", desc=True)
            .execute()
        )

        return jsonify({
            "success": True,
            "orders": result.data or []
        }), 200

    except Exception as exc:
        print("Order listing error:", repr(exc))
        return jsonify({
            "success": False,
            "message": "Unable to retrieve your orders."
        }), 500


@orders_bp.get("/<order_id>/tracking")
def get_order_tracking(order_id):
    account, error = get_current_buyer()
    if error:
        return error

    try:
        db = get_supabase()

        order_result = (
            db.table("orders")
            .select(
                "id, order_reference, status, total_amount, "
                "payment_status, created_at, updated_at"
            )
            .eq("id", order_id)
            .eq("buyer_id", account["id"])
            .limit(1)
            .execute()
        )

        orders = order_result.data or []
        if not orders:
            return jsonify({
                "success": False,
                "message": "Order not found."
            }), 404

        order = orders[0]

        events_result = (
            db.table("order_tracking_events")
            .select("id, status, description, location, created_at")
            .eq("order_id", order["id"])
            .order("created_at", desc=True)
            .execute()
        )

        return jsonify({
            "success": True,
            "order": order,
            "events": events_result.data or []
        }), 200

    except Exception as exc:
        print("Order tracking error:", repr(exc))
        return jsonify({
            "success": False,
            "message": "Unable to retrieve tracking information."
        }), 500
