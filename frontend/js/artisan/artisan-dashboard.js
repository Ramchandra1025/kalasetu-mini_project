
"use strict";

/* ============================================================
   KALASETU — ARTISAN STUDIO
   Live dashboard integration
   Authentication: Flask signed-cookie session
   Database: Supabase through the Flask backend
   ============================================================ */

const API_BASE = window.location.origin;

const API = {
  dashboard: "/api/artisan/dashboard",
  products: "/api/artisan/products",
  profile: "/api/artisan/profile",
  logout: "/api/auth/logout",
  enquiries: "/api/enquiries",
  orders: "/api/artisan/orders",
};

const STORAGE = {
  tasks: "kalasetu_artisan_tasks_v1"
};

/* ============================================================
   AI TOOL DIRECTORY
   These cards describe capabilities. They do not imply that
   every model is connected or production-ready.
   ============================================================ */

const aiTools = [
  {
    id: "vision",
    name: "Product vision & cataloguing",
    icon: "scan-search",
    description: "Analyse product imagery and prepare product listings.",
    status: "Integration pending"
  },
  {
    id: "verification",
    name: "Craft verification",
    icon: "badge-check",
    description: "Compare craft evidence and provide similarity-based guidance.",
    status: "Integration pending"
  },

{
  id: "pricing",
  name: "Fair pricing assistant",
  icon: "indian-rupee",
  description: "Estimate pricing guidance using product and cost information.",
  status: "Experimental model connected"
},

  {
    id: "demand",
    name: "Demand prediction",
    icon: "trending-up",
    description: "Explore demand estimates with relevant data and time horizons.",
    status: "Integration pending"
  },
  {
    id: "market",
    name: "Market opportunity analysis",
    icon: "compass",
    description: "Explore market opportunities and their recommendation factors.",
    status: "Integration pending"
  },
  {
    id: "buyers",
    name: "Buyer matching",
    icon: "users-round",
    description: "Compare product attributes with buyer requirements.",
    status: "Integration pending"
  },
  {
    id: "waste",
    name: "Waste intelligence",
    icon: "recycle",
    description: "Explore practical ways to reuse leftover craft materials.",
    status: "Integration pending"
  },
  {
    id: "anomaly",
    name: "Scam & anomaly alerts",
    icon: "shield-alert",
    description: "Flag unusual activity for further review.",
    status: "Integration pending"
  },
  {
    id: "nlp",
    name: "Semantic craft search",
    icon: "search-code",
    description: "Support meaning-aware search and related-product discovery.",
    status: "Integration pending"
  },
  {
    id: "ocr",
    name: "Text extraction (OCR)",
    icon: "scan-text",
    description: "Extract text from supported images and documents.",
    status: "Integration pending"
  },
  {
    id: "voice",
    name: "Voice & language assistant",
    icon: "languages",
    description: "Support available language and voice workflows.",
    status: "Integration pending"
  },
  {
    id: "inventory",
    name: "Inventory intelligence",
    icon: "boxes",
    description: "Interpret stock and material records when available.",
    status: "Integration pending"
  },
  {
    id: "logistics",
    name: "Smart logistics",
    icon: "truck",
    description: "Explore fulfilment planning using delivery information.",
    status: "Integration pending"
  },
  {
    id: "sustainability",
    name: "Sustainability intelligence",
    icon: "leaf",
    description: "Review sustainability indicators and their assumptions.",
    status: "Integration pending"
  },
  {
    id: "dpp",
    name: "Digital product passport",
    icon: "fingerprint",
    description: "Organise product identity and provenance information.",
    status: "Integration pending"
  },
  {
    id: "poster",
    name: "AI marketing poster",
    icon: "image-plus",
    description: "Prepare promotional content for product campaigns.",
    status: "Generator integration pending"
  }
];

/* ============================================================
   STATE
   ============================================================ */

let products = [];
let account = null;
let profile = null;
let dashboardStats = {};
let tasks = [false, false, false];
let dashboardLoading = false;
let enquiries = [];
let enquiriesLoading = false;
let artisanOrders = [];
let ordersLoading = false;

const $ = (selector, root = document) =>
  root.querySelector(selector);

const $$ = (selector, root = document) =>
  [...root.querySelectorAll(selector)];

/* ============================================================
   SAFE HELPERS
   ============================================================ */

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[character]);
}

function safeImage(value) {
  if (!value) return "";

  try {
    const url = new URL(value, window.location.origin);

    if (!["https:", "http:"].includes(url.protocol)) {
      return "";
    }

    return url.href;
  } catch {
    return "";
  }
}

function readJSON(key, fallback) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

function saveJSON(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    toast("Could not save this setting in your browser.", "alert-circle");
    return false;
  }
}

function formatINR(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) return "—";

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2
  }).format(number);
}

function icon(name, className = "") {
  return `<i data-lucide="${escapeHTML(name)}" class="${escapeHTML(className)}"></i>`;
}

function refreshIcons() {
  if (window.lucide?.createIcons) {
    window.lucide.createIcons();
  }
}

function toast(message, iconName = "check-circle-2") {
  const container = $("#toastContainer");

  if (!container) {
    console.info(message);
    return;
  }

  const item = document.createElement("div");
  item.className = "toast";

  item.innerHTML = `
    ${icon(iconName)}
    <span>${escapeHTML(message)}</span>
  `;

  container.appendChild(item);
  refreshIcons();

  window.setTimeout(() => item.remove(), 4000);
}

/* ============================================================
   API CLIENT
   Uses the existing Flask session cookie.
   No JWT or Supabase service key is stored in the browser.
   ============================================================ */

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});

  const isFormData = options.body instanceof FormData;

  if (
    options.body &&
    !isFormData &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include"
  });

  const contentType = response.headers.get("content-type") || "";

  let data = null;

  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    const text = await response.text();

    if (text) {
      data = { message: text };
    }
  }

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Your session has expired. Please log in again.");
    }

    throw new Error(
      data?.message || `Server request failed (${response.status}).`
    );
  }

  return data;
}

/* ============================================================
   NORMALISE DATABASE PRODUCT RECORDS
   ============================================================ */

function normaliseProduct(item, index = 0) {
  const price = Number(item.base_price ?? 0);
  const quantity = Number(item.stock_quantity ?? 0);

  return {
    id: String(item.id ?? `product-${index}`),
    name: String(item.name ?? "Untitled product"),
    category: String(item.craft_category ?? "Uncategorised"),
    price: Number.isFinite(price) ? price : 0,
    quantity: Number.isFinite(quantity) ? quantity : 0,
    status: String(
  item.publication_status ?? "draft"
).toLowerCase(),
    materials: String(item.material ?? ""),
    description: String(item.description ?? ""),
    image: safeImage(item.image_url ?? ""),
    createdAt: item.created_at ?? null
  };
}
async function toggleProductPublication(productId, nextStatus) {
  const product = products.find(
    item => String(item.id) === String(productId)
  );

  if (!product) {
    toast("Product not found. Refresh and try again.", "alert-circle");
    return;
  }

  if (!["published", "draft"].includes(nextStatus)) {
    toast("Invalid publication status.", "alert-circle");
    return;
  }

  if (nextStatus === "published" && product.quantity <= 0) {
    toast("Add available stock before publishing.", "alert-circle");
    return;
  }

  const confirmed = window.confirm(
    nextStatus === "published"
      ? `Publish "${product.name}" to the buyer catalogue?`
      : `Remove "${product.name}" from the buyer catalogue?`
  );

  if (!confirmed) return;

  const button = $(
    `[data-toggle-publish="${CSS.escape(String(productId))}"]`
  );

  if (button) {
    button.disabled = true;
    button.textContent =
      nextStatus === "published" ? "Publishing..." : "Unpublishing...";
  }

  try {
    const response = await apiFetch(
      `${API.products}/${encodeURIComponent(productId)}/publish`,
      {
        method: "POST",
        body: JSON.stringify({
          publication_status: nextStatus
        })
      }
    );

    if (response?.success !== true) {
      throw new Error(
        response?.message || "Could not update publication status."
      );
    }

    await loadBackendData();

    toast(
      nextStatus === "published"
        ? "Product published successfully."
        : "Product moved back to draft.",
      "check-circle-2"
    );
  } catch (error) {
    console.error("Product publication failed:", error);
    toast(
      error.message || "Could not update publication status.",
      "alert-circle"
    );

    await loadBackendData();
  }
}


/* ============================================================
   PRODUCT RENDERING
   ============================================================ */


function renderProductCard(product) {
  const image = safeImage(product.image);
  const isPublished = product.status === "published";
  const isArchived = product.status === "archived";

  const statusClass = isPublished
    ? "published"
    : isArchived
      ? "archived"
      : "draft";

  const statusLabel = isPublished
    ? "Published"
    : isArchived
      ? "Archived"
      : "Draft";

  return `
    <article class="product-card">
      <div class="product-image">
        ${
          image
            ? `
              <img
                src="${escapeHTML(image)}"
                alt="${escapeHTML(product.name)}"
                loading="lazy"
              />
            `
            : `
              <div class="empty-state">
                ${icon("image")}
                <p>No product photo</p>
              </div>
            `
        }

        <span class="product-status ${statusClass}">
          ${statusLabel}
        </span>
      </div>

      <div class="product-body">
        <span class="product-category">
          ${escapeHTML(product.category)}
        </span>

        <h3 class="product-name">
          ${escapeHTML(product.name)}
        </h3>

        <div class="product-meta">
          <strong class="product-price">
            ${escapeHTML(formatINR(product.price))}
          </strong>

          <span class="product-stock">
            ${product.quantity} in stock
          </span>
        </div>

        <div class="product-footer">
          <button
            type="button"
            data-edit-product="${escapeHTML(product.id)}"
          >
            ${icon("pencil")} Edit
          </button>

          <button
            type="button"
            data-view-product="${escapeHTML(product.id)}"
          >
            ${icon("arrow-up-right")} Details
          </button>

          <button
            type="button"
            data-toggle-publish="${escapeHTML(product.id)}"
            data-next-status="${isPublished ? "draft" : "published"}"
            ${product.quantity <= 0 && !isPublished ? "disabled" : ""}
          >
            ${
              isPublished
                ? `${icon("eye-off")} Unpublish`
                : `${icon("globe")} Publish`
            }
          </button>
        </div>
      </div>
    </article>
  `;
}


function renderRecentProducts() {
  const root = $("#recentProducts");
  if (!root) return;

  if (dashboardLoading && !products.length) {
    root.innerHTML = `
      <div class="empty-state">
        ${icon("loader-circle")}
        <p>Loading your products...</p>
      </div>
    `;
  } else if (!products.length) {
    root.innerHTML = `
      <div class="empty-state">
        ${icon("package-open")}
        <p>Your catalogue is empty. Add your first product to get started.</p>
      </div>
    `;
  } else {
    root.innerHTML = products
      .slice(0, 3)
      .map(renderProductCard)
      .join("");
  }

  refreshIcons();
}

function renderAllProducts() {
  const root = $("#allProducts");
  const empty = $("#productEmpty");

  if (!root) return;

  const query = ($("#productSearch")?.value || "")
    .trim()
    .toLowerCase();

  const status = $("#productStatusFilter")?.value || "all";
  const sort = $("#productSort")?.value || "recent";

  let filtered = products.filter(product => {
    const searchText = [
      product.name,
      product.category,
      product.materials,
      product.description
    ].join(" ").toLowerCase();

    const matchesQuery = searchText.includes(query);

    const matchesStatus =
      status === "all" ||
      product.status === status;

    return matchesQuery && matchesStatus;
  });

  if (sort === "name") {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  }

  if (sort === "price") {
    filtered.sort((a, b) => a.price - b.price);
  }

  if (sort === "recent") {
    filtered.sort((a, b) => {
      const dateA = Date.parse(a.createdAt || "") || 0;
      const dateB = Date.parse(b.createdAt || "") || 0;

      return dateB - dateA;
    });
  }

  root.innerHTML = filtered.map(renderProductCard).join("");

  if (empty) {
    empty.classList.toggle("hidden", filtered.length > 0);
  }

  if (!filtered.length && empty) {
    empty.classList.remove("hidden");
  }

  refreshIcons();
}

/* ============================================================
   METRICS
   ============================================================ */

function renderMetrics(summary = dashboardStats) {
  const productCount =
    summary?.total_products ??
    summary?.product_count ??
    products.length;

  const enquiries =
    summary?.open_enquiries ?? "—";

  const orders =
    summary?.active_orders ??
    summary?.pending_orders ??
    "—";

  const opportunities =
    summary?.market_opportunities ?? "—";

  const metricProducts = $("#metricProducts");
  const metricEnquiries = $("#metricEnquiries");
  const metricOrders = $("#metricOrders");
  const metricOpportunities = $("#metricOpportunities");
  const navProductCount = $("#navProductCount");

  if (metricProducts) metricProducts.textContent = productCount;
  if (metricEnquiries) metricEnquiries.textContent = enquiries;
  if (metricOrders) metricOrders.textContent = orders;
  if (metricOpportunities) metricOpportunities.textContent = opportunities;

  if (navProductCount) {
    navProductCount.textContent = products.length;
  }

  const activity = $("#activityList");

  if (activity) {
    if (!products.length) {
      activity.innerHTML = `
        <div class="empty-state">
          ${icon("activity")}
          <p>Your product and order activity will appear here when records exist.</p>
        </div>
      `;
    } else {
      activity.innerHTML = `
        <div class="activity-row">
          <span class="activity-icon">${icon("package")}</span>
          <div>
            <strong>Product catalogue</strong>
            <p>${products.length} product record(s) loaded from your account.</p>
          </div>
        </div>
      `;
    }
  }

  refreshIcons();
}

/* ============================================================
   PROFILE UI
   ============================================================ */



function setProfileUI() {
  const name =
    profile?.name?.trim() ||
    account?.name?.trim() ||
    "Artisan";

  const craft =
    profile?.craft?.trim() ||
    profile?.primaryMaterial?.trim() ||
    "Complete your craft profile";

  const location = profile?.location?.trim() || "";
  const story = profile?.story?.trim() || "";

  // Existing sidebar and dashboard identity
  const sidebarName = $("#sidebarName");
  const sidebarShortName = $("#sidebarShortName");
  const sidebarCraft = $("#sidebarCraft");
  const welcomeTitle = $("#welcomeTitle");

  if (sidebarName) sidebarName.textContent = name;
  if (sidebarShortName) {
    sidebarShortName.textContent = name.split(/\s+/)[0];
  }
  if (sidebarCraft) sidebarCraft.textContent = craft;

  if (welcomeTitle) {
    welcomeTitle.replaceChildren();
    welcomeTitle.append(document.createTextNode(`Welcome, ${name} `));

    const wave = document.createElement("span");
    wave.className = "wave";
    wave.textContent = "✳";
    welcomeTitle.appendChild(wave);
  }

  // Fill the new profile editor fields
  const nameInput = $("#profileName");
  const craftInput = $("#profileSpecialisation");
  const locationInput = $("#profileLocation");
  const storyInput = $("#profileAbout");

  if (nameInput) nameInput.value = profile?.name || "";
  if (craftInput) craftInput.value = profile?.craft || "";
  if (locationInput) locationInput.value = location;
  if (storyInput) storyInput.value = story;

  // Update the profile banner
  const bannerName = $("#profileBannerName");
  const bannerCraft = $("#profileBannerCraft");
  const bannerLocation = $("#profileBannerLocation");

  if (bannerName) bannerName.textContent = name;
  if (bannerCraft) bannerCraft.textContent = craft;
  if (bannerLocation) {
    bannerLocation.textContent = location || "Location not added yet";
  }

  // Update the buyer-facing preview
  const previewInitial = $("#profilePreviewInitial");
  const previewName = $("#profilePreviewName");
  const previewMeta = $("#profilePreviewMeta");
  const previewAbout = $("#profilePreviewAbout");
  const craftTag = $("#profileCraftTag");
  const locationTag = $("#profileLocationTag");

  const initial = name.charAt(0).toUpperCase() || "A";

  if (previewInitial) previewInitial.textContent = initial;
  if (previewName) previewName.textContent = name;
  if (previewMeta) {
    previewMeta.textContent = [craft, location].filter(Boolean).join(" · ");
  }
  if (previewAbout) {
    previewAbout.textContent = story || "Your craft story will appear here.";
  }
  if (craftTag) craftTag.textContent = craft;
  if (locationTag) locationTag.textContent = location || "Location not added yet";

  // Preserve the existing avatar display
  $$(".avatar, .profile-large-avatar").forEach(element => {
    element.textContent = initial;
  });

  // Update character count if present
  const aboutCount = $("#profileAboutCount");
  if (aboutCount && storyInput) {
    aboutCount.textContent = String(storyInput.value.length);
  }
}



/* ============================================================
   DASHBOARD DATA LOADING
   ============================================================ */


async function loadBackendData() {
  if (dashboardLoading) return;

  dashboardLoading = true;
  renderRecentProducts();

  try {
    const dashboard = await apiFetch(API.dashboard);

    account = dashboard?.account || null;
    dashboardStats = dashboard?.stats || {};

    const serverProfile = dashboard?.profile || {};

    profile = {
      id: serverProfile.id || account?.id || null,
      name: serverProfile.full_name || account?.name || "",
      craft: serverProfile.craft_category || "",
      
location: [
  serverProfile.village,
  serverProfile.district,
  serverProfile.state
].filter(Boolean).join(", "),

      
story: serverProfile.craft_story || "",

      primaryMaterial: serverProfile.primary_material || "",
      preferredLanguage:
        serverProfile.preferred_language ||
        account?.preferred_language ||
        "English",
      onboardingCompleted: Boolean(
        serverProfile.onboarding_completed
      )
    };

    // Update identity as soon as the dashboard response arrives.
    setProfileUI();
    renderMetrics(dashboardStats);

    // Product loading is independent of the profile display.
    try {
      const productResponse = await apiFetch(API.products);

      const records = Array.isArray(productResponse?.products)
        ? productResponse.products
        : [];

      products = records.map(normaliseProduct);
    } catch (productError) {
      console.error("Product loading failed:", productError);
      products = [];

      toast(
        "Your profile loaded, but products could not be loaded.",
        "alert-circle"
      );
    }

    renderRecentProducts();
    renderAllProducts();
    renderMetrics(dashboardStats);

    console.info("KalaSetu dashboard loaded from the backend.");
  } catch (error) {
    console.error("Dashboard loading failed:", error);

    toast(
      error.message || "Could not load dashboard data.",
      "alert-circle"
    );

    if (error.message?.includes("session has expired")) {
      window.location.assign("/login.html");
    }
  } finally {
    dashboardLoading = false;
  }
}

async function loadEnquiries() {
  const root = $("#enquiriesList");

  enquiriesLoading = true;

  if (root) {
    root.innerHTML = `
      <div class="empty-state">
        ${icon("loader-circle")}
        <p>Loading buyer enquiries...</p>
      </div>
    `;
  }

  try {
    const response = await apiFetch(API.enquiries);

    enquiries = Array.isArray(response?.enquiries)
      ? response.enquiries
      : [];

    renderEnquiries();
  } catch (error) {
    console.error("Enquiries loading failed:", error);

    if (root) {
      root.innerHTML = `
        <div class="empty-state">
          ${icon("alert-circle")}
          <p>${escapeHTML(error.message || "Could not load enquiries.")}</p>
          <button type="button" id="retryEnquiries">
            Try again
          </button>
        </div>
      `;
    }

    refreshIcons();
  } finally {
    enquiriesLoading = false;
  }
}

function renderEnquiries() {
  const root = $("#enquiriesList");
  if (!root) return;

  if (!enquiries.length) {
    root.innerHTML = `
      <div class="empty-state">
        ${icon("messages-square")}
        <h3>No enquiries yet</h3>
        <p>Buyer messages will appear here when someone enquires about your products.</p>
      </div>
    `;

    refreshIcons();
    return;
  }

  root.innerHTML = enquiries.map(enquiry => `
    <article class="enquiry-card">
      <div class="enquiry-card-header">
        <div>
          <h3>${escapeHTML(enquiry.subject || "Product enquiry")}</h3>
          <p>${escapeHTML(enquiry.buyer_name || "Buyer")}</p>
        </div>

        <span class="enquiry-status">
          ${escapeHTML(enquiry.status || "open")}
        </span>
      </div>

      <p>${escapeHTML(enquiry.message || "")}</p>

      <div class="enquiry-card-footer">
        <span>${escapeHTML(enquiry.product_name || "Product not specified")}</span>
        <span>${escapeHTML(enquiry.created_at || "")}</span>
      </div>
    </article>
  `).join("");

  refreshIcons();
}



/* ============================================================
   ARTISAN FULFILMENT ORDERS
   Loads real orders belonging to the signed-in artisan.
   ============================================================ */

async function loadArtisanOrders() {
  const root = $("#ordersList");
  if (!root || ordersLoading) return;

  ordersLoading = true;

  root.innerHTML = `
    <div class="empty-state">
      ${icon("loader-circle")}
      <p>Loading your orders...</p>
    </div>
  `;

  try {
    const response = await apiFetch(API.orders);

    if (response?.success !== true) {
      throw new Error(response?.message || "Could not load orders.");
    }

    artisanOrders = Array.isArray(response.orders)
      ? response.orders
      : [];

    renderArtisanOrders();
  } catch (error) {
    console.error("Artisan orders loading failed:", error);

    root.innerHTML = `
      <div class="empty-state">
        ${icon("alert-circle")}
        <h3>Unable to load orders</h3>
        <p>${escapeHTML(error.message || "Please try again.")}</p>
        <button type="button" id="retryArtisanOrders">
          Try again
        </button>
      </div>
    `;

    refreshIcons();
  } finally {
    ordersLoading = false;
  }
}

function renderArtisanOrders() {
  const root = $("#ordersList");
  if (!root) return;

  const normaliseStatus = status =>
    String(status || "pending").trim().toLowerCase();

  const pendingCount = artisanOrders.filter(order =>
    ["pending"].includes(normaliseStatus(order.status))
  ).length;

  const fulfilmentCount = artisanOrders.filter(order =>
    ["confirmed", "processing", "shipped", "in_fulfilment",
     "in fulfillment"].includes(normaliseStatus(order.status))
  ).length;

  const completedCount = artisanOrders.filter(order =>
    ["delivered", "completed"].includes(normaliseStatus(order.status))
  ).length;

  if ($("#orderTotal")) {
    $("#orderTotal").textContent = artisanOrders.length;
  }

  if ($("#orderPending")) {
    $("#orderPending").textContent = pendingCount;
  }

  if ($("#orderShipping")) {
    $("#orderShipping").textContent = fulfilmentCount;
  }

  if ($("#orderCompleted")) {
    $("#orderCompleted").textContent = completedCount;
  }

  const query = ($("#orderSearch")?.value || "")
    .trim()
    .toLowerCase();

  const statusFilter =
    $("#orderStatusFilter")?.value || "all";

  const filtered = artisanOrders.filter(order => {
    const product = products.find(
      item => String(item.id) === String(order.product_id)
    );

    const productName = product?.name || order.product_name || "";

    const searchText = [
      order.order_reference,
      order.id,
      order.buyer_name,
      order.buyer_phone,
      productName,
      order.status
    ].join(" ").toLowerCase();

    const matchesSearch = searchText.includes(query);
    const status = normaliseStatus(order.status);
    const matchesStatus =
      statusFilter === "all" || status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  if (!filtered.length) {
    root.innerHTML = `
      <div class="empty-state">
        ${icon("shopping-bag")}
        <h3>${artisanOrders.length ? "No matching orders" : "No orders yet"}</h3>
        <p>${
          artisanOrders.length
            ? "Try changing your search or status filter."
            : "Orders will appear here when buyers purchase your products."
        }</p>
      </div>
    `;

    refreshIcons();
    return;
  }

  root.innerHTML = filtered.map(order => {
    const product = products.find(
      item => String(item.id) === String(order.product_id)
    );

    const productName =
      product?.name || order.product_name || "Product details unavailable";

    const status = normaliseStatus(order.status);
    const statusLabel = status.replaceAll("_", " ");

    const address = order.delivery_address || {};
    const deliveryAddress = [
      address.address,
      address.city,
      address.state,
      address.pincode
    ].filter(Boolean).join(", ");

    const createdDate = order.created_at
      ? new Date(order.created_at).toLocaleString("en-IN")
      : "Date unavailable";

    return `
      <article class="enquiry-card artisan-order-card">
        <div class="enquiry-card-header">
          <div>
            <h3>${escapeHTML(order.order_reference || order.id)}</h3>
            <p>${escapeHTML(productName)}</p>
          </div>
          <span class="enquiry-status">
            ${escapeHTML(statusLabel)}
          </span>
        </div>

        <p><strong>Buyer:</strong>
          ${escapeHTML(order.buyer_name || "Not provided")}
        </p>

        <p><strong>Phone:</strong>
          ${escapeHTML(order.buyer_phone || "Not provided")}
        </p>

        <p><strong>Quantity:</strong>
          ${Number(order.quantity) || 0}
        </p>

        <p><strong>Order total:</strong>
          ${escapeHTML(formatINR(order.total_amount))}
        </p>

        <p><strong>Payment:</strong>
          ${escapeHTML(order.payment_status || "Unknown")}
        </p>

        <p><strong>Delivery address:</strong>
          ${escapeHTML(deliveryAddress || "Not provided")}
        </p>

        <div class="enquiry-card-footer">
          <span>${escapeHTML(createdDate)}</span>
        </div>
      </article>
    `;
  }).join("");

  refreshIcons();
}

/* ============================================================
   NAVIGATION
   ============================================================ */

function navigate(view) {
  const target = $(`#view-${CSS.escape(view)}`);
  if (!target) return;

  $$(".page-view").forEach(page => {
    page.classList.remove("active");
  });

  target.classList.add("active");

  $$(".nav-item[data-view]").forEach(button => {
    button.classList.toggle(
      "active",
      button.dataset.view === view
    );
  });

  const navButton = $(
    `.nav-item[data-view="${CSS.escape(view)}"]`
  );

  const breadcrumb = $("#breadcrumbCurrent");

  if (breadcrumb) {
    breadcrumb.textContent =
      navButton?.querySelector("span")?.textContent ||
      view.replaceAll("-", " ");
  }

  $("#sidebar")?.classList.remove("open");
  $("#sidebarScrim")?.classList.remove("open");

  window.scrollTo({ top: 0, behavior: "smooth" });

  if (view === "products") renderAllProducts();
  if (view === "products") {
  renderAllProducts();
}

if (view === "buyers") {
  loadEnquiries();
}

if (view === "orders") {
  loadArtisanOrders();
}
}

/* ============================================================
   PRODUCT MODAL
   ============================================================ */

function openProductModal() {
  const form = $("#productForm");
  const modal = $("#productModal");

  if (!form || !modal) {
    toast("The product form is unavailable.", "alert-circle");
    return;
  }

  form.reset();
  delete form.dataset.editId;

  const submitButton = form.querySelector('[type="submit"]');

  if (submitButton) {
    submitButton.innerHTML = `${icon("plus")} Save product`;
  }

  if (typeof modal.showModal === "function") {
    modal.showModal();
  } else {
    toast("Your browser does not support the product dialog.", "alert-circle");
  }

  refreshIcons();
}

function closeProductModal() {
  const modal = $("#productModal");

  if (modal?.open) modal.close();
}

/* ============================================================
   CREATE PRODUCT
   Current backend accepts product metadata without an image.
   Image storage has not been configured yet.
   ============================================================ */

/* ============================================================
   PRODUCT IMAGE AI ANALYSIS
   ============================================================ */

let productAiPrediction = null;
let productAiRequestId = 0;

function normalizeAiCategory(value) {
  const key = String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[\s&-]+/g, "_");

  const categories = {
    textiles_handloom: "Textiles & handloom",
    textile: "Textiles & handloom",
    textiles: "Textiles & handloom",
    handloom: "Textiles & handloom",
    pottery_ceramics: "Pottery & ceramics",
    pottery: "Pottery & ceramics",
    ceramics: "Pottery & ceramics",
    woodcraft: "Woodcraft",
    wood_craft: "Woodcraft",
    metalcraft: "Metal craft",
    metal_craft: "Metal craft",
    jewellery: "Jewellery",
    jewelry: "Jewellery",
    home_decor: "Home decor",
    other_handicrafts: "Other handicrafts",
  };

  return categories[key] || null;
}

async function handleProductImageChange(event) {
  const form = $("#productForm");
  const file = event.currentTarget.files?.[0];
  const panel = $("#productAiAnalysis");
  const status = $("#productAiStatus");
  const suggestions = $("#productAiSuggestions");
  const checkbox = form?.elements.namedItem("aiCatalogue");

  const requestId = ++productAiRequestId;
  productAiPrediction = null;

  if (suggestions) suggestions.hidden = true;
  if (panel) panel.hidden = true;

  if (!file) return;

  if (checkbox && !checkbox.checked) return;

  if (file.size > 5 * 1024 * 1024) {
    toast("Product images must be 5 MB or smaller.", "error");
    event.currentTarget.value = "";
    return;
  }

  const allowedTypes = [
    "image/jpeg",
    "image/png",
    "image/webp",
  ];

  if (!allowedTypes.includes(file.type)) {
    toast("Choose a JPG, PNG or WebP image.", "error");
    event.currentTarget.value = "";
    return;
  }

  if (panel) panel.hidden = false;
  if (status) status.textContent = "Analyzing product image…";

  try {
    const body = new FormData();
    body.append("image", file);

    const result = await apiFetch(
      "/api/artisan/products/analyze-image",
      {
        method: "POST",
        body,
      }
    );

    // Ignore stale results if the artisan selected another image.
    if (requestId !== productAiRequestId) return;

    if (!result?.success || !result.suggestions) {
      throw new Error(result?.message || "Image analysis failed.");
    }

    productAiPrediction = result.suggestions;

    const category = result.suggestions.category;
    const material = result.suggestions.material;
    const color = result.suggestions.color;

    const categoryLabel = category?.label || "Unavailable";
    const materialLabel = material?.label || "Unavailable";
    const colorLabel = color?.label || "Unavailable";

    const confidenceText = (prediction) => {
      const confidence = Number(prediction?.confidence);

      return Number.isFinite(confidence)
        ? ` (${(confidence * 100).toFixed(1)}% model confidence)`
        : "";
    };

    $("#productAiCategory").textContent =
      `Category: ${categoryLabel}${confidenceText(category)}`;

    $("#productAiMaterial").textContent =
      `Material: ${materialLabel}${confidenceText(material)}`;

    $("#productAiColor").textContent =
      `Color: ${colorLabel}${confidenceText(color)}`;

    $("#productAiWarning").textContent =
      "Experimental model: review these suggestions before saving.";

    if (status) {
      status.textContent =
        "Analysis complete. Review the suggestions below.";
    }

    if (suggestions) suggestions.hidden = false;
  } catch (error) {
    if (requestId !== productAiRequestId) return;

    console.error("Product image analysis failed:", error);

    if (status) {
      status.textContent =
        error.message || "AI analysis failed. You can enter details manually.";
    }
  }
}


function applyProductAiSuggestions() {
  if (!productAiPrediction) {
    toast("Analyze a product image first.", "alert-circle");
    return;
  }

  const form = $("#productForm");
  if (!form) return;

  const nameInput = form.elements.namedItem("name");
  const categorySelect = form.elements.namedItem("category");
  const materialInput = form.elements.namedItem("materials");
  const descriptionInput = form.elements.namedItem("description");

  const category = productAiPrediction.category?.label?.trim();
  const material = productAiPrediction.material?.label?.trim();
  const color = productAiPrediction.color?.label?.trim();

  // Apply category only when it maps to an existing dropdown option.
  const normalizedCategory = normalizeAiCategory(category);

  if (categorySelect && normalizedCategory) {
    const option = Array.from(categorySelect.options).find(
      item =>
        item.value.trim().toLowerCase() ===
          normalizedCategory.toLowerCase() ||
        item.textContent.trim().toLowerCase() ===
          normalizedCategory.toLowerCase()
    );

    if (option) categorySelect.value = option.value;
  }

  // Do not overwrite artisan-entered material details.
  if (materialInput && material && !materialInput.value.trim()) {
    materialInput.value = material;
  }

  // Add color to the material field only if it is not already present.
  if (materialInput && color) {
    const current = materialInput.value.trim();

    if (
      !current ||
      !current.toLowerCase().includes(color.toLowerCase())
    ) {
      materialInput.value = current
        ? `${current}, ${color} color`
        : `${color} color`;
    }
  }

  // Draft title: based only on the predicted category/material.
  // Keep existing artisan-entered text unchanged.
  if (nameInput && !nameInput.value.trim()) {
    const titleParts = [];

    if (material) {
      titleParts.push(
        material.charAt(0).toUpperCase() + material.slice(1)
      );
    }

    if (normalizedCategory) {
      titleParts.push(normalizedCategory);
    }

    if (titleParts.length) {
      nameInput.value = titleParts.join(" ");
    }
  }

  // Draft description: explicitly describe it as a draft for review.
  if (descriptionInput && !descriptionInput.value.trim()) {
    const details = [];

    if (category) details.push(`Craft category: ${category}`);
    if (material) details.push(`Suggested material: ${material}`);
    if (color) details.push(`Detected color: ${color}`);

    if (details.length) {
      descriptionInput.value =
        `${details.join(". ")}. ` +
        "Please review and edit these image-based suggestions " +
        "to accurately describe your handmade product.";
    }
  }

  toast(
    "Suggestions added where fields were empty. Review and edit before saving.",
    "success"
  );
}



async function handleProductSubmitWithEdit(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const submitButton = form.querySelector('[type="submit"]');
  const editId = form.dataset.editId || null;

  const formData = new FormData(form);
  const image = formData.get("image");

  if (image instanceof File && image.size > 5 * 1024 * 1024) {
    toast("Product images must be 5 MB or smaller.", "error");
    return;
  }

  const name = String(formData.get("name") || "").trim();
  const price = Number(formData.get("price"));
  const quantityRaw = String(formData.get("quantity") ?? "").trim();
  const quantity = Number(quantityRaw);

  if (!name) {
    toast("Enter a product name.", "error");
    return;
  }

  if (!Number.isFinite(price) || price <= 0) {
    toast("Enter a valid price greater than zero.", "error");
    return;
  }

  if (!/^\d+$/.test(quantityRaw) || !Number.isSafeInteger(quantity)) {
    toast("Quantity must be a whole number zero or greater.", "error");
    return;
  }

  if (image instanceof File && image.size === 0 && !image.name) {
    formData.delete("image");
  }

  const endpoint = editId
    ? `${API.products}/${encodeURIComponent(editId)}`
    : API.products;

  const method = editId ? "PUT" : "POST";
  const originalLabel = submitButton?.textContent;

  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = editId ? "Saving Changes..." : "Saving Product...";
  }

  try {
    const result = await apiFetch(endpoint, {
      method,
      body: formData
    });

    if (!result?.success || !result.product) {
      throw new Error(result?.message || "The product could not be saved.");
    }

    if (typeof productModal !== "undefined" && productModal?.open) {
      productModal.close();
    }

    form.reset();
    delete form.dataset.editId;

    await loadBackendData();

    toast(
      editId ? "Product updated successfully." : "Product added successfully.",
      "success"
    );
  } catch (error) {
    console.error("Product save failed:", error);
    toast(error.message || "Unable to save the product.", "error");
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent =
        originalLabel || (editId ? "Save Changes" : "Save Product");
    }
  }
}



/* ============================================================
   EDIT AND VIEW PRODUCT
   Existing-product editing is not implemented by the backend.
   ============================================================ */

function editProduct(id) {
  const product = products.find(
    (item) => String(item.id) === String(id)
  );

  if (!product) {
    toast("Product not found. Refresh and try again.", "alert-circle");
    return;
  }

  const form = document.getElementById("productForm");
  const modal = document.getElementById("productModal");

  if (!form || !modal) {
    toast("Product editor could not be opened.", "alert-circle");
    return;
  }

  form.reset();
  form.dataset.editId = String(product.id);

  form.elements.namedItem("name").value = product.name || "";
  form.elements.namedItem("category").value = product.category || "";
  form.elements.namedItem("price").value = product.price ?? "";
  form.elements.namedItem("quantity").value = product.quantity ?? 0;
  form.elements.namedItem("materials").value = product.materials || product.material || "";
  form.elements.namedItem("description").value = product.description || "";

  const submitButton = form.querySelector('[type="submit"]');
  if (submitButton) {
    submitButton.textContent = "Save Changes";
  }

  modal.showModal();
}

function showProductDetails(id) {
  const product = products.find(item => item.id === id);

  if (!product) return;

  toast(
    `${product.name} · ${product.category} · Stock: ${product.quantity}`,
    "package"
  );
}

/* ============================================================
   AI TOOL NAVIGATION
   Navigates to existing sections where possible.
   It does not fabricate AI results.
   ============================================================ */


function handleToolClick(id) {
  const tool = aiTools.find(item => item.id === id);
  if (!tool) return;

  const toolRoutes = {
    pricing: "pricing",
    demand: "markets",
    market: "markets",
    buyers: "buyers",
    inventory: "inventory",
    logistics: "inventory",
    waste: "sustainability",
    sustainability: "sustainability",
    dpp: "sustainability",
    vision: "products"
  };

  const route = toolRoutes[id];

  if (!route) {
    toast(
      `${tool.name} is not connected to an interactive workflow yet.`,
      "info"
    );
    return;
  }

  const target = document.getElementById(`view-${route}`);

  if (!target) {
    toast(
      `${tool.name}: the destination view is missing from the HTML.`,
      "alert-circle"
    );
    return;
  }

  navigate(route);

  if (id === "pricing") {
    toast(
      "Pricing assistant opened. Estimates are experimental.",
      "info"
    );
  } else {
    toast(
      `${tool.name}: open the section to review its available features.`,
      "info"
    );
  }
}

/* ============================================================
   AI TOOL CARDS
   ============================================================ */

function renderAiTools() {
  const root = $("#aiToolsGrid");
  if (!root) return;

  root.innerHTML = aiTools.map(tool => `
    <article class="ai-tool-card">
      <span class="ai-tool-icon">
        ${icon(tool.icon)}
      </span>

      <h3>${escapeHTML(tool.name)}</h3>

      <p>${escapeHTML(tool.description)}</p>

      <span class="tool-status">
        ${escapeHTML(tool.status)}
      </span>

      <button
        type="button"
        class="text-action"
        data-tool="${escapeHTML(tool.id)}"
      >
        Open tool ${icon("arrow-up-right")}
      </button>
    </article>
  `).join("");

  refreshIcons();
}

/* ============================================================
   ONBOARDING TASKS
   These checkboxes are browser-local UI preferences only.
   They do not represent completed server workflows.
   ============================================================ */

function renderTasks() {
  const root = $("#taskList");
  if (!root) return;

  const taskData = [
    [
      "Complete your craft profile",
      "Help buyers understand your craft and background."
    ],
    [
      "Review buyer enquiries",
      "Respond when enquiry functionality is available."
    ],
    [
      "Review your product details",
      "Keep product prices and stock information current."
    ]
  ];

  root.innerHTML = taskData.map((task, index) => `
    <label class="task-item">
      <input
        type="checkbox"
        data-task="${index}"
        ${tasks[index] ? "checked" : ""}
      />

      <span class="task-check">${icon("check")}</span>

      <span class="task-copy">
        <strong>${escapeHTML(task[0])}</strong>
        <small>${escapeHTML(task[1])}</small>
      </span>

      ${icon("chevron-right", "task-arrow")}
    </label>
  `).join("");

  const completed = tasks.filter(Boolean).length;
  const remaining = tasks.length - completed;

  if ($("#stepsCount")) {
    $("#stepsCount").textContent = `${remaining} remaining`;
  }

  if ($("#completionText")) {
    $("#completionText").textContent =
      `${completed} of ${tasks.length}`;
  }

  if ($("#completionBar")) {
    $("#completionBar").style.width =
      `${tasks.length ? completed / tasks.length * 100 : 0}%`;
  }

  refreshIcons();
}

/* ============================================================
   PROFILE SAVE
   Current backend supports full_name and craft_category here.
   Location/story are not claimed as saved by this handler.
   ============================================================ */



async function saveProfile() {
  const name = ($("#profileName")?.value || "").trim();
  const craft = ($("#profileSpecialisation")?.value || "").trim();
  const location = ($("#profileLocation")?.value || "").trim();
  const story = ($("#profileAbout")?.value || "").trim();

  if (!name) {
    toast("Please enter your name.", "alert-circle");
    return;
  }

  // The existing backend expects village, district and state.
  const locationParts = location.split(",").map(part => part.trim());

  const button = $("#saveArtisanProfile") || $("#saveProfile");
  if (button) {
    button.disabled = true;
  }

  try {
    const result = await apiFetch(API.profile, {
      method: "PUT",
      body: JSON.stringify({
        full_name: name,
        craft_category: craft,
        village: locationParts[0] || "",
        district: locationParts[1] || "",
        state: locationParts.slice(2).join(", "),
        craft_story: story
      })
    });

    if (result?.success === false) {
      throw new Error(result.message || "Profile update failed.");
    }

    await loadBackendData();
    toast("Your craft profile has been saved.");
  } catch (error) {
    console.error("Profile update failed:", error);
    toast(error.message || "Could not save your profile.", "alert-circle");
  } finally {
    if (button) button.disabled = false;
  }
}



function wireProfilePreview() {
  const nameInput = $("#profileName");
  const craftInput = $("#profileSpecialisation");
  const locationInput = $("#profileLocation");
  const storyInput = $("#profileAbout");

  const updatePreview = () => {
    const name = nameInput?.value.trim() || "Artisan";
    const craft = craftInput?.value.trim() || "Craft specialisation";
    const location = locationInput?.value.trim() || "Location not added yet";
    const story = storyInput?.value.trim() || "Your craft story will appear here.";
    const initial = name.charAt(0).toUpperCase() || "A";

    if ($("#profileBannerName")) $("#profileBannerName").textContent = name;
    if ($("#profileBannerCraft")) $("#profileBannerCraft").textContent = craft;
    if ($("#profileBannerLocation")) {
      $("#profileBannerLocation").textContent = location;
    }

    if ($("#profilePreviewInitial")) {
      $("#profilePreviewInitial").textContent = initial;
    }
    if ($("#profilePreviewName")) $("#profilePreviewName").textContent = name;
    if ($("#profilePreviewMeta")) {
      $("#profilePreviewMeta").textContent =
        [craft, locationInput?.value.trim()].filter(Boolean).join(" · ");
    }
    if ($("#profilePreviewAbout")) {
      $("#profilePreviewAbout").textContent = story;
    }
    if ($("#profileCraftTag")) $("#profileCraftTag").textContent = craft;
    if ($("#profileLocationTag")) {
      $("#profileLocationTag").textContent =
        locationInput?.value.trim() || "Location not added yet";
    }

    const count = $("#profileAboutCount");
    if (count && storyInput) {
      count.textContent = String(storyInput.value.length);
    }
  };

  [nameInput, craftInput, locationInput, storyInput].forEach(input => {
    input?.addEventListener("input", updatePreview);
  });

  updatePreview();
}


function initArtisanSettings() {
  const languageSelect = $("#workspaceLanguage");
  const saveLanguageButton = $("#saveLanguagePreference");
  const languageFeedback = $("#languageFeedback");

  const largerText = $("#largerTextPreference");
  const reduceMotion = $("#reduceMotionPreference");
  const saveAccessibilityButton = $("#saveAccessibility");
  const accessibilityFeedback = $("#accessibilityFeedback");

  const savedSettings = readJSON("kalasetu_artisan_settings_v1", {
    language: "English",
    largerText: false,
    reduceMotion: false
  });

  if (languageSelect) {
    languageSelect.value = savedSettings.language || "English";
  }

  if (largerText) largerText.checked = Boolean(savedSettings.largerText);
  if (reduceMotion) reduceMotion.checked = Boolean(savedSettings.reduceMotion);

  const applyAccessibility = () => {
    document.body.classList.toggle(
      "kalasetu-large-text",
      Boolean(largerText?.checked)
    );

    document.body.classList.toggle(
      "kalasetu-reduce-motion",
      Boolean(reduceMotion?.checked)
    );
  };

  applyAccessibility();

  saveLanguageButton?.addEventListener("click", () => {
    const current = readJSON("kalasetu_artisan_settings_v1", {});

    const success = saveJSON("kalasetu_artisan_settings_v1", {
      ...current,
      language: languageSelect?.value || "English"
    });

    if (languageFeedback) {
      languageFeedback.textContent = success
        ? "Language preference saved in this browser."
        : "Could not save the language preference.";
    }
  });

  saveAccessibilityButton?.addEventListener("click", () => {
    const current = readJSON("kalasetu_artisan_settings_v1", {});

    const success = saveJSON("kalasetu_artisan_settings_v1", {
      ...current,
      largerText: Boolean(largerText?.checked),
      reduceMotion: Boolean(reduceMotion?.checked)
    });

    applyAccessibility();

    if (accessibilityFeedback) {
      accessibilityFeedback.textContent = success
        ? "Accessibility preferences saved in this browser."
        : "Could not save accessibility preferences.";
    }
  });
}

function initLanguageSettings() {
  const select = $("#workspaceLanguage");
  const saveButton = $("#saveLanguagePreference");
  const feedback = $("#languageFeedback");
  const i18n = window.KalaSetuI18n;

  if (!select || !saveButton || !i18n) return;

  select.value = i18n.getLanguage();

  document.addEventListener("kalasetu:languageChanged", () => {
    select.value = i18n.getLanguage();
  });

  saveButton.addEventListener("click", () => {
    const saved = i18n.setLanguage(select.value);

    if (feedback) {
      feedback.textContent = saved
        ? i18n.get("common.languageSaved")
        : i18n.get("common.languageError");
    }

    refreshIcons();
  });
}
/* ============================================================
   EVENT WIRING
   ============================================================ */

function wireEvents() {
  $$(".nav-item[data-view]").forEach(button => {
    button.addEventListener("click", () => {
      navigate(button.dataset.view);
    });
  });

  $$("[data-go]").forEach(button => {
    button.addEventListener("click", () => {
      navigate(button.dataset.go);
    });
  });

  $$("[data-action='add-product']").forEach(button => {
    button.addEventListener("click", openProductModal);
  });

  $$("[data-close-modal]").forEach(button => {
    button.addEventListener("click", closeProductModal);
  });

  const productForm = $("#productForm");

  if (productForm) {
    productForm.addEventListener(
      "submit",
      handleProductSubmitWithEdit
    );
  }
   const productImageInput = $("#productImageInput");

productImageInput?.addEventListener(
  "change",
  handleProductImageChange
);

$("#applyProductAiSuggestions")?.addEventListener(
  "click",
  applyProductAiSuggestions
);

$("#productForm")?.elements
  .namedItem("aiCatalogue")
  ?.addEventListener("change", event => {
    if (!event.currentTarget.checked) {
      productAiRequestId++;
      productAiPrediction = null;

      const panel = $("#productAiAnalysis");
      if (panel) panel.hidden = true;
    } else if ($("#productImageInput")?.files?.[0]) {
      handleProductImageChange({
        currentTarget: $("#productImageInput"),
      });
    }
  });
  const productModal = $("#productModal");

  if (productModal) {
    productModal.addEventListener("close", () => {
      const form = $("#productForm");

      if (form) {
        delete form.dataset.editId;

        const submitButton = form.querySelector('[type="submit"]');

        if (submitButton) {
          submitButton.innerHTML = `${icon("plus")} Save product`;
        }
      }

      refreshIcons();
    });

    productModal.addEventListener("click", event => {
      if (event.target === productModal) {
        closeProductModal();
      }
    });
  }

  $("#menuToggle")?.addEventListener("click", () => {
    $("#sidebar")?.classList.toggle("open");
    $("#sidebarScrim")?.classList.toggle("open");
  });

  $("#sidebarScrim")?.addEventListener("click", () => {
    $("#sidebar")?.classList.remove("open");
    $("#sidebarScrim")?.classList.remove("open");
  });

  $("#productSearch")?.addEventListener("input", renderAllProducts);
  $("#productStatusFilter")?.addEventListener("change", renderAllProducts);
  $("#productSort")?.addEventListener("change", renderAllProducts);
   $("#refreshOrders")?.addEventListener("click", () => {
  loadArtisanOrders();
});

$("#orderSearch")?.addEventListener("input", renderArtisanOrders);

$("#orderStatusFilter")?.addEventListener("change", renderArtisanOrders);

document.addEventListener("click", event => {
  if (event.target.closest("#retryArtisanOrders")) {
    loadArtisanOrders();
  }
});
  $("#globalSearch")?.addEventListener("keydown", event => {
    if (event.key !== "Enter") return;

    const query = event.currentTarget.value.trim();
    if (!query) return;

    navigate("products");

    if ($("#productSearch")) {
      $("#productSearch").value = query;
    }

    renderAllProducts();
  });

  $("#taskList")?.addEventListener("change", event => {
    const input = event.target.closest("[data-task]");
    if (!input) return;

    const index = Number(input.dataset.task);

    if (index < 0 || index >= tasks.length) return;

    tasks[index] = input.checked;

    saveJSON(STORAGE.tasks, tasks);
    renderTasks();
  });

  document.addEventListener("click", event => {
    const target = event.target;

    if (!(target instanceof Element)) return;

    const editButton = target.closest("[data-edit-product]");

    if (editButton) {
      editProduct(editButton.dataset.editProduct);
      return;
    }

    const detailsButton = target.closest("[data-view-product]");

    if (detailsButton) {
      showProductDetails(detailsButton.dataset.viewProduct);
      return;
    }
     const publishButton = target.closest("[data-toggle-publish]");

if (publishButton) {
  toggleProductPublication(
    publishButton.dataset.togglePublish,
    publishButton.dataset.nextStatus
  );
  return;
}
    const toolButton = target.closest("[data-tool]");

    if (toolButton) {
      handleToolClick(toolButton.dataset.tool);
    }
  });

  wireProfilePreview();

($("#saveArtisanProfile") || $("#saveProfile"))
  ?.addEventListener("click", saveProfile);

  $("#notificationsButton")?.addEventListener("click", () => {
    toast(
      "Live notifications are not connected yet.",
      "bell"
    );
  });

  $("#profileMenu")?.addEventListener("click", () => {
    navigate("profile");
  });

  document.addEventListener("keydown", event => {
    const target = event.target;

    const isTyping =
      target instanceof HTMLInputElement ||
      target instanceof HTMLTextAreaElement ||
      target instanceof HTMLSelectElement ||
      target?.isContentEditable;

    if (event.key === "/" && !isTyping && $("#globalSearch")) {
      event.preventDefault();
      $("#globalSearch").focus();
    }

    if (event.key === "Escape") {
      $("#sidebar")?.classList.remove("open");
      $("#sidebarScrim")?.classList.remove("open");
    }
  });
  document.addEventListener("click", event => {
  if (event.target.closest("#retryEnquiries")) {
    loadEnquiries();
  }
});
}

/* ============================================================
   INITIALISATION
   ============================================================ */

async function initDashboard() {
  window.KalaSetuI18n?.init();
  tasks = readJSON(STORAGE.tasks, [false, false, false]);

  if (!Array.isArray(tasks) || tasks.length !== 3) {
    tasks = [false, false, false];
  }

  products = [];
  account = null;
  profile = {
    id: null,
    name: "",
    craft: "",
    location: "",
    story: "",
    primaryMaterial: ""
  };
  dashboardStats = {};

  renderRecentProducts();
  renderAllProducts();
  renderMetrics({});
  renderTasks();
  renderAiTools();
  initLanguageSettings();
  wireEvents();
  refreshIcons();
  initArtisanSettings();
  await loadBackendData();

  renderTasks();
  refreshIcons();
}

document.addEventListener("DOMContentLoaded", initDashboard);


/* ============================================================
   FAIR PRICING ASSISTANT
   Uses the registered backend PricingService.
   ============================================================ */

function initPricingAssistant() {
  const form = document.getElementById("pricingForm");
  const resultBox = document.getElementById("pricingResult");
  const submitButton = document.getElementById("pricingSubmit");

  if (!form || !resultBox || !submitButton) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) return;

    const formData = new FormData(form);
    const payload = {
      craft_category: String(formData.get("craft_category")),
      material: String(formData.get("material")),
      region: String(formData.get("region")),
      size_cm: Number(formData.get("size_cm")),
      production_hours: Number(formData.get("production_hours")),
      material_cost: Number(formData.get("material_cost")),
      labor_cost: Number(formData.get("labor_cost")),
      demand_score: Number(formData.get("demand_score")),
      complexity_score: Number(formData.get("complexity_score"))
    };

    const numericFields = [
      "size_cm",
      "production_hours",
      "material_cost",
      "labor_cost",
      "demand_score",
      "complexity_score"
    ];

    const invalid = numericFields.some((field) =>
      !Number.isFinite(payload[field]) ||
      payload[field] < 0
    );

    if (
      invalid ||
      payload.size_cm <= 0 ||
      payload.production_hours <= 0 ||
      payload.demand_score > 100 ||
      payload.complexity_score > 100
    ) {
      resultBox.hidden = false;
      resultBox.textContent =
        "Please check the numeric values and score ranges.";
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Estimating…";
    resultBox.hidden = false;
    resultBox.textContent = "Requesting a pricing estimate…";

    try {
      const response = await apiFetch("/api/ai/pricing", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (!response || response.success !== true || !response.result) {
        throw new Error(
          response?.error || "The pricing service could not estimate a price."
        );
      }

      const prediction = response.result;

      if (!Number.isFinite(Number(prediction.recommended_price))) {
        throw new Error("The pricing service returned an invalid price.");
      }

      resultBox.replaceChildren();

      const heading = document.createElement("h2");
      heading.textContent = "Suggested price";

      const price = document.createElement("p");
      price.className = "suggested-price";
      price.textContent = new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: prediction.currency || "INR",
        maximumFractionDigits: 0
      }).format(Number(prediction.recommended_price));

      const modelInfo = document.createElement("p");
      modelInfo.textContent =
        `Model: ${prediction.model || response.model || "Pricing model"}`;

      const warning = document.createElement("p");
      warning.className = "pricing-warning";
      warning.textContent = prediction.warning ||
        "Experimental estimate. Verify the result against actual costs and local market evidence.";

      resultBox.append(heading, price, modelInfo, warning);

    } catch (error) {
      resultBox.textContent =
        error.message || "Unable to obtain a pricing estimate.";
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Estimate suggested price";
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener(
    "DOMContentLoaded",
    initPricingAssistant,
    { once: true }
  );
} else {
  initPricingAssistant();
}
