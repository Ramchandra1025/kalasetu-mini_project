# KalaSetu Project Guide

## What this project does

KalaSetu is a marketplace and market-intelligence prototype connecting Indian artisans with buyers. It combines an HTML/CSS/JavaScript web client, a Flask API, Supabase for application data and product images, and a collection of Python AI/ML experiments and prediction adapters.

## How the pieces fit together

```text
Browser (frontend/)
   | same-origin /api requests, Flask session cookie
   v
Flask app (backend/app.py)
   |-- auth, artisan, buyer catalogue, enquiries, orders routes
   |-- AI routes -> backend/ai registry and pipeline -> ai/ model code
   v
Supabase (Postgres tables, Auth-independent app records, Storage)
```

The browser does not call Supabase directly. `frontend/js/api.js` centralizes requests and includes credentials so the Flask session cookie is sent. `backend/database.py` creates a Supabase client with the service-role key; keep that key on the server and out of frontend files.

## Main directories

| Path | Purpose |
| --- | --- |
| `backend/app.py` | Creates the Flask application, loads configuration, registers API blueprints, serves frontend pages/assets, and exposes `/api/health`. |
| `backend/routes/` | API endpoints for authentication, artisan profiles/products, public catalogue, enquiries, orders, and AI. |
| `backend/services/` | Shared backend operations such as OTP/email and product intelligence orchestration. |
| `backend/ai/` | Production-facing AI service adapters, registry, shared input/error handling, and pipeline. |
| `frontend/` | Static pages, styles, browser scripts, and artisan/buyer dashboards. |
| `ai/` | Per-feature model code: data preparation, training, inference, evaluation, and scoring. |
| `ml/datasets/`, `ml/models/` | Dataset and saved model artifacts used by AI modules. |
| `research/` | Experiment metadata and evaluation/result outputs. |
| `database/` | Intended schema/seed documentation and scripts. The current `schema.sql` and `seed.py` are empty. |
| `tests/` | AI and backend integration test modules. |

## Backend and API map

The Flask app registers these blueprints:

| Prefix | Responsibilities |
| --- | --- |
| `/api/auth` | Registration, email OTP verification/resend, login, current session (`/me`), and logout. |
| `/api/artisan` | Artisan dashboard and profile, product image analysis, product CRUD, publication state, and orders. |
| `/api/catalogue` | Public product listing for buyers. |
| `/api/enquiries` | Enquiry listing/details, messages, and status updates. |
| `/api/orders` | Checkout, buyer order listing, and tracking. |
| `/api/ai` | AI service health/listing, digital product passport, pricing, and multi-module pipeline. |

Authentication uses password hashing/verification in `backend/utils/security.py`, OTP and email helpers in `backend/services/`, and Flask's signed session cookie. Configuration is read from `backend/.env`; `backend/config.py` requires `FLASK_SECRET_KEY`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY` at import time. EmailJS settings and OTP/session options are also configurable there.

## Frontend flow

`backend/app.py` serves the landing page and named routes for login, registration, verification, artisan, and buyer pages. Static assets are served from `frontend/` with a resolved-path check to prevent traversal outside that directory. The JavaScript modules call the same-origin `/api` endpoints. Registration starts email verification; login establishes the session and sends the user to the dashboard matching the account type. Buyer flows include catalogue browsing and checkout; artisan flows include profile/product management and AI-assisted product entry.

## AI and model layer

`backend/ai/registry.py` exposes adapters for cataloguing, pricing, demand, market opportunity, recommendations, waste, anomaly detection, NLP, OCR, voice, inventory, logistics, sustainability, and digital product passports. `backend/ai/pipeline.py` calls one or more registered services. Most adapters import their model implementation from `ai/` only when prediction is requested.

The separate `backend/services/product_ai_service.py` coordinates cataloguing, pricing, demand, and sustainability suggestions for artisan product entry. Missing required inputs are returned as `needs_input`; prediction failures are represented as a result instead of inventing values. Some model paths explicitly label outputs as experimental/prototype, so treat AI estimates as decision support and review them before using them in listings or business decisions.

The model code and artifacts may need additional packages beyond `backend/requirements.txt` (for example model, image, data-frame, or speech libraries). Check the imports of the AI module you plan to run and ensure its corresponding artifact exists under `ml/models/`. Image/audio prediction services accept filesystem paths in their service payloads; the artisan product-analysis route separately accepts uploaded image data.

## Running locally

1. Create and activate a Python virtual environment.
2. Install the backend dependencies: `pip install -r backend/requirements.txt`.
3. Create `backend/.env` and set at least `FLASK_SECRET_KEY`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY`. Add EmailJS values if verification email delivery is enabled. There is no checked-in `.env.example` at present.
4. Ensure the Supabase project has the tables, policies, and `product-images` Storage bucket expected by the route code. The repository's `database/schema.sql` and `database/seed.py` do not currently define these.
5. From the project root, run `python backend/app.py` (or use the root `run.py` launcher if its import setup matches your environment). The app binds to `127.0.0.1:5000` in debug mode.
6. Open `http://127.0.0.1:5000`; check `/api/health` for the basic backend status.

For model development, each `ai/<module>/` directory generally contains its own configuration, dataset/features, train, predict, and evaluate code where applicable. `scripts/check.py` contains sample payloads and invokes registered services; it writes a report under `research/results/` when run.

## Current repository notes

- `README.md` is a short MVP overview; this document reflects the current code layout and routes.
- `database/schema.sql` and `database/seed.py` are empty, and there is no checked-in `.env.example`.
- `backend/requirements.txt` lists Flask, dotenv, Supabase, requests, Argon2, and CORS, but does not enumerate all optional AI inference dependencies.
- The project contains backup files (`.bak`, `.backup`) alongside live frontend/backend files; these are not the active route/page sources.
- The main app enables Flask debug mode and uses the Supabase service-role key. Use appropriate secret handling and production configuration before deployment.

