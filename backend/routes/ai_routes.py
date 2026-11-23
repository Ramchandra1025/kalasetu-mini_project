"""
KalaSetu AI API routes.
"""

import logging

from flask import (
    Blueprint,
    jsonify,
    request,
)

from backend.ai.base_service import (
    AIInputError,
    AIModelNotAvailableError,
)

from backend.ai.pipeline import (
    ProductIntelligencePipeline,
)

from backend.ai.registry import (
    ai_registry,
)


ai_bp = Blueprint(
    "ai",
    __name__,
    url_prefix="/api/ai",
)


pipeline = ProductIntelligencePipeline()


@ai_bp.get("/health")
def ai_health():

    return jsonify(
        {
            "success": True,
            "services": ai_registry.health(),
        }
    )


@ai_bp.get("/services")
def list_ai_services():

    return jsonify(
        {
            "success": True,
            "services": (
                ai_registry.list_services()
            ),
        }
    )


@ai_bp.post("/dpp")
def generate_dpp():

    try:

        data = request.get_json(
            silent=True
        )

        if data is None:
            raise AIInputError(
                "Request body must contain JSON."
            )

        result = pipeline.run_dpp(
            data
        )

        return jsonify(result), 200

    except AIInputError as exc:

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400

    except AIModelNotAvailableError as exc:

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 503

    except Exception as exc:
        logging.exception("Digital product passport prediction failed")

        return jsonify(
            {
                "success": False,
                "error": (
                    "AI service failed."
                ),
            }
        ), 500


@ai_bp.post("/pricing")
def predict_pricing():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            raise AIInputError(
                "Request body must be a JSON object."
            )

        result = pipeline.run_module("pricing", data)
        return jsonify(result), 200

    except AIInputError as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    except AIModelNotAvailableError as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 503

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    except Exception as exc:
        logging.exception("Pricing prediction failed")
        return jsonify({
            "success": False,
            "error": "Pricing prediction failed.",
        }), 500

@ai_bp.post("/pipeline")
def run_pipeline():

    try:

        data = request.get_json(
            silent=True
        )

        if not isinstance(data, dict):
            raise AIInputError(
                "Request body must be a JSON object."
            )

        modules = data.pop(
            "modules",
            None,
        )

        if modules is None:
            modules = list(data)

        if (
            not isinstance(modules, list)
            or not modules
            or any(not isinstance(name, str) or not name for name in modules)
        ):
            raise AIInputError(
                "Provide a non-empty list of AI modules and their input objects."
            )

        if len(set(modules)) != len(modules):
            raise AIInputError("Duplicate AI modules are not allowed.")

        if any(not isinstance(data.get(name), dict) for name in modules):
            raise AIInputError(
                "Each requested AI module needs a JSON input object."
            )

        result = pipeline.run(
          module_inputs=data,
          modules=modules,
        )

        return jsonify(result), 200

    except AIInputError as exc:

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400

    except AIModelNotAvailableError as exc:

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 503

    except KeyError as exc:

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400

    except Exception as exc:
        logging.exception("AI pipeline failed")

        return jsonify(
            {
                "success": False,
                "error": (
                    "AI pipeline failed."
                ),
            }
        ), 500
