import logging
import math
import uuid
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

from flask import Blueprint, jsonify, request, session
from backend.database import get_supabase


artisan_bp = Blueprint("artisan", __name__, url_prefix="/api/artisan")

IMAGE_BUCKET = "product-images"
MAX_IMAGE_BYTES = 5 * 1024 * 1024

IMAGE_SIGNATURES = {
    "jpeg": {"extension": ".jpg", "content_type": "image/jpeg"},
    "png": {"extension": ".png", "content_type": "image/png"},
    "webp": {"extension": ".webp", "content_type": "image/webp"},
}


def detect_image_type(data):
    """Return verified image type, or None for unsupported content."""
    if data.startswith(b"\xff\xd8\xff"):
        return IMAGE_SIGNATURES["jpeg"]
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return IMAGE_SIGNATURES["png"]
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return IMAGE_SIGNATURES["webp"]
    return None


def read_validated_image(image):
    """Return (bytes, image_type, error); rewind the upload stream."""
    if not image or not image.filename:
        return None, None, None

    try:
        image.stream.seek(0)
        data = image.stream.read(MAX_IMAGE_BYTES + 1)
        image.stream.seek(0)
    except Exception:
        return None, None, "Unable to read the uploaded image."

    if not data:
        return None, None, "The selected image is empty."
    if len(data) > MAX_IMAGE_BYTES:
        return None, None, "Product images must be 5 MB or smaller."

    image_type = detect_image_type(data)
    if not image_type:
        return None, None, (
            "Unsupported image content. Upload a valid JPEG, PNG, or WebP image."
        )
    return data, image_type, None


def catalogue_product_image(image):
    """Run experimental cataloguing; inference failure does not block saving."""
    if not image or not image.filename:
        return None, {
            "status": "not_run",
            "message": "No product image was supplied for AI cataloguing.",
        }

    image_bytes, _, validation_error = read_validated_image(image)
    if validation_error:
        return None, {"status": "failed", "message": validation_error}

    try:
        from ai.cataloguing.predict import predict_image_bytes
        prediction = predict_image_bytes(image_bytes)
        return prediction, {
            "status": "completed",
            "experimental": True,
            "training_images": prediction.get("training_images", 12),
            "message": (
                "Experimental AI cataloguing completed. Review suggestions "
                "before relying on them."
            ),
        }
    except Exception:
        logging.exception("KalaSetu AI cataloguing failed")
        return None, {
            "status": "failed",
            "experimental": True,
            "training_images": 12,
            "message": "AI cataloguing failed. The product can still be saved.",
        }

@artisan_bp.post("/products/analyze-image")
def analyze_product_image():
    """Analyze an uploaded product image without saving a product."""
    account, error = require_artisan()
    if error:
        return error

    image = request.files.get("image")

    if not image or not image.filename:
        return jsonify({
            "success": False,
            "message": "Please select a product image.",
        }), 400

    prediction, ai_analysis = catalogue_product_image(image)

    invalid_image_messages = {
        "The selected image is empty.",
        "Product images must be 5 MB or smaller.",
        "Unsupported image content. Upload a valid JPEG, PNG, or WebP image.",
        "Unable to read the uploaded image.",
    }

    if ai_analysis.get("message") in invalid_image_messages:
        return jsonify({
            "success": False,
            "message": ai_analysis["message"],
        }), 400

    if not prediction:
        return jsonify({
            "success": False,
            "message": ai_analysis.get(
                "message",
                "Image analysis failed. Please enter product details manually.",
            ),
            "ai_analysis": ai_analysis,
        }), 422

    return jsonify({
        "success": True,
        "message": "Image analysis completed. Review the suggestions before saving.",
        "suggestions": {
            "category": prediction.get("category"),
            "material": prediction.get("material"),
            "color": prediction.get("color"),
        },
        "ai_analysis": ai_analysis,
        "experimental": True,
        "training_images": prediction.get("training_images"),
    }), 200


def build_ai_attributes(prediction, ai_analysis):
    """Build JSON-compatible values for products.ai_attributes."""
    return {
        "status": ai_analysis.get("status", "not_run"),
        "color": prediction.get("color") if prediction else None,
        "confidence": {
            "category": prediction["category"]["confidence"],
            "material": prediction["material"]["confidence"],
            "color": prediction["color"]["confidence"],
        } if prediction else None,
        "experimental": True,
        "training_images": (
            prediction.get("training_images", 12) if prediction else 12
        ),
        "message": ai_analysis.get("message"),
    }


def remove_storage_object(supabase, storage_path):
    """Best-effort cleanup of an uploaded object."""
    if not storage_path:
        return
    try:
        supabase.storage.from_(IMAGE_BUCKET).remove([storage_path])
    except Exception:
        logging.exception("Unable to remove storage object: %s", storage_path)


def upload_product_image(supabase, artisan_id, image):
    """Upload an optional image; return (public_url, path, error)."""
    if not image or not image.filename:
        return None, None, None

    image_bytes, image_type, validation_error = read_validated_image(image)
    if validation_error:
        return None, None, validation_error
    if image_bytes is None:
        return None, None, None

    storage_path = f"{artisan_id}/{uuid.uuid4().hex}{image_type['extension']}"

    try:
        storage = supabase.storage.from_(IMAGE_BUCKET)
        storage.upload(
            storage_path,
            image_bytes,
            {
                "content-type": image_type["content_type"],
                "upsert": "false",
            },
        )
        public_url = storage.get_public_url(storage_path)
        if not isinstance(public_url, str) or not public_url.startswith("https://"):
            remove_storage_object(supabase, storage_path)
            return None, None, "Storage did not return a valid public image URL."
        return public_url, storage_path, None
    except Exception:
        logging.exception("Product image upload failed")
        remove_storage_object(supabase, storage_path)
        return (
            None,
            None,
            "Image upload failed. Check the product-images bucket and Supabase configuration.",
        )


def get_current_account():
    """Resolve the account from the existing Flask session."""
    account_id = session.get("account_id")
    if not account_id:
        return None
    result = (
        get_supabase()
        .table("accounts")
        .select(
            "id,name,email,account_type,"
            "preferred_language,email_verified"
        )
        .eq("id", account_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def require_artisan():
    """Return (account, error_response)."""
    try:
        account = get_current_account()
    except Exception:
        logging.exception("Unable to verify the current account")
        return None, (
            jsonify({
                "success": False,
                "message": "Unable to verify your session. Please try again.",
            }),
            503,
        )

    if not account:
        return None, (jsonify({
            "success": False, "message": "Please log in to continue."
        }), 401)
    if account.get("account_type") != "artisan":
        return None, (jsonify({
            "success": False, "message": "An artisan account is required."
        }), 403)
    if not account.get("email_verified"):
        return None, (jsonify({
            "success": False, "message": "Please verify your email first."
        }), 403)
    return account, None


def get_artisan_products(artisan_id):
    result = (
        get_supabase().table("products").select("*")
        .eq("artisan_id", artisan_id)
        .order("created_at", desc=True).execute()
    )
    return result.data or []


def get_owned_product(supabase, artisan_id, product_id):
    result = (
        supabase.table("products").select("*")
        .eq("id", product_id).eq("artisan_id", artisan_id)
        .limit(1).execute()
    )
    return result.data[0] if result.data else None


def get_product_storage_path(image_url, artisan_id):
    """Extract a storage path only if it belongs to this artisan."""
    if not image_url or not artisan_id:
        return None
    try:
        parsed = urlparse(image_url)
        marker = f"/storage/v1/object/public/{IMAGE_BUCKET}/"
        if marker not in parsed.path:
            return None
        path = unquote(parsed.path.split(marker, 1)[1])
        parts = path.split("/")
        if (
            len(parts) < 2
            or parts[0] != str(artisan_id)
            or any(part in ("", ".", "..") for part in parts)
        ):
            return None
        return path
    except (TypeError, ValueError):
        return None


def validate_product_fields(form, existing=None):
    """Validate fields and return (updates, error_message)."""
    name = (form.get("name") or "").strip()
    category = (form.get("category") or "").strip()
    material = (form.get("materials") or form.get("material") or "").strip()
    description = (form.get("description") or "").strip()
    price_raw = (
        form.get("price") if form.get("price") is not None
        else form.get("base_price")
    )
    quantity_raw = (
        form.get("quantity") if form.get("quantity") is not None
        else form.get("stock_quantity")
    )

    if existing:
        if not name:
            name = existing.get("name") or ""
        if not category:
            category = existing.get("craft_category") or ""
        if not material:
            material = existing.get("material") or ""
        if not description:
            description = existing.get("description") or ""
        if price_raw in (None, ""):
            price_raw = existing.get("base_price")
        if quantity_raw in (None, ""):
            quantity_raw = existing.get("stock_quantity", 0)

    if not name:
        return None, "Product name is required."
    if len(name) > 120:
        return None, "Product name must be 120 characters or fewer."
    if len(description) > 1500:
        return None, "Description must be 1500 characters or fewer."
    if len(material) > 160:
        return None, "Materials must be 160 characters or fewer."

    try:
        price = float(price_raw)
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        return None, "Enter a valid price and whole-number quantity."

    if not math.isfinite(price) or price <= 0:
        return None, "Price must be a finite positive number."
    if quantity < 0 or str(quantity_raw).strip() != str(quantity):
        return None, "Quantity must be a non-negative whole number."

    return {
        "name": name,
        "craft_category": category or None,
        "material": material or None,
        "description": description or None,
        "base_price": price,
        "stock_quantity": quantity,
    }, None


# ============================================================
# DASHBOARD
# ============================================================

@artisan_bp.get("/dashboard")
def dashboard():
    account, error = require_artisan()
    if error:
        return error
    try:
        supabase = get_supabase()
        artisan_id = account["id"]
        products = get_artisan_products(artisan_id)

        orders_result = (
            supabase.table("orders").select("id,status,total_amount")
            .eq("artisan_id", artisan_id).execute()
        )
        orders = orders_result.data or []
        active_statuses = {"pending", "processing"}
        active_orders = sum(
            1 for order in orders
            if (order.get("status") or "").lower() in active_statuses
        )
        recorded_order_value = sum(
            float(order.get("total_amount") or 0) for order in orders
        )

        profile_result = (
            supabase.table("artisans")
            .select(
                "id,full_name,phone,profile_image_url,state,district,"
                "village,craft_category,primary_material,"
                "preferred_language,onboarding_completed,craft_story"
            )
            .eq("id", artisan_id).limit(1).execute()
        )
        profile = profile_result.data[0] if profile_result.data else None

        stats = {
            "total_products": len(products),
            "product_count": len(products),
            "pending_orders": active_orders,
            "active_orders": active_orders,
            "estimated_revenue": None,
            "recorded_order_value": round(recorded_order_value, 2),
            "potential_buyers": None,
            "open_enquiries": None,
            "market_opportunities": None,
        }
        return jsonify({
            "success": True,
            "account": {
                "id": account["id"],
                "name": account["name"],
                "email": account["email"],
                "account_type": account["account_type"],
                "preferred_language": account.get("preferred_language"),
            },
            "profile": profile,
            "stats": stats,
            "products": products[:20],
        }), 200
    except Exception:
        logging.exception("Unable to load artisan dashboard")
        return jsonify({
            "success": False,
            "message": "Unable to load dashboard data. Please try again.",
        }), 500



# ============================================================
# ARTISAN FULFILMENT ORDERS
# ============================================================

@artisan_bp.get("/orders")
def list_artisan_orders():
    account, error = require_artisan()
    if error:
        return error

    try:
        supabase = get_supabase()
        artisan_id = account["id"]

        result = (
            supabase.table("orders")
            .select(
                "id,order_reference,product_id,quantity,"
                "total_amount,status,payment_status,"
                "buyer_name,buyer_phone,delivery_address,"
                "created_at,updated_at"
            )
            .eq("artisan_id", artisan_id)
            .order("created_at", desc=True)
            .execute()
        )

        return jsonify({
            "success": True,
            "orders": result.data or [],
            "count": len(result.data or [])
        }), 200

    except Exception:
        logging.exception("Unable to load artisan fulfilment orders")
        return jsonify({
            "success": False,
            "message": "Unable to load orders. Please try again."
        }), 500

# ============================================================
# PRODUCTS LIST
# ============================================================

@artisan_bp.get("/products")
def list_products():
    account, error = require_artisan()
    if error:
        return error
    try:
        products = get_artisan_products(account["id"])
        return jsonify({
            "success": True,
            "products": products,
            "count": len(products),
        }), 200
    except Exception:
        logging.exception("Unable to list artisan products")
        return jsonify({
            "success": False,
            "message": "Unable to load products. Please try again.",
        }), 500


# ============================================================
# ADD PRODUCT WITH AI CATALOGUING
# ============================================================

@artisan_bp.post("/products")
def add_product():
    account, error = require_artisan()
    if error:
        return error

    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip()
    material = (request.form.get("materials") or request.form.get("material") or "").strip()
    description = (request.form.get("description") or "").strip()
    price_raw = (request.form.get("price") or request.form.get("base_price") or "").strip()
    quantity_raw = (request.form.get("quantity") or "1").strip()

    if not name:
        return jsonify({"success": False, "message": "Product name is required."}), 400
    if len(name) > 120:
        return jsonify({"success": False, "message": "Product name must be 120 characters or fewer."}), 400
    if len(description) > 1500:
        return jsonify({"success": False, "message": "Description must be 1500 characters or fewer."}), 400
    if len(material) > 160:
        return jsonify({"success": False, "message": "Materials must be 160 characters or fewer."}), 400

    try:
        price = float(price_raw)
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Enter a valid price and whole-number quantity."}), 400

    if not math.isfinite(price) or price <= 0:
        return jsonify({"success": False, "message": "Price must be a finite positive number."}), 400
    if quantity < 0 or str(quantity_raw).strip() != str(quantity):
        return jsonify({"success": False, "message": "Quantity must be a non-negative whole number."}), 400

    image = request.files.get("image")
    prediction, ai_analysis = catalogue_product_image(image)

    invalid_image_messages = {
        "The selected image is empty.",
        "Product images must be 5 MB or smaller.",
        "Unsupported image content. Upload a valid JPEG, PNG, or WebP image.",
        "Unable to read the uploaded image.",
    }
    if image and image.filename and ai_analysis.get("message") in invalid_image_messages:
        return jsonify({"success": False, "message": ai_analysis["message"]}), 400

    supabase = get_supabase()
    storage_path = None
    try:
        image_url, storage_path, upload_error = upload_product_image(
            supabase, account["id"], image
        )
        if upload_error:
            return jsonify({"success": False, "message": upload_error}), 400

        product_data = {
            "artisan_id": account["id"],
            "name": name,
            "description": description or None,
            "craft_category": category or None,
            "material": material or None,
            "base_price": price,
            "recommended_price": None,
            "stock_quantity": quantity,
            "image_url": image_url,
            "ai_category": prediction["category"]["label"] if prediction else None,
            "ai_material": prediction["material"]["label"] if prediction else None,
            "ai_attributes": build_ai_attributes(prediction, ai_analysis),
        }

        try:
            result = supabase.table("products").insert(product_data).execute()
        except Exception:
            remove_storage_object(supabase, storage_path)
            raise

        if not result.data:
            remove_storage_object(supabase, storage_path)
            return jsonify({"success": False, "message": "The product could not be saved."}), 500

        return jsonify({
            "success": True,
            "message": "Product saved successfully.",
            "product": result.data[0],
            "ai_analysis": ai_analysis,
        }), 201
    except Exception:
        logging.exception("Unable to save artisan product")
        remove_storage_object(supabase, storage_path)
        return jsonify({
            "success": False,
            "message": "Unable to save product. Please check backend logs.",
        }), 500


# ------------------------------------------------------------
# PUBLISH / UNPUBLISH / DELETE PRODUCT
# ------------------------------------------------------------

@artisan_bp.patch("/products/<product_id>/publication")
def update_product_publication(product_id):
    account, error = require_artisan()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    status = data.get("publication_status")

    if status not in {"published", "draft"}:
        return jsonify({
            "success": False,
            "message": "Status must be published or draft.",
        }), 400

    supabase = get_supabase()

    existing = (
        supabase.table("products")
        .select("id,artisan_id,stock_quantity")
        .eq("id", product_id)
        .eq("artisan_id", account["id"])
        .limit(1)
        .execute()
    )

    if not existing.data:
        return jsonify({
            "success": False,
            "message": "Product not found or you do not own it.",
        }), 404

    product = existing.data[0]

    if status == "published":
        if int(product.get("stock_quantity") or 0) <= 0:
            return jsonify({
                "success": False,
                "message": "Add available stock before publishing.",
            }), 400

        published_at = datetime.now(timezone.utc).isoformat()
    else:
        published_at = None

    result = (
        supabase.table("products")
        .update({
            "publication_status": status,
            "published_at": published_at,
        })
        .eq("id", product_id)
        .eq("artisan_id", account["id"])
        .execute()
    )

    if not result.data:
        return jsonify({
            "success": False,
            "message": "The publication status could not be updated.",
        }), 500

    return jsonify({
        "success": True,
        "message": (
            "Product published successfully."
            if status == "published"
            else "Product moved back to drafts."
        ),
        "product": result.data[0],
    }), 200



# ============================================================
# EDIT PRODUCT WITH OPTIONAL AI RE-CATALOGUING
# ============================================================

@artisan_bp.put("/products/<product_id>")
def update_product(product_id):
    account, error = require_artisan()
    if error:
        return error

    supabase = get_supabase()
    artisan_id = account["id"]
    new_storage_path = None

    try:
        existing = get_owned_product(supabase, artisan_id, product_id)
        if not existing:
            return jsonify({"success": False, "message": "Product not found."}), 404

        updates, validation_error = validate_product_fields(request.form, existing)
        if validation_error:
            return jsonify({"success": False, "message": validation_error}), 400

        old_storage_path = get_product_storage_path(existing.get("image_url"), artisan_id)
        image = request.files.get("image")
        ai_analysis = None

        if image and image.filename:
            prediction, ai_analysis = catalogue_product_image(image)
            invalid_image_messages = {
                "The selected image is empty.",
                "Product images must be 5 MB or smaller.",
                "Unsupported image content. Upload a valid JPEG, PNG, or WebP image.",
                "Unable to read the uploaded image.",
            }
            if ai_analysis.get("message") in invalid_image_messages:
                return jsonify({"success": False, "message": ai_analysis["message"]}), 400

            image_url, new_storage_path, upload_error = upload_product_image(
                supabase, artisan_id, image
            )
            if upload_error:
                return jsonify({"success": False, "message": upload_error}), 400

            updates["image_url"] = image_url
            # If inference fails, preserve the previous AI metadata.
            if prediction:
                updates["ai_category"] = prediction["category"]["label"]
                updates["ai_material"] = prediction["material"]["label"]
                updates["ai_attributes"] = build_ai_attributes(prediction, ai_analysis)

        result = (
            supabase.table("products").update(updates)
            .eq("id", product_id).eq("artisan_id", artisan_id).execute()
        )
        if not result.data:
            remove_storage_object(supabase, new_storage_path)
            return jsonify({
                "success": False,
                "message": "The product update was not confirmed.",
            }), 500

        if new_storage_path and old_storage_path:
            remove_storage_object(supabase, old_storage_path)

        response = {
            "success": True,
            "message": "Product updated successfully.",
            "product": result.data[0],
        }
        if ai_analysis is not None:
            response["ai_analysis"] = ai_analysis
        return jsonify(response), 200
    except Exception:
        logging.exception("Failed to update artisan product")
        remove_storage_object(supabase, new_storage_path)
        return jsonify({
            "success": False,
            "message": "Unable to update product. Check backend logs.",
        }), 500


# ============================================================
# DELETE PRODUCT
# ============================================================

@artisan_bp.delete("/products/<product_id>")
def delete_product(product_id):
    account, error = require_artisan()
    if error:
        return error

    supabase = get_supabase()
    artisan_id = account["id"]

    try:
        existing = get_owned_product(supabase, artisan_id, product_id)
        if not existing:
            return jsonify({"success": False, "message": "Product not found."}), 404

        storage_path = get_product_storage_path(existing.get("image_url"), artisan_id)
        result = (
            supabase.table("products").delete()
            .eq("id", product_id).eq("artisan_id", artisan_id).execute()
        )
        if not result.data:
            return jsonify({
                "success": False,
                "message": "Product deletion was not confirmed.",
            }), 500

        if storage_path:
            remove_storage_object(supabase, storage_path)

        return jsonify({
            "success": True,
            "message": "Product deleted successfully.",
            "product_id": product_id,
        }), 200
    except Exception:
        logging.exception("Failed to delete artisan product")
        return jsonify({
            "success": False,
            "message": "Unable to delete product. It may be linked to existing orders.",
        }), 500



# ============================================================
# PUBLISH / UNPUBLISH PRODUCT
# ============================================================

@artisan_bp.post("/products/<product_id>/publish")
def publish_product(product_id):
    account, error = require_artisan()
    if error:
        return error

    try:
        supabase = get_supabase()
        product = get_owned_product(
            supabase, account["id"], product_id
        )

        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found.",
            }), 404

        # Require the basic information buyers need.
        if not product.get("name") or not product.get("base_price"):
            return jsonify({
                "success": False,
                "message": "Add a product name and valid price before publishing.",
            }), 400

        try:
            stock_quantity = int(product.get("stock_quantity") or 0)
        except (TypeError, ValueError):
            stock_quantity = 0

        if stock_quantity <= 0:
            return jsonify({
                "success": False,
                "message": "Add available stock before publishing.",
            }), 400

        result = (
            supabase.table("products")
            .update({
                "publication_status": "published",
                "published_at": product.get("published_at")
                or datetime.now(timezone.utc).isoformat(),
            })
            .eq("id", product_id)
            .eq("artisan_id", account["id"])
            .execute()
        )

        if not result.data:
            return jsonify({
                "success": False,
                "message": "Publishing could not be confirmed.",
            }), 500

        return jsonify({
            "success": True,
            "message": "Product published successfully.",
            "product": result.data[0],
        }), 200

    except Exception:
        logging.exception("Unable to publish product")
        return jsonify({
            "success": False,
            "message": "Unable to publish this product.",
        }), 500


@artisan_bp.post("/products/<product_id>/unpublish")
def unpublish_product(product_id):
    account, error = require_artisan()
    if error:
        return error

    try:
        supabase = get_supabase()
        product = get_owned_product(
            supabase, account["id"], product_id
        )

        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found.",
            }), 404

        result = (
            supabase.table("products")
            .update({
                "publication_status": "draft",
                "published_at": None,
            })
            .eq("id", product_id)
            .eq("artisan_id", account["id"])
            .execute()
        )

        if not result.data:
            return jsonify({
                "success": False,
                "message": "Unpublishing could not be confirmed.",
            }), 500

        return jsonify({
            "success": True,
            "message": "Product unpublished successfully.",
            "product": result.data[0],
        }), 200

    except Exception:
        logging.exception("Unable to unpublish product")
        return jsonify({
            "success": False,
            "message": "Unable to unpublish this product.",
        }), 500

# ============================================================
# UPDATE CRAFT PROFILE
# ============================================================

@artisan_bp.put("/profile")
def update_profile():
    account, error = require_artisan()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    allowed_fields = {
        "full_name", "craft_category", "primary_material",
        "preferred_language", "state", "district", "village",
        "phone", "craft_story",
    }
    updates = {
        key: value.strip()
        for key, value in data.items()
        if key in allowed_fields and isinstance(value, str)
    }

    if not updates:
        return jsonify({
            "success": False,
            "message": "No valid profile changes were supplied.",
        }), 400
    if "full_name" in updates and not updates["full_name"]:
        return jsonify({
            "success": False,
            "message": "Artisan name cannot be empty.",
        }), 400

    try:
        supabase = get_supabase()
        account_id = account["id"]
        existing = (
            supabase.table("artisans")
            .select(
                "id,full_name,phone,profile_image_url,state,district,"
                "village,craft_category,primary_material,"
                "preferred_language,onboarding_completed,craft_story"
            )
            .eq("id", account_id).limit(1).execute()
        )
        if not existing.data:
            return jsonify({
                "success": False,
                "message": (
                    "Artisan profile not found for this account. "
                    "No changes were saved."
                ),
            }), 404

        result = (
            supabase.table("artisans").update(updates)
            .eq("id", existing.data[0]["id"]).execute()
        )
        if not result.data:
            return jsonify({
                "success": False,
                "message": "Supabase did not confirm the profile update.",
            }), 500

        return jsonify({
            "success": True,
            "message": "Craft profile updated successfully.",
            "profile": result.data[0],
        }), 200
    except Exception:
        logging.exception("Unable to update artisan profile")
        return jsonify({
            "success": False,
            "message": "Unable to update profile. Please try again.",
        }), 500
