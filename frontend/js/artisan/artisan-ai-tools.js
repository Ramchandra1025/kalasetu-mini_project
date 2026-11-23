
"use strict";

/*
 * KalaSetu Artisan AI Workbench
 * Uses the existing POST /api/ai/pipeline endpoint.
 * Results are model outputs, not guarantees of real-world accuracy.
 */

(() => {
  const API_BASE =
    (window.KALASETU_API_BASE || window.location.origin).replace(/\/+$/, "");

  const MODULES = {
    pricing: {
      title: "Pricing Assistant",
      description: "Estimate a product price from production and market inputs.",
      fields: [
        ["craft_category", "Craft category", "text", "Handicrafts"],
        ["material", "Primary material", "text", "Wood"],
        ["region", "Region", "text", "Karnataka"],
        ["size_cm", "Product size (cm)", "number", 20],
        ["production_hours", "Production hours", "number", 5],
        ["material_cost", "Material cost (â‚¹)", "number", 300],
        ["labor_cost", "Labour cost (â‚¹)", "number", 500],
        ["demand_score", "Demand score (0â€“1)", "number", 0.7],
        ["complexity_score", "Complexity score (0â€“1)", "number", 0.6]
      ]
    },

    demand: {
      title: "Demand Forecast",
      description: "Estimate demand using historical, seasonal and regional inputs.",
      fields: [
        ["product_category", "Product category", "text", "Handicrafts"],
        ["region", "Region", "text", "Karnataka"],
        ["month", "Month (1â€“12)", "number", 10],
        ["season", "Season", "text", "Festive"],
        ["historical_demand", "Historical demand", "number", 100],
        ["previous_demand", "Previous-period demand", "number", 90],
        ["price", "Product price (â‚¹)", "number", 1200],
        ["demand_growth", "Demand growth", "number", 0.1]
      ]
    },

    market: {
      title: "Market Intelligence",
      description: "Score an opportunity using the model's market indicators.",
      fields: [
        ["product_category", "Product category", "text", "Handicrafts"],
        ["region", "Target region", "text", "Karnataka"],
        ["demand_score", "Demand score (0â€“1)", "number", 0.7],
        ["price_opportunity", "Price opportunity (0â€“1)", "number", 0.6],
        ["market_growth", "Market growth", "number", 0.1],
        ["regional_fit", "Regional fit (0â€“1)", "number", 0.8],
        ["seasonality_score", "Seasonality score (0â€“1)", "number", 0.6],
        ["competition_score", "Competition score (0â€“1)", "number", 0.4]
      ]
    },

    recommendation: {
      title: "Buyer Matching",
      description: "Evaluate compatibility between a buyer profile and a product.",
      fields: [
        ["buyer_id", "Buyer ID", "text", "demo-buyer-001"],
        ["buyer_region", "Buyer region", "text", "Bengaluru"],
        ["preferred_category", "Preferred category", "text", "Handicrafts"],
        ["preferred_material", "Preferred material", "text", "Wood"],
        ["min_budget", "Minimum budget (â‚¹)", "number", 500],
        ["max_budget", "Maximum budget (â‚¹)", "number", 3000],
        ["previous_category", "Previous category", "text", "Handicrafts"],
        ["previous_material", "Previous material", "text", "Wood"],
        ["product_category", "Product category", "text", "Handicrafts"],
        ["product_material", "Product material", "text", "Wood"],
        ["product_price", "Product price (â‚¹)", "number", 1500],
        ["product_region", "Product region", "text", "Karnataka"],
        ["product_demand_score", "Product demand score", "number", 0.7]
      ]
    },

    inventory: {
      title: "Inventory Intelligence",
      description: "Estimate stock coverage, safety stock and reorder quantity.",
      fields: [
        ["product_category", "Product category", "text", "Handicrafts"],
        ["material", "Primary material", "text", "Wood"],
        ["region", "Region", "text", "Karnataka"],
        ["current_stock", "Current stock (units)", "number", 20],
        ["minimum_stock", "Minimum stock (units)", "number", 5],
        ["maximum_stock", "Maximum stock (units)", "number", 100],
        ["average_daily_sales", "Average daily sales", "number", 2],
        ["recent_daily_sales", "Recent daily sales", "number", 3],
        ["historical_demand", "Historical demand", "number", 60],
        ["demand_growth", "Demand growth", "number", 0.1],
        ["lead_time_days", "Supplier lead time (days)", "number", 7],
        ["unit_price", "Unit price (â‚¹)", "number", 800],
        ["days_since_last_order", "Days since last order", "number", 10],
        ["stockout_count", "Previous stockout count", "number", 1]
      ]
    },

    waste: {
      title: "Waste-to-Product",
      description: "Explore reuse possibilities from craft material waste.",
      fields: [
        ["craft_category", "Craft category", "text", "Woodcraft"],
        ["material", "Waste material", "text", "Wood"],
        ["waste_quantity_kg", "Waste quantity (kg)", "number", 5],
        ["condition_score", "Condition score (0â€“1)", "number", 0.8],
        ["reuse_compatibility", "Reuse compatibility (0â€“1)", "number", 0.7],
        ["demand_score", "Demand score (0â€“1)", "number", 0.6],
        ["processing_effort", "Processing effort (0â€“1)", "number", 0.3],
        ["disposal_cost", "Disposal cost (â‚¹)", "number", 100],
        ["expected_reuse_value", "Expected reuse value (â‚¹)", "number", 500]
      ]
    },

    sustainability: {
      title: "Sustainability Intelligence",
      description: "Estimate sustainability indicators and carbon impact.",
      fields: [
        ["product_id", "Product ID", "text", "demo-product-001"],
        ["product_category", "Product category", "text", "Handicrafts"],
        ["material", "Primary material", "text", "Wood"],
        ["material_weight_kg", "Material weight (kg)", "number", 2],
        ["production_energy_kwh", "Production energy (kWh)", "number", 1.5],
        ["waste_kg", "Production waste (kg)", "number", 0.2],
        ["packaging_type", "Packaging type", "text", "Recyclable cardboard"],
        ["transport_distance_km", "Transport distance (km)", "number", 100],
        ["recyclability", "Recyclability", "text", "high"],
        ["local_sourcing", "Locally sourced?", "text", "yes"]
      ]
    },

    digital_product_passport: {
      title: "Digital Product Passport",
      description: "Generate the existing prototype passport and inspect its verification status.",
      fields: [
        ["product_id", "Product ID", "text", "demo-product-001"],
        ["product_name", "Product name", "text", "Handcrafted wooden bowl"],
        ["artisan_id", "Artisan ID", "text", "demo-artisan-001"],
        ["artisan_name", "Artisan name", "text", "Demo Artisan"],
        ["craft_category", "Craft category", "text", "Woodcraft"],
        ["material", "Primary material", "text", "Wood"],
        ["origin_state", "Origin state", "text", "Karnataka"],
        ["origin_district", "Origin district", "text", "Bagalkot"],
        ["production_method", "Production method", "text", "Handcrafted"],
        ["material_source", "Material source", "text", "Local supplier"],
        ["sustainability_score", "Sustainability score", "number", 75],
        ["carbon_impact_kg_co2e", "Carbon impact (kg COâ‚‚e)", "number", 1.2]
      ]
    }
  };

  const EXAMPLE_KEYS = new Set(
    Object.keys(MODULES)
  );

  let root;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function escapeText(value) {
    return String(value ?? "");
  }

  function createField(moduleName, field) {
    const [key, labelText, type, defaultValue] = field;
    const wrapper = element("label", "ks-ai-field");
    wrapper.appendChild(element("span", "", labelText));

    const input = element("input");
    input.name = key;
    input.type = type === "number" ? "number" : "text";
    input.value = String(defaultValue ?? "");
    input.required = !["disposal_cost", "expected_reuse_value"].includes(key);

    if (type === "number") {
      input.step = "any";
    }

    input.autocomplete = "off";
    wrapper.appendChild(input);
    return wrapper;
  }

  function createModuleCard(moduleName, config) {
    const card = element("section", "ks-ai-card");
    card.dataset.module = moduleName;

    const header = element("div", "ks-ai-card-header");
    header.appendChild(element("h3", "", config.title));
    header.appendChild(element("p", "", config.description));
    card.appendChild(header);

    const form = element("form", "ks-ai-form");
    form.dataset.module = moduleName;

    const fields = element("div", "ks-ai-fields");
    config.fields.forEach(field => fields.appendChild(createField(moduleName, field)));
    form.appendChild(fields);

    const actions = element("div", "ks-ai-actions");
    const submit = element("button", "ks-ai-run", "Run analysis");
    submit.type = "submit";
    actions.appendChild(submit);
    form.appendChild(actions);

    const status = element("p", "ks-ai-status", "Example inputs are provided. Replace them with your product's actual data.");
    status.setAttribute("aria-live", "polite");
    form.appendChild(status);

    const output = element("div", "ks-ai-output");
    output.hidden = true;
    output.setAttribute("aria-live", "polite");
    form.appendChild(output);

    form.addEventListener("submit", event => {
      event.preventDefault();
      runModule(moduleName, form, submit, status, output);
    });

    card.appendChild(form);
    return card;
  }

  function installStyles() {
    if (document.getElementById("ks-ai-workbench-styles")) return;

    const style = element("style");
    style.id = "ks-ai-workbench-styles";
    style.textContent = `
      #ksAiWorkbench { margin: 24px 0; color: var(--text, #24332d); }
      .ks-ai-intro { margin: 0 0 18px; padding: 16px; border: 1px solid var(--line, #e8e6dd); border-radius: 14px; background: var(--paper, #fffefa); }
      .ks-ai-intro h2 { margin: 0 0 8px; font-size: 1.25rem; }
      .ks-ai-intro p { margin: 6px 0; line-height: 1.55; color: var(--muted, #7c857e); }
      .ks-ai-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
      .ks-ai-card { min-width: 0; border: 1px solid var(--line, #e8e6dd); border-radius: 16px; padding: 18px; background: var(--paper, #fffefa); }
      .ks-ai-card-header h3 { margin: 0 0 6px; font-size: 1.05rem; }
      .ks-ai-card-header p { margin: 0 0 16px; color: var(--muted, #7c857e); line-height: 1.5; font-size: .92rem; }
      .ks-ai-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .ks-ai-field { display: flex; flex-direction: column; gap: 6px; min-width: 0; font-size: .86rem; }
      .ks-ai-field span { color: var(--text, #24332d); }
      .ks-ai-field input { width: 100%; min-width: 0; box-sizing: border-box; padding: 10px; border: 1px solid var(--line, #e8e6dd); border-radius: 8px; background: white; color: #24332d; font: inherit; }
      .ks-ai-actions { display: flex; gap: 10px; margin-top: 16px; }
      .ks-ai-run { border: 0; border-radius: 9px; padding: 11px 16px; background: var(--forest, #245447); color: white; cursor: pointer; font: inherit; font-weight: 600; }
      .ks-ai-run:disabled { opacity: .6; cursor: wait; }
      .ks-ai-status { margin: 12px 0 0; color: var(--muted, #7c857e); font-size: .85rem; line-height: 1.5; }
      .ks-ai-status[data-kind="error"] { color: #a33131; }
      .ks-ai-status[data-kind="success"] { color: #246246; }
      .ks-ai-output { margin-top: 14px; border-top: 1px solid var(--line, #e8e6dd); padding-top: 14px; }
      .ks-ai-output h4 { margin: 0 0 10px; }
      .ks-ai-output pre { white-space: pre-wrap; overflow-wrap: anywhere; max-height: 420px; overflow: auto; margin: 0; padding: 12px; border-radius: 9px; background: #f3f3ed; color: #26342e; font-size: .82rem; }
      .ks-ai-warning { margin-top: 10px; font-size: .82rem; color: #805c16; line-height: 1.5; }
      
      @media (max-width: 850px) { .ks-ai-grid { grid-template-columns: 1fr; } }
      @media (max-width: 480px) { .ks-ai-fields { grid-template-columns: 1fr; } .ks-ai-card { padding: 14px; } }
    .ks-ai-workspace {
  margin-top: 20px;
  scroll-margin-top: 24px;
}

.ks-ai-workspace > h3 {
  margin-bottom: 8px;
}

.ks-ai-active-card {
  max-width: 900px;
} `;
    
    document.head.appendChild(style);
  }

  
function findMountPoint() {
  const existing = document.getElementById("ksAiWorkbench");
  if (existing) return existing;

  const view = document.getElementById("view-ai-studio");
  if (!view) return null;

  const mount = element("div");
  mount.id = "ksAiWorkbench";

  const intro = element("div", "ks-ai-intro");
  intro.appendChild(element("h2", "", "AI Product Intelligence Workbench"));
  intro.appendChild(element(
    "p",
    "",
    "Choose a capability above to open its workspace. Example inputs are for testing, not live market data."
  ));
  intro.appendChild(element(
    "p",
    "",
    "Some services use experimental or synthetic data. Digital Product Passport output is a prototype and is not blockchain-backed."
  ));
  mount.appendChild(intro);

  const workspace = element("div", "ks-ai-workspace");
  workspace.id = "ksAiWorkspace";
  workspace.appendChild(element("h3", "", "Select an AI tool above"));
  workspace.appendChild(element(
    "p",
    "",
    "Click Open tool on a capability card to work with that service."
  ));
  mount.appendChild(workspace);

  view.appendChild(mount);

  return mount;
}


  function readForm(moduleName, form) {
    const config = MODULES[moduleName];
    const data = {};

    for (const [key, label, type] of config.fields) {
      const input = form.elements.namedItem(key);
      if (!input) continue;

      const raw = input.value.trim();
      if (input.required && raw === "") {
        throw new Error(`Please enter: ${label}`);
      }

      if (raw === "") continue;

      if (type === "number") {
        const number = Number(raw);
        if (!Number.isFinite(number)) {
          throw new Error(`${label} must be a valid number.`);
        }
        data[key] = number;
      } else {
        data[key] = raw;
      }
    }

    if (moduleName === "waste") {
      // These are optional fields in the service contract.
      if (!("disposal_cost" in data)) data.disposal_cost = 0;
      if (!("expected_reuse_value" in data)) data.expected_reuse_value = 0;
    }

    return data;
  }

  function showOutput(output, data) {
    output.replaceChildren();
    output.hidden = false;
    output.appendChild(element("h4", "", "Model response"));

    const pre = element("pre");
    pre.textContent = JSON.stringify(data, null, 2);
    output.appendChild(pre);

    const warning = element(
      "p",
      "ks-ai-warning",
      "Interpret this output as a model estimate. Confirm assumptions and data quality before using it for pricing, sourcing, buyer decisions, or sustainability claims."
    );
    output.appendChild(warning);
  }

  async function runModule(moduleName, form, button, status, output) {
    button.disabled = true;
    status.dataset.kind = "";
    status.textContent = "Running analysisâ€¦";
    output.hidden = true;

    try {
      const input = readForm(moduleName, form);

      const response = await fetch(`${API_BASE}/api/ai/pipeline`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({
          modules: [moduleName],
          [moduleName]: input
        })
      });

      let body;
      try {
        body = await response.json();
      } catch {
        throw new Error(`Server returned a non-JSON response (HTTP ${response.status}).`);
      }

      if (response.status === 401 || response.status === 403) {
        throw new Error(
          body.message ||
          "Your session may have expired or your account may not have permission to use this service. Sign in again."
        );
      }

      if (!response.ok) {
        throw new Error(
          body.message ||
          body.error ||
          `AI request failed (HTTP ${response.status}).`
        );
      }

      if (body.success !== true) {
        throw new Error(body.message || body.error || "The AI pipeline did not report success.");
      }

      const moduleResult = body.results?.[moduleName];
      if (!moduleResult) {
        throw new Error(`The pipeline response did not contain results for "${moduleName}".`);
      }

      if (moduleResult.success === false) {
        throw new Error(moduleResult.message || moduleResult.error || "The AI service failed.");
      }

      showOutput(output, moduleResult);
      status.dataset.kind = "success";
      status.textContent = `Completed: ${MODULES[moduleName].title}. Review the returned fields and any research warnings.`;
    } catch (error) {
      status.dataset.kind = "error";
      status.textContent = error?.message || "An unexpected error occurred.";
      output.hidden = true;
    } finally {
      button.disabled = false;
    }
  }

  

function openTool(moduleName) {
    const config = MODULES[moduleName];
    const workspace = document.getElementById("ksAiWorkspace");

    if (!config || !workspace) {
        console.error("AI tool or workspace not found:", moduleName);
        return;
    }

    workspace.replaceChildren();

    const heading = element("h3", "", config.title);
    const description = element("p", "", config.description);
    const card = createModuleCard(moduleName, config);

    workspace.appendChild(heading);
    workspace.appendChild(description);
    workspace.appendChild(card);

    workspace.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function init() {
    installStyles();

    const root = findMountPoint();

    if (!root) {
        console.error(
            "KalaSetu AI Studio view #view-ai-studio was not found."
        );
        return;
    }

    const workspace = document.getElementById("ksAiWorkspace");

    if (!workspace) {
        console.error("KalaSetu AI workspace was not created.");
        return;
    }

    const studio = document.getElementById("view-ai-studio");

    if (!studio || studio.dataset.aiWorkbenchBound === "true") {
        return;
    }

    // Frontend button ID -> registered backend module
    const toolMap = {
        pricing: "pricing",
        demand: "demand",
        market: "market",
        buyers: "recommendation",
        waste: "waste",
        inventory: "inventory",
        sustainability: "sustainability",
        dpp: "digital_product_passport"
    };

    const pendingTools = {
        vision: "Product vision & cataloguing",
        verification: "Craft verification",
        anomaly: "Scam & anomaly alerts",
        nlp: "Semantic craft search",
        ocr: "Text extraction (OCR)",
        voice: "Voice & language assistant",
        logistics: "Smart logistics",
        poster: "AI marketing poster"
    };

    studio.dataset.aiWorkbenchBound = "true";

    studio.addEventListener("click", function (event) {
        const button = event.target.closest("button[data-tool]");

        if (!button || !studio.contains(button)) {
            return;
        }

        const toolId = button.dataset.tool;

        if (Object.prototype.hasOwnProperty.call(toolMap, toolId)) {
            event.preventDefault();
            event.stopPropagation();

            openTool(toolMap[toolId]);
            return;
        }

        if (Object.prototype.hasOwnProperty.call(pendingTools, toolId)) {
            event.preventDefault();

            workspace.replaceChildren();

            workspace.appendChild(
                element("h3", "", pendingTools[toolId])
            );

            workspace.appendChild(
                element(
                    "p",
                    "",
                    "Integration pending. This capability is not yet connected to a working AI service."
                )
            );

            workspace.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

            return;
        }

        console.warn("Unknown KalaSetu AI tool ID:", toolId);
    });
}


  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

