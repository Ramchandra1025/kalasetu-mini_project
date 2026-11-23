"""
KalaSetu Unified AI Product Intelligence Pipeline.
"""

from typing import Any, Dict, Optional

from .registry import ai_registry


class ProductIntelligencePipeline:

    def __init__(
        self,
        registry=None,
    ):

        self.registry = (
            registry
            if registry is not None
            else ai_registry
        )

    def run_module(
        self,
        module_name: str,
        data: Dict[str, Any],
    ):

        service = self.registry.get(
            module_name
        )

        return service.predict(
            data
        )

    def run_dpp(
        self,
        product: Dict[str, Any],
    ):

        return self.run_module(
            "digital_product_passport",
            product,
        )

    def run(
        self,
        module_inputs: Dict[str, Dict[str, Any]],
        modules: Optional[list] = None,
    ):

        if modules is None:

            modules = list(
                module_inputs.keys()
            )

        results = {}

        for module_name in modules:

            if module_name not in module_inputs:

                raise ValueError(
                    f"No input supplied for "
                    f"module '{module_name}'."
                )

            results[module_name] = (
                self.run_module(
                    module_name,
                    module_inputs[
                        module_name
                    ],
                )
            )

        return {
            "success": True,

            "pipeline":
                "KalaSetu Product Intelligence",

            "modules_requested":
                modules,

            "modules_completed":
                list(
                    results.keys()
                ),

            "results":
                results,
        }