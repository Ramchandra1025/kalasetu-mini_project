(() => {
  "use strict";

  const API_BASE = `${window.location.origin}/api`;
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];

  const STORAGE = {
    wishlist: "kalasetu_buyer_wishlist",
    shared: "kalasetu_buyer_shared",
    viewed: "kalasetu_buyer_viewed",
    cart: "kalasetu_buyer_cart",
    personalisation: "kalasetu_buyer_personalisation"
  };

  function readJSON(key, fallback = []) {
    try {
      const value = JSON.parse(localStorage.getItem(key));
      return value ?? fallback;
    } catch {
      return fallback;
    }
  }

  function escapeHTML(value = "") {
    return String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    })[char]);
  }

  function setHTML(selector, html) {
    const element = $(selector);
    if (element) element.innerHTML = html;
  }

  function setText(selector, value) {
    const element = $(selector);
    if (element) element.textContent = value ?? "";
  }

  function cash(value) {
    const amount = Number(value);
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2
    }).format(Number.isFinite(amount) ? amount : 0);
  }

  function formatDate(value) {
    if (!value) return "Date unavailable";
    const date = new Date(value);
    return Number.isNaN(date.getTime())
      ? "Date unavailable"
      : date.toLocaleDateString("en-IN", {
          day: "numeric",
          month: "short",
          year: "numeric"
        });
  }

  function safeImageURL(value) {
    if (!value) return "";
    try {
      const url = new URL(value, window.location.origin);
      if (["https:", "http:"].includes(url.protocol)) {
        return url.href;
      }
    } catch {
      // Use the fallback image.
    }
    return "";
  }

  function toast(message) {
    let element = $("#toast");
    if (!element) {
      element = document.createElement("div");
      element.id = "toast";
      element.setAttribute("role", "status");
      element.className = "toast";
      document.body.appendChild(element);
    }

    element.textContent = message;
    element.classList.add("show");

    window.clearTimeout(toast.timeout);
    toast.timeout = window.setTimeout(() => {
      element.classList.remove("show");
    }, 3000);
  }

  async function apiRequest(endpoint, options = {}) {
    const config = {
      method: options.method || "GET",
      credentials: "include",
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {})
      },
      ...(options.body ? { body: JSON.stringify(options.body) } : {})
    };

    let response;

    try {
      response = await fetch(`${API_BASE}${endpoint}`, config);
    } catch {
      throw new Error(
        "Cannot connect to KalaSetu. Check that the Flask backend is running."
      );
    }

    const contentType = response.headers.get("content-type") || "";
    let data = {};

    if (contentType.includes("application/json")) {
      data = await response.json().catch(() => ({}));
    } else {
      const text = await response.text().catch(() => "");
      data = text ? { message: text } : {};
    }

    if (!response.ok) {
      throw new Error(
        data.message || data.error || `Request failed (${response.status}).`
      );
    }

    return data;
  }

  const state = {
    products: [],
    category: "All",
    search: "",
    sort: "newest",
    view: "home",
    wishlist: new Set(
      readJSON(STORAGE.wishlist, []).map(String)
    ),
    shared: new Set(
      readJSON(STORAGE.shared, []).map(String)
    ),
    viewed: readJSON(STORAGE.viewed, []),
    cart: readJSON(STORAGE.cart, {}),
    personalisation:
      localStorage.getItem(STORAGE.personalisation) !== "false",
    ordersLoading: false,
    trackingLoading: false,
    checkoutLoading: false
  };

  function saveState() {
    localStorage.setItem(
      STORAGE.wishlist,
      JSON.stringify([...state.wishlist])
    );
    localStorage.setItem(
      STORAGE.shared,
      JSON.stringify([...state.shared])
    );
    localStorage.setItem(
      STORAGE.viewed,
      JSON.stringify(state.viewed.slice(0, 30))
    );
    localStorage.setItem(
      STORAGE.cart,
      JSON.stringify(state.cart)
    );
  }

  
function normalizeProduct(raw) {
  const artisan = raw.artisan || {};

  // Safely resolve the product price
  const rawPrice =
    raw.recommended_price ??
    raw.base_price ??
    raw.price ??
    null;

  const parsedPrice =
    rawPrice === null || rawPrice === ""
      ? null
      : Number(rawPrice);

  // Preserve unknown stock instead of treating it as zero
  const rawStock =
    raw.stock_quantity ??
    raw.stock ??
    null;

  const parsedStock =
    rawStock === null || rawStock === ""
      ? null
      : Number(rawStock);

  // Resolve image URL
  const imageValue =
    raw.image_url ||
    raw.image ||
    raw.photo_url ||
    raw.thumbnail ||
    null;

  // Resolve nested AI attributes safely
  const attributes =
    raw.ai_attributes &&
    typeof raw.ai_attributes === "object"
      ? raw.ai_attributes
      : {};

  return {
    id: String(raw.id ?? raw.product_id ?? ""),

    name:
      raw.name ||
      raw.product_name ||
      raw.title ||
      "Untitled craft",

    category:
      raw.craft_category ||
      raw.category ||
      raw.ai_category ||
      "Other",

    artisan:
      artisan.name ||
      raw.artisan_name ||
      raw.seller_name ||
      "Indian artisan",

    artisanId: String(
      raw.artisan_id ?? artisan.id ?? ""
    ),

    location:
      raw.location ||
      artisan.location ||
      raw.artisan_location ||
      "India",

    price:
      parsedPrice !== null && Number.isFinite(parsedPrice)
        ? Math.max(0, parsedPrice)
        : null,

    image: safeImageURL(imageValue),

    description:
      raw.description ||
      raw.product_description ||
      "Handcrafted with care.",

    material:
      raw.material ||
      raw.ai_material ||
      attributes.material ||
      "Not specified",

    color:
      raw.color ||
      attributes.color ||
      "Not specified",

    dimensions:
      raw.dimensions ||
      attributes.dimensions ||
      "Not specified",

    // null means unknown; 0 means confirmed zero stock
    stock:
      parsedStock !== null && Number.isFinite(parsedStock)
        ? Math.max(0, parsedStock)
        : null,

    createdAt:
      raw.created_at ||
      raw.createdAt ||
      null,

    rating: Number.isFinite(Number(raw.rating))
      && raw.rating !== null
      && raw.rating !== ""
        ? Number(raw.rating)
        : null
  };
}


  function getProduct(id) {
    return state.products.find(
      (product) => product.id === String(id)
    );
  }

  function getCartEntries() {
    return Object.entries(state.cart)
      .map(([id, quantity]) => ({
        product: getProduct(id),
        quantity: Number(quantity)
      }))
      .filter(
        (entry) =>
          entry.product &&
          Number.isInteger(entry.quantity) &&
          entry.quantity > 0
      );
  }

  function cartSubtotal() {
    return getCartEntries().reduce(
      (sum, entry) =>
        sum + entry.product.price * entry.quantity,
      0
    );
  }

  function emptyState(message) {
    return `<div class="empty-state"><p>${escapeHTML(message)}</p></div>`;
  }

  async function loadProducts() {
   setHTML("#shopProducts", emptyState("Loading products…"));

    try {
      const data = await apiRequest("/catalogue/products");
      const products = Array.isArray(data)
        ? data
        : data.products || data.items || [];

      state.products = products
        .map(normalizeProduct)
        .filter((product) => product.id);

      // Remove products that no longer exist.
      const validIds = new Set(
        state.products.map((product) => product.id)
      );

      state.wishlist = new Set(
        [...state.wishlist].filter((id) => validIds.has(id))
      );

      state.shared = new Set(
        [...state.shared].filter((id) => validIds.has(id))
      );

      for (const id of Object.keys(state.cart)) {
        if (!validIds.has(id)) delete state.cart[id];
      }

      saveState();
      renderAll();

      const productId = new URLSearchParams(
        window.location.search
      ).get("product");

      if (productId && getProduct(productId)) {
        openProduct(productId);
      }
    } catch (error) {
      setHTML("#productGrid", emptyState(error.message));
      toast(error.message);
    }
  }

 

function productCard(product) {
  const p = product || {};
  const id = String(p.id ?? p.product_id ?? "");
  if (!id) return "";

  const name = p.name || p.product_name || "Handcrafted product";
  const category =
    p.category || p.craft_category || p.ai_category || "Indian craft";
  const artisan =
    p.artisan || p.artisan_name || p.seller_name || p.artist_name || "Indian artisan";
  const location = p.location || p.origin || p.state || "India";
  const rawPrice = p.price ?? p.recommended_price ?? p.base_price;
  const price = Number(rawPrice);
  const validPrice =
    rawPrice !== undefined &&
    rawPrice !== null &&
    rawPrice !== "" &&
    Number.isFinite(price) &&
    price >= 0;

  const image = safeImageURL(
    p.image || p.image_url || p.photo_url || p.thumbnail || ""
  );

  // Use the actual wishlist Set maintained by this script.
  const saved = state.wishlist.has(id);

  const rawStock = p.stock ?? p.stock_quantity;
  const hasStock =
    rawStock !== undefined &&
    rawStock !== null &&
    rawStock !== "" &&
    Number.isFinite(Number(rawStock));

  const stock = hasStock ? Number(rawStock) : null;
  const outOfStock = stock !== null && stock <= 0;
  const inCart = Number(state.cart[id] || 0);

  const stockLabel = outOfStock
    ? "Currently unavailable"
    : stock === null
      ? "Availability to be confirmed"
      : stock === 1
        ? "1 available"
        : `${stock} available`;

  const money = validPrice
    ? cash(price)
    : "Price unavailable";

  const safeId = escapeHTML(id);
  const safeName = escapeHTML(name);

  return `
    <article class="ks-product-card" data-product-id="${safeId}">
      <div class="ks-product-media">
        ${
          image
            ? `<img class="ks-product-image"
                    src="${escapeHTML(image)}"
                    alt="${safeName}"
                    loading="lazy"
                    decoding="async"
                    onerror="this.style.display='none'; this.nextElementSibling.hidden=false">
               <div class="ks-product-image-fallback" hidden>
                 <span aria-hidden="true">✳</span>
                 <span>Craft image unavailable</span>
               </div>`
            : `<div class="ks-product-image-fallback">
                 <span aria-hidden="true">✳</span>
                 <span>Craft image unavailable</span>
               </div>`
        }

        <span class="ks-product-badge">${escapeHTML(category)}</span>

        <button class="ks-product-heart ${saved ? "is-saved" : ""}"
                type="button"
                data-wish="${safeId}"
                aria-label="${saved ? "Remove from wishlist" : "Save to wishlist"}"
                aria-pressed="${saved}"
                title="${saved ? "Remove from wishlist" : "Save to wishlist"}">
          ${saved ? "♥" : "♡"}
        </button>

        <button class="ks-product-share"
                type="button"
                data-share="${safeId}"
                aria-label="Share ${safeName}"
                title="Share product">
          ↗
        </button>
      </div>

      <div class="ks-product-info">
        <div class="ks-product-eyebrow">AUTHENTIC INDIAN CRAFT</div>

        <h3 class="ks-product-title">
          <button type="button" data-open="${safeId}">
            ${safeName}
          </button>
        </h3>

        <div class="ks-product-artisan">
          <span class="ks-product-artisan-mark" aria-hidden="true">K</span>
          <span>${escapeHTML(artisan)}</span>
        </div>

        <div class="ks-product-location">
          <span aria-hidden="true">⌖</span>
          ${escapeHTML(location)}
        </div>

        <div class="ks-product-bottom">
          <div class="ks-product-price-block">
            <div class="ks-product-price">${money}</div>
            <div class="ks-product-stock ${
              stock !== null && stock > 0 && stock <= 3 ? "is-low" : ""
            }">${escapeHTML(stockLabel)}</div>
          </div>
        </div>

        <div class="ks-product-actions">
          <button class="ks-product-add"
                  type="button"
                  data-add="${safeId}"
                  ${outOfStock ? "disabled" : ""}>
            ${outOfStock ? "Out of stock" : inCart > 0 ? `Add more (${inCart})` : "Add to cart"}
          </button>

          <button class="ks-product-buy"
                  type="button"
                  data-buy-now="${safeId}"
                  ${outOfStock ? "disabled" : ""}>
            Buy now
          </button>

          <button class="ks-product-view"
                  type="button"
                  data-open="${safeId}"
                  aria-label="View ${safeName} details"
                  title="View details">
            Details
          </button>
        </div>
      </div>
    </article>
  `;
}


  function filteredProducts() {
  let products = [...state.products].filter(
    (product) => product.stock === null || product.stock > 0
  );

  if (state.category !== "All") {
    products = products.filter(
      (product) => product.category === state.category
    );
  }

  const query = state.search.trim().toLowerCase();

  if (query) {
    products = products.filter((product) =>
      [
        product.name,
        product.category,
        product.artisan,
        product.location,
        product.description,
        product.material
      ].some((value) =>
        String(value ?? "").toLowerCase().includes(query)
      )
    );
  }

  switch (state.sort) {
    case "low":
      products.sort((a, b) => a.price - b.price);
      break;
    case "high":
      products.sort((a, b) => b.price - a.price);
      break;
    case "rating":
      products.sort(
        (a, b) => Number(b.rating || 0) - Number(a.rating || 0)
      );
      break;
    default:
      products.sort(
        (a, b) =>
          new Date(b.createdAt || 0) - new Date(a.createdAt || 0)
      );
  }

  return products;
}

 function renderProductList() {
  const products = filteredProducts();

  setHTML(
    "#shopProducts",
    products.map(productCard).join("")
  );

  const empty = $("#shopEmpty");
  if (empty) {
    empty.classList.toggle("hidden", products.length > 0);
  }

  renderCategories();
}
  function renderCategories() {
  const container = $("#filters");
  if (!container) return;

  const categories = [
    "All",
    ...new Set(
      state.products.map(p => p.category).filter(Boolean)
    )
  ];

  container.innerHTML = categories.map(category => `
    <button
      type="button"
      data-cat="${escapeHTML(category)}"
      class="filter${state.category === category ? " active" : ""}">
      ${escapeHTML(category)}
    </button>
  `).join("");

  const homeCategories = $("#categories");
  if (homeCategories) {
    homeCategories.innerHTML = categories
      .filter(category => category !== "All")
      .map(category => `
        <button
          type="button"
          class="category"
          data-cat="${escapeHTML(category)}">
          <b>${escapeHTML(category)}</b>
        </button>
      `).join("");
  }
}

function renderHomeProducts() {
  const products = state.products.filter(p => p.stock > 0);

  setHTML(
    "#featured",
    products.length
      ? products.slice(0, 4).map(productCard).join("")
      : emptyState("No products are available yet.")
  );

  setHTML(
    "#collections",
    [...new Set(products.map(p => p.category))]
      .filter(Boolean)
      .map(category => `
        <button type="button" data-cat="${escapeHTML(category)}">
          ${escapeHTML(category)}
        </button>
      `).join("")
  );
}
  function renderRecommendations() {
    const viewedCategories = state.viewed
      .map((id) => getProduct(id)?.category)
      .filter(Boolean);

    const preferredCategories = new Set([
      ...viewedCategories,
      ...[...state.wishlist].map(
        (id) => getProduct(id)?.category
      ),
      ...getCartEntries().map(
        (entry) => entry.product.category
      )
    ]);

    let recommendations = state.products.filter(
      (product) =>
        product.stock > 0 &&
        !state.wishlist.has(product.id) &&
        !state.cart[product.id]
    );

    if (state.personalisation && preferredCategories.size) {
      recommendations.sort(
        (a, b) =>
          Number(preferredCategories.has(b.category)) -
          Number(preferredCategories.has(a.category))
      );
    }

    recommendations = recommendations.slice(0, 4);

   const html = recommendations.length
  ? recommendations.map(productCard).join("")
  : emptyState("Explore the catalogue to discover more crafts.");

setHTML("#allRecommended", html);
setHTML("#recommended", html);
  }

  function renderWishlist() {
    const products = [...state.wishlist]
      .map(getProduct)
      .filter(Boolean);

    setHTML(
      "#wishlistProducts",
      products.length
        ? products.map(productCard).join("")
        : emptyState("Your wishlist is empty.")
    );

    const empty = $("#wishlistEmpty");
    if (empty) {
      empty.classList.toggle("hidden", products.length > 0);
    }
  }

  function renderShared() {
    const products = [...state.shared]
      .map(getProduct)
      .filter(Boolean);

    setHTML(
      "#sharedProducts",
      products.length
        ? products.map(productCard).join("")
        : emptyState("You have not shared any products yet.")
    );

    const empty = $("#sharedEmpty");
    if (empty) {
      empty.classList.toggle("hidden", products.length > 0);
    }
  }

  function renderCart() {
    const entries = getCartEntries();

    setHTML(
      "#cartItems",
      entries.length
        ? entries.map(({ product, quantity }) => `
          <div class="cart-item">
            <div class="cart-item-info">
              <h3>${escapeHTML(product.name)}</h3>
              <p>${cash(product.price)} each</p>
              <p>Line total: ${cash(product.price * quantity)}</p>
            </div>
            <div class="cart-item-controls">
              <button type="button" data-qty="${escapeHTML(product.id)}" data-delta="-1" aria-label="Decrease quantity">−</button>
              <span>${quantity}</span>
              <button type="button" data-qty="${escapeHTML(product.id)}" data-delta="1" aria-label="Increase quantity" ${quantity >= product.stock ? "disabled" : ""}>+</button>
              <button type="button" data-remove="${escapeHTML(product.id)}">Remove</button>
            </div>
          </div>
        `).join("")
        : emptyState("Your cart is empty.")
    );

    setHTML("#cartTotal", `<span>Total</span><span>${cash(cartSubtotal())}</span>`);

    const checkoutButton = $("#checkout");
    if (checkoutButton) {
      checkoutButton.disabled =
        entries.length === 0 || state.checkoutLoading;
    }

    renderCounts();
  }

  function renderCounts() {
    const cartCount = getCartEntries().reduce(
      (sum, entry) => sum + entry.quantity,
      0
    );

    const wishCount = state.wishlist.size;

    setText("#cartCount", cartCount);
    setText("#wishCount", wishCount);        // sidebar nav badge
    setText("#wishCountTop", wishCount);     // topbar icon badge
  }

function renderAll() {
  renderHomeProducts();
  renderProductList();
  renderRecommendations();
  renderWishlist();
  renderShared();
  renderCart();
  renderCounts();
}

  function addToCart(id, quantity = 1) {
    const product = getProduct(id);

    if (!product) {
      toast("Product not found.");
      return;
    }

    if (product.stock < 1) {
      toast("This product is currently out of stock.");
      return;
    }

    const existing = Number(state.cart[product.id] || 0);
    const next = existing + quantity;

    if (!Number.isInteger(next) || next < 1) return;

    if (next > product.stock) {
      toast(`Only ${product.stock} item(s) are available.`);
      return;
    }

    state.cart[product.id] = next;
    saveState();
    renderCart();
    renderRecommendations();
    toast("Added to your cart.");
  }

  function changeQuantity(id, delta) {
    const product = getProduct(id);
    if (!product) return;

    const next = Number(state.cart[id] || 0) + delta;

    if (next <= 0) {
      delete state.cart[id];
    } else if (next > product.stock) {
      toast(`Only ${product.stock} item(s) are available.`);
      return;
    } else {
      state.cart[id] = next;
    }

    saveState();
    renderCart();
    renderRecommendations();
  }

  function removeFromCart(id) {
    delete state.cart[id];
    saveState();
    renderCart();
    renderRecommendations();
    toast("Item removed from cart.");
  }

  function toggleWishlist(id) {
    const key = String(id);

    if (state.wishlist.has(key)) {
      state.wishlist.delete(key);
      toast("Removed from wishlist.");
    } else {
      state.wishlist.add(key);
      toast("Added to wishlist.");
    }

    saveState();
    renderWishlist();
    renderProductList();
    renderRecommendations();
    renderCounts();
  }

  async function shareProduct(id) {
    const product = getProduct(id);
    if (!product) return;

    const url = new URL(window.location.href);
    url.searchParams.set("product", product.id);

    const shareData = {
      title: product.name,
      text: `Discover ${product.name} by ${product.artisan} on KalaSetu.`,
      url: url.href
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareData.url);
        toast("Product link copied.");
      } else {
        window.prompt("Copy this product link:", shareData.url);
      }

      state.shared.add(product.id);
      saveState();
      renderShared();
      renderCounts();
    } catch (error) {
      if (error.name !== "AbortError") {
        toast("Could not share this product.");
      }
    }
  }

  function openProduct(id) {
    const product = getProduct(id);
    if (!product) return;

    state.viewed = [
      product.id,
      ...state.viewed.filter((value) => String(value) !== product.id)
    ].slice(0, 30);

    saveState();

    const modal = $("#modal");
    if (!modal) {
      toast(`${product.name} — ${cash(product.price)}`);
      return;
    }

    const saved = state.wishlist.has(product.id);

    const image = product.image
      ? `<img src="${escapeHTML(product.image)}" alt="${escapeHTML(product.name)}" style="width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:10px;background:var(--sage);margin-bottom:16px;">`
      : `<div class="ks-product-image-fallback" style="margin-bottom:16px;"><span aria-hidden="true">✳</span><span>Image unavailable</span></div>`;

    const stockText = product.stock > 0
      ? `${product.stock} in stock`
      : product.stock === 0
        ? "Currently unavailable"
        : "Availability to be confirmed";

    setHTML(
      "#modalContent",
      `
      <div class="modal-product">
        <div>${image}</div>
        <div>
          <p class="kicker">${escapeHTML(product.category)}</p>
          <h2>${escapeHTML(product.name)}</h2>
          <p class="modal-price">${cash(product.price)}</p>
          <p>${escapeHTML(product.description)}</p>
          <p><strong>Artisan:</strong> ${escapeHTML(product.artisan)}</p>
          <p><strong>Location:</strong> ${escapeHTML(product.location)}</p>
          <p><strong>Material:</strong> ${escapeHTML(product.material)}</p>
          <p><strong>Color:</strong> ${escapeHTML(product.color)}</p>
          <p><strong>Dimensions:</strong> ${escapeHTML(product.dimensions)}</p>
          <p><strong>Stock:</strong> ${escapeHTML(stockText)}</p>
          <div class="product-actions">
            <button class="primary" type="button" data-add="${escapeHTML(product.id)}" ${product.stock === 0 ? "disabled" : ""}>Add to cart</button>
            <button class="buy-now" type="button" data-buy-now="${escapeHTML(product.id)}" ${product.stock === 0 ? "disabled" : ""}>Buy now</button>
            <button class="outline" type="button" data-wish="${escapeHTML(product.id)}" aria-pressed="${saved}" aria-label="${saved ? "Remove from wishlist" : "Save to wishlist"}">${saved ? "♥ Wishlisted" : "♡ Wishlist"}</button>
            <button class="ghost" type="button" data-enquire="${escapeHTML(product.id)}">Enquire</button>
          </div>
        </div>
      </div>`
    );

    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");
    renderRecommendations();
  }

  function closeProductModal() {
    const modal = $("#modal");
    modal?.classList.add("hidden");
    modal?.setAttribute("aria-hidden", "true");
  }


function buyNow(id) {
  const product = getProduct(id);
  if (!product) {
    toast("Product not found.");
    return;
  }

  if (product.stock < 1) {
    toast("This product is currently out of stock.");
    return;
  }

  const currentQuantity = Number(state.cart[product.id] || 0);

  if (currentQuantity < 1) {
    addToCart(product.id, 1);

    // addToCart validates stock and displays an error if needed.
    if (Number(state.cart[product.id] || 0) < 1) return;
  }

  closeProductModal();
  show("cart");
}


function show(view) {
  const allowedViews = [
    "home",
    "shop",
    "recommendations",
    "wishlist",
    "shared",
    "orders",
    "tracking",
    "messages",
    "profile",
    "settings",
    "cart"
  ];

  if (!allowedViews.includes(view)) {
    console.warn("Unknown buyer dashboard view:", view);
    return;
  }

  state.view = view;

  // Your HTML uses homeView, shopView, ordersView, etc.
  $$(".view").forEach((section) => {
    const isActive = section.id === `${view}View`;
    section.classList.toggle("hidden", !isActive);
    section.classList.toggle("active", isActive);
  });

  $$("[data-view]").forEach((element) => {
    const isActive = element.dataset.view === view;
    element.classList.toggle("active", isActive);

    if (element.matches("button")) {
      element.setAttribute("aria-current", isActive ? "page" : "false");
    }
  });

  if (view === "home") renderAll();
  if (view === "shop") renderProductList();
  if (view === "recommendations") renderRecommendations();
  if (view === "wishlist") renderWishlist();
  if (view === "shared") renderShared();
  if (view === "cart") renderCart();
  if (view === "orders") renderOrders();

  // Close the mobile navigation drawer if present.
  $("#sidebar")?.classList.remove("open");
  $("#scrim")?.classList.remove("show");
}


  function statusLabel(status) {
    const labels = {
      pending: "Pending",
      confirmed: "Confirmed",
      accepted: "Accepted",
      processing: "Processing",
      shipped: "Shipped",
      in_transit: "In transit",
      delivered: "Delivered",
      cancelled: "Cancelled"
    };

    const key = String(status || "pending").toLowerCase();
    return labels[key] || key.replaceAll("_", " ");
  }

  async function renderOrders() {
    if (state.ordersLoading) return;
    state.ordersLoading = true;

    setHTML("#orders", emptyState("Loading orders…"));

    try {
      const data = await apiRequest("/orders");
      const orders = Array.isArray(data)
        ? data
        : data.orders || [];

      setHTML(
        "#orders",
        orders.length
          ? orders.map((order) => {
              const id = order.id || order.order_id;
              const reference = order.order_reference || id;
              return `
                <article class="order-card">
                  <h3>Order ${escapeHTML(reference || "")}</h3>
                  <p>Status: ${escapeHTML(statusLabel(order.status))}</p>
                  <p>Total: ${cash(order.total_amount ?? order.total ?? 0)}</p>
                  <p>Placed: ${formatDate(order.created_at)}</p>
                  <button type="button" data-track-order="${escapeHTML(id || "")}">Track order</button>
                </article>`;
            }).join("")
          : emptyState("You have not placed any orders yet.")
      );
    } catch (error) {
      setHTML("#orders", emptyState(error.message));
    } finally {
      state.ordersLoading = false;
    }
  }

  async function track(orderId) {
    if (!orderId || state.trackingLoading) return;

    state.trackingLoading = true;
    setHTML("#trackingResult", emptyState("Loading tracking information…"));

    try {
      const data = await apiRequest(
        `/orders/${encodeURIComponent(orderId)}/tracking`
      );

      const events = Array.isArray(data)
        ? data
        : data.events || data.tracking_events || [];

      const order = data.order || null;

      const header = order
        ? `<h3>Order status: ${escapeHTML(statusLabel(order.status))}</h3>`
        : "";

      setHTML(
        "#trackingResult",
        header + (
          events.length
            ? `<ol class="tracking-timeline">${events.map((event) => `
                <li>
                  <strong>${escapeHTML(statusLabel(event.status))}</strong>
                  <p>${escapeHTML(event.description || "")}</p>
                  <p>${escapeHTML(event.location || "")}</p>
                  <small>${formatDate(event.created_at || event.updated_at)}</small>
                </li>`).join("")}</ol>`
            : emptyState("No tracking events are available yet.")
        )
      );
    } catch (error) {
      setHTML("#trackingResult", emptyState(error.message));
    } finally {
      state.trackingLoading = false;
    }
  }

  function openCheckoutForm() {
    if (!getCartEntries().length) {
      toast("Add at least one product to your cart.");
      return;
    }

    const form = $("#checkoutForm");

    if (!form) {
      toast("Add the checkout form fields to your cart HTML first.");
      return;
    }

    form.classList.remove("hidden");
    form.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function getDeliveryDetails() {
    const fields = {
      name: $("#deliveryName"),
      phone: $("#deliveryPhone"),
      address: $("#deliveryAddress"),
      city: $("#deliveryCity"),
      state: $("#deliveryState"),
      pincode: $("#deliveryPincode")
    };

    for (const [key, element] of Object.entries(fields)) {
      if (!element || !element.value.trim()) {
        throw new Error(`Please enter your delivery ${key}.`);
      }

      if (!element.checkValidity()) {
        element.reportValidity();
        throw new Error(`Please check the delivery ${key}.`);
      }
    }

    return {
      name: fields.name.value.trim(),
      phone: fields.phone.value.trim(),
      address: fields.address.value.trim(),
      city: fields.city.value.trim(),
      state: fields.state.value.trim(),
      pincode: fields.pincode.value.trim()
    };
  }

  async function placeOrder() {
    if (state.checkoutLoading) return;

    const entries = getCartEntries();

    if (!entries.length) {
      toast("Your cart is empty.");
      return;
    }

    let delivery;

    try {
      delivery = getDeliveryDetails();
    } catch (error) {
      toast(error.message);
      return;
    }

    const items = entries.map(({ product, quantity }) => ({
      product_id: product.id,
      quantity
    }));

    state.checkoutLoading = true;

    const placeOrderButton = $("#placeOrder");
    const checkoutButton = $("#checkout");

    if (placeOrderButton) {
      placeOrderButton.disabled = true;
      placeOrderButton.textContent = "Placing order…";
    }

    if (checkoutButton) checkoutButton.disabled = true;

    try {
      const result = await apiRequest("/orders/checkout", {
        method: "POST",
        body: {
          items,
          delivery
        }
      });

      const confirmed =
        result.success === true &&
        (
          (Array.isArray(result.orders) && result.orders.length > 0) ||
          Boolean(result.order?.id) ||
          Boolean(result.order_id)
        );

      if (!confirmed) {
        throw new Error(
          result.message ||
          "The server did not confirm the order. Your cart has been preserved."
        );
      }

      // Clear the cart only after explicit server confirmation.
      state.cart = {};
      saveState();
      renderCart();

      $("#checkoutForm")?.classList.add("hidden");

      toast("Order placed successfully.");
      show("orders");
      await renderOrders();
    } catch (error) {
      toast(error.message);
    } finally {
      state.checkoutLoading = false;

      if (placeOrderButton) {
        placeOrderButton.disabled = false;
        placeOrderButton.textContent = "Place order";
      }

      if (checkoutButton) {
        checkoutButton.disabled = getCartEntries().length === 0;
      }
    }
  }

 async function loadProfile() {
  try {
    const data = await apiRequest("/auth/me");
    const user = data.user || data.account || data;

    const name =
      user.name ||
      user.full_name ||
      user.display_name ||
      user.email?.split("@")[0] ||
      "Buyer";

    setText("#buyerName", name);
    setText("#avatar", name.charAt(0).toUpperCase());

    if ($("#name")) $("#name").value = user.name || user.full_name || "";
    if ($("#email")) $("#email").value = user.email || "";

    if ($("#interest")) {
      $("#interest").value = user.interest || user.preferred_craft || "";
    }
  } catch (error) {
    console.error("Profile loading failed:", error);
    toast("Could not load your profile.");
  }
}

  async function saveProfile(event) {
    event.preventDefault();

    const name = $("#profileName")?.value.trim();
    const phone = $("#profilePhone")?.value.trim();

    try {
      await apiRequest("/profile", {
        method: "PUT",
        body: { name, phone }
      });

      toast("Profile updated.");
    } catch (error) {
      toast(error.message);
    }
  }

  async function logout() {
    try {
      await apiRequest("/auth/logout", { method: "POST" });
    } catch (error) {
      console.warn("Logout request failed:", error.message);
    }

    window.location.href = "../login.html";
  }

  function initialiseControls() {
    $("#searchInput")?.addEventListener("input", (event) => {
      state.search = event.target.value;
      renderProductList();
    });

    $("#search")?.addEventListener("input", (event) => {
      state.search = event.target.value;
      renderProductList();
    });

    // Sort — HTML select is id="sort"
    $("#sort")?.addEventListener("change", (event) => {
      state.sort = event.target.value;
      renderProductList();
    });

    $("#trackForm")?.addEventListener("submit", (event) => {
      event.preventDefault();
      track($("#orderId")?.value.trim());
    });

    $("#profileForm")?.addEventListener("submit", saveProfile);

    $("#checkout")?.addEventListener("click", openCheckoutForm);
    $("#placeOrder")?.addEventListener("click", placeOrder);

    $("#cancelCheckout")?.addEventListener("click", () => {
      $("#checkoutForm")?.classList.add("hidden");
    });

    // Modal close — HTML has id="modalClose" and id="modal"
    $("#modalClose")?.addEventListener("click", closeProductModal);

    $("#modal")?.addEventListener("click", (event) => {
      if (event.target.id === "modal") {
        closeProductModal();
      }
    });

    document.addEventListener("keydown", (evt) => {
      if (evt.key === "Escape") closeProductModal();
    });

    // Personalisation toggle — HTML id is "personalisation"
    $("#personalisation")?.addEventListener("change", (event) => {
      state.personalisation = event.target.checked;
      localStorage.setItem(
        STORAGE.personalisation,
        String(state.personalisation)
      );
      renderRecommendations();
    });

    // Save settings button
    $("#saveSettings")?.addEventListener("click", () => {
      const lang = $("#settingsLanguage")?.value;
      if (lang) localStorage.setItem("kalasetu_lang", lang);
      state.personalisation = $("#personalisation")?.checked ?? state.personalisation;
      localStorage.setItem(STORAGE.personalisation, String(state.personalisation));
      toast("Settings saved.");
    });

    $("#logoutButton")?.addEventListener("click", logout);
    $("#logout")?.addEventListener("click", logout);

    document.addEventListener("click", async (event) => {
      const target = event.target.closest("button, a");
      if (!target) return;

      if (target.matches("[data-view]")) {
        event.preventDefault();
        show(target.dataset.view);
        return;
      }

      if (target.matches("[data-cat]")) {
        state.category = target.dataset.cat;
        renderProductList();
        return;
      }

      if (target.matches("[data-open]")) {
        openProduct(target.dataset.open);
        return;
      }

      if (target.matches("[data-add]")) {
        addToCart(target.dataset.add);
        return;
      }

      if (target.matches("[data-buy-now]")) {
        buyNow(target.dataset.buyNow);
        return;
      }

      if (target.matches("[data-wish]")) {
        toggleWishlist(target.dataset.wish);
        return;
      }

      if (target.matches("[data-share]")) {
        await shareProduct(target.dataset.share);
        return;
      }

      if (target.matches("[data-qty]")) {
        changeQuantity(
          target.dataset.qty,
          Number(target.dataset.delta || 0)
        );
        return;
      }

      if (target.matches("[data-remove]")) {
        removeFromCart(target.dataset.remove);
        return;
      }

      if (target.matches("[data-track-order]")) {
        show("tracking");
        track(target.dataset.trackOrder);
        return;
      }

      if (target.matches("[data-track]")) {
        show("tracking");
        track(target.dataset.track);
        return;
      }

      if (target.matches("[data-enquire]")) {
        const product = getProduct(target.dataset.enquire);
        if (!product) return;

        const subject = encodeURIComponent(
          `Enquiry about ${product.name}`
        );

        const body = encodeURIComponent(
          `Hello, I am interested in ${product.name} on KalaSetu.`
        );

        const email = product.artisanEmail || "";
        if (email) {
          window.location.href =
            `mailto:${encodeURIComponent(email)}?subject=${subject}&body=${body}`;
        } else {
          toast("Artisan contact details are not available yet.");
        }
      }
    });
  }

  async function init() {
    initialiseControls();

    // Copyright year
    setText("#year", new Date().getFullYear());

    const personalisationToggle = $("#personalisation");
    if (personalisationToggle) {
      personalisationToggle.checked = state.personalisation;
    }

    // Right-rail "Share a product" button — share the first featured product if available
    $("#shareFeatured")?.addEventListener("click", () => {
      const first = state.products.find((p) => p.stock > 0);
      if (first) shareProduct(first.id);
      else toast("No products available to share yet.");
    });

    renderCart();
    renderCounts();

    await Promise.all([
      loadProducts(),
      loadProfile()
    ]);

    const initialView = new URLSearchParams(
      window.location.search
    ).get("view");

    if (initialView) show(initialView);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
