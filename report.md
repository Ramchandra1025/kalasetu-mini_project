# KalaSetu QA and Testing Report

**Test date:** 30 October 2026  
**Result:** Pass with fixes applied; external integration and interactive browser coverage remain open.

## Executive summary

I tested the Flask app through both a real local HTTP server and Flask's test client, checked all rendered local page assets and navigation links, exercised unauthenticated and invalid API requests, reviewed auth/session and CORS behavior, injected AI failures to inspect responses and logs, ran the existing test suite, and checked Python/JavaScript syntax.

The review found and fixed broken frontend paths and missing script references, hard-coded localhost API URLs, credentialed CORS that reflected arbitrary origins, an empty AI pipeline accepted as a successful request, and AI exceptions that returned internal details to callers. Earlier fixes to the launcher, debug configuration, OCR/voice test paths, product publication validation/timestamps, and UTC timestamps were also revalidated.

## Results

- Existing automated suite: **148 passed**.
- Python compilation: **passed**.
- JavaScript syntax: **9 files passed**.
- Local page routes: **11/11 returned HTTP 200**.
- Local page asset references: **64/64 returned HTTP 200**.
- Navigation links: **33/33 returned non-error responses**.
- HTTP smoke probes: health and AI discovery returned 200; anonymous protected calls returned 401; malformed auth/AI inputs returned 400.
- Traversal probes: **3/3 returned 404** without exposing a secret field.
- CORS probe: no `Access-Control-Allow-Origin` or credential header is returned for an arbitrary external origin after the fix.
- Forced AI exception probe: all 3 endpoints returned generic 500 responses without the injected diagnostic string; all 3 failures were recorded in backend logs.
- Local server log review: the requested pages and API probes produced expected access-log statuses; no unexpected server exception appeared in that run.

The test suite emits dependency/runtime warnings from SpeechRecognition, NumPy/joblib, and loky. They do not fail the suite.

## File-by-file status

The percentage is an estimate of how much of the file's relevant behavior was exercised by the checks available here. It is **not** a line-coverage or production reliability score. External-service workflows and real browser interaction are excluded where noted.

| File or area | Estimated working / tested | Result and observations |
| --- | ---: | --- |
| `backend/app.py` | 95% | Real local HTTP startup, page serving, API registration, asset delivery, and arbitrary-origin CORS behavior checked. Debug mode is off by default. |
| `run.py` | 100% | Started the app from the project root; server reported debug mode off and served requests. |
| `backend/config.py` | 75% | Configuration loaded from the local backend environment and app startup succeeded. Production secret rotation/deployment settings were not audited. |
| `backend/routes/auth_routes.py` | 55% | Empty registration/login and malformed OTP requests returned 400. Full registration, OTP delivery/verification, successful login, logout, and session rotation need live Supabase and EmailJS. |
| `backend/routes/artisan_routes.py` | 50% | Anonymous dashboard/products/orders access returned 401; image/product workflows and ownership checks need a configured database and Storage bucket. |
| `backend/routes/enquiry_routes.py` | 50% | Anonymous access returned 401. Conversation persistence, role ownership, and message/status transitions need live Supabase records. |
| `backend/routes/orders_routes.py` | 55% | Anonymous order listing and checkout were rejected with 401. Checkout RPC, order creation, and tracking need live Supabase data and the database function. |
| `backend/routes/catalogue_routes.py` | 45% | Route registration and page/API wiring reviewed; product filtering and returned records require live Supabase data. |
| `backend/routes/ai_routes.py` | 90% | Health/service discovery, malformed requests, empty/invalid pipeline selection, generic failures, and log behavior exercised. Successful real model API calls were not exhaustively sent over HTTP. |
| `backend/ai/` and `ai/` | 85% | Existing suite passed; this does not measure model accuracy or validate every module with real-world data. |
| `backend/services/` | 45% | Product AI behavior is covered indirectly by the passing suite; external email delivery and transactional behavior were not exercised. |
| `frontend/index.html`, `login.html`, `register.html`, `verify-email.html`, artisan and buyer pages | 75% | All named pages served; local assets and 33 local navigation links resolved. No visual layout, responsive breakpoint, keyboard, or screen-reader interaction could be driven in this session. |
| `frontend/js/auth.js` | 65% | Syntax checked and API URL corrected to same origin; browser form submission and session-cookie transitions need interactive browser plus backend services. |
| `frontend/js/buyer/buyer.js` | 65% | Syntax checked, same-origin API URL corrected, and page assets load; buyer account/catalogue/order UI flows require interactive browser and Supabase. |
| `frontend/js/artisan/artisan-dashboard.js` | 65% | Syntax checked and same-origin API URL corrected; dashboard/product/enquiry interactions require browser and Supabase. |
| `frontend/js/artisan/artisan-ai-tools.js` | 70% | Syntax checked, same-origin URL default added; full prediction UX is not equivalent to the AI model unit/integration suite. |
| Remaining frontend JS (`api.js`, `app.js`, `i18n.js`) | 75% | Syntax checked; shared API paths and local page references resolve. Browser runtime behavior was not click-tested. |
| `database/schema.sql`, `database/seed.py` | 0% | Both are empty. The database contract is not represented in the repository, preventing local schema/RPC validation. |

## Bugs found and fixed

| Severity | Finding | Fix |
| --- | --- | --- |
| High | Credentialed CORS reflected arbitrary origins, including an attacker-controlled origin. | Removed global CORS handling. The frontend uses same-origin requests, so cross-origin credential access is not needed. |
| High | Several frontend clients hard-coded `http://127.0.0.1:5000`, breaking deployed or non-local access. | Changed clients to build API URLs from `window.location.origin`. |
| Medium | Landing page linked to `/frontend/login.html` and `/frontend/register.html`, and buyer hero image used a `/frontend/` prefix; these paths returned 404. | Corrected links to `/login` and `/register` and the image URL to `/assets/images/hero-crafts.jpg`. |
| Medium | Login/register referenced missing `login.js`, `service-worker.js`, PWA manifest, and icon assets. | Removed nonexistent references and the no-op service-worker registration block; fixed the registration auth script path. |
| Medium | Empty or malformed AI pipeline selection could return success with no predictions. | Added non-empty module list, unique module, and per-module JSON-object validation. Invalid requests now return 400. |
| Medium | AI 500 responses included raw exception details. | Server logs retain exception details; API callers receive generic errors. |
| Medium | Product publish endpoints previously disagreed on stock and timestamp handling. | Both paths now require stock; publish sets a timestamp and unpublish clears it. |
| Low | OCR/voice tests used the wrong project root and wrote test artifacts outside the workspace. | Corrected repository root resolution and moved save/load artifacts into temporary directories. |
| Low | Root `run.py` was empty; Flask debug mode was hard-coded on. | Added the root launcher and made debug mode opt-in with `FLASK_DEBUG` defaulting to false. |
| Low | Product AI output generated a naive UTC timestamp. | Changed it to timezone-aware UTC ISO output. |

## Security assessment

**Passed locally:** anonymous access to artisan, enquiry, and buyer order routes was rejected; path traversal probes did not escape the frontend root; arbitrary-origin credentialed CORS was removed; AI failure responses no longer expose injected exception text; Flask debug mode defaults off; session cookie configuration includes HttpOnly and SameSite=Lax.

**Follow-up risks:**

- Login attempts are not rate-limited in the current route implementation. OTP attempt and resend controls exist, but account-level throttling was not stress-tested.
- `SESSION_COOKIE_SECURE` defaults to false for local HTTP use. Set it to true behind HTTPS in production.
- No CSRF token mechanism was found. SameSite=Lax offers some mitigation, but state-changing cookie-authenticated endpoints should receive a deployment-specific CSRF review, especially for same-site sibling origins.
- No deployed Supabase RLS policy, schema constraints, order RPC, or Storage access policy could be checked from this repository because its schema and seed files are empty.

## Coverage limits

No Windows browser-control capability was available, so I did not perform visual or interactive browser testing. Page responses, assets, and links were checked over HTTP, but the assessment does not include screenshots, click-through workflows, layout at mobile widths, or accessibility tooling. Live Supabase and EmailJS calls were not used; successful account creation, OTP delivery, product persistence, checkout, and order tracking remain unverified. The QA percentages above reflect these limits.

