
import logging

from flask import Blueprint, jsonify, request
from backend.database import get_supabase

catalogue_bp = Blueprint(
    "catalogue", __name__, url_prefix="/api/catalogue"
)


@catalogue_bp.get("/products")
def list_public_products():
    try:
        supabase = get_supabase()

        query = (
            supabase.table("products")
            .select(
                "id,name,description,craft_category,material,color,"
                "dimensions,base_price,recommended_price,"
                "stock_quantity,image_url,ai_category,ai_material,"
                "created_at,artisan_id"
            )
            .eq("publication_status", "published")
            .gt("stock_quantity", 0)
            .order("created_at", desc=True)
        )

        search = (request.args.get("q") or "").strip()
        category = (request.args.get("category") or "").strip()
        material = (request.args.get("material") or "").strip()

        if search:
            safe_search = (
                search.replace("%", "")
                .replace(",", "")
                .replace("(", "")
                .replace(")", "")
            )
            query = query.ilike("name", f"%{safe_search}%")

        if category:
            query = query.eq("craft_category", category)

        if material:
            query = query.eq("material", material)

        sort = request.args.get("sort", "newest")
        if sort == "price_asc":
            query = query.order("base_price")
        elif sort == "price_desc":
            query = query.order("base_price", desc=True)

        result = query.limit(100).execute()
        products = result.data or []

        # Return safe public artisan display details only.
        artisan_ids = list({
            p["artisan_id"] for p in products if p.get("artisan_id")
        })
        artisans_by_id = {}

        if artisan_ids:
            artisan_result = (
                supabase.table("artisans")
                .select("id,full_name,state,district,craft_category")
                .in_("id", artisan_ids)
                .execute()
            )
            artisans_by_id = {
                a["id"]: a for a in (artisan_result.data or [])
            }

        for product in products:
            product["artisan"] = artisans_by_id.get(
                product.get("artisan_id")
            )

        return jsonify({
            "success": True,
            "products": products,
            "count": len(products),
        }), 200

    except Exception:
        logging.exception("Unable to load public catalogue")
        return jsonify({
            "success": False,
            "message": "Unable to load the product catalogue.",
        }), 500
