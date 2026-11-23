from pathlib import Path

from flask import Flask, send_from_directory


from backend.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.artisan_routes import artisan_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.enquiry_routes import enquiry_bp
from backend.routes.catalogue_routes import catalogue_bp
from backend.routes.orders_routes import orders_bp


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(__name__)

app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = Config.SESSION_COOKIE_SECURE

# The frontend is served by this Flask app and uses same-origin requests.
# Do not emit credentialed CORS headers for arbitrary requesting origins.


# =========================================================
# REGISTER BLUEPRINTS
# =========================================================
app.register_blueprint(auth_bp)
app.register_blueprint(artisan_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(enquiry_bp)
app.register_blueprint(catalogue_bp)
app.register_blueprint(orders_bp)


# =========================================================
# FRONTEND PAGES
# =========================================================

@app.get("/")
def landing_page():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/login")
@app.get("/login.html")
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.get("/register")
@app.get("/register.html")
def register_page():
    return send_from_directory(FRONTEND_DIR, "register.html")


@app.get("/verify-email")
@app.get("/verify-email.html")
def verify_email_page():
    return send_from_directory(FRONTEND_DIR, "verify-email.html")


@app.get("/artisan")
@app.get("/artisan/")
def artisan_dashboard():
    return send_from_directory(
        FRONTEND_DIR / "artisan",
        "index.html"
    )


@app.get("/buyer")
@app.get("/buyer/")
def buyer_dashboard():
    return send_from_directory(
        FRONTEND_DIR / "buyer",
        "buyer_dashboard.html"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():
    return {
        "project": "KalaSetu",
        "status": "running",
        "database": "Supabase"
    }, 200


# =========================================================
# STATIC FRONTEND FILES
# =========================================================

@app.get("/<path:path>")
def frontend_files(path):
    file_path = (FRONTEND_DIR / path).resolve()

    # Prevent paths from escaping the frontend directory.
    if not file_path.is_relative_to(FRONTEND_DIR.resolve()):
        return {"error": "File not found"}, 404

    if file_path.is_file():
        return send_from_directory(FRONTEND_DIR, path)

    return {"error": "File not found", "path": path}, 404


# =========================================================
# RUN APPLICATION
# =========================================================


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=Config.DEBUG,
        use_reloader=False,
    )
