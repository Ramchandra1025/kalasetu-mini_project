
/**
 * KalaSetu — Shared API utility
 *
 * Centralizes requests to the Flask backend.
 * Uses the existing Flask session cookie.
 * Does not access Supabase directly from the browser.
 */

(() => {
  "use strict";

  const API_BASE = `${window.location.origin}/api`;

  async function request(path, options = {}) {
    const {
      method = "GET",
      headers = {},
      body,
      ...rest
    } = options;

    const config = {
      method,
      credentials: "include",
      headers: { ...headers },
      ...rest,
    };

    if (body !== undefined) {
      if (
        body instanceof FormData ||
        body instanceof Blob ||
        typeof body === "string"
      ) {
        config.body = body;
      } else {
        config.headers["Content-Type"] = "application/json";
        config.body = JSON.stringify(body);
      }
    }

    let response;

    try {
      response = await fetch(`${API_BASE}${path}`, config);
    } catch (error) {
      throw new Error(
        "Unable to connect to KalaSetu. Check that the backend is running."
      );
    }

    const contentType = response.headers.get("content-type") || "";
    let data;

    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const message =
        typeof data === "object" && data !== null
          ? data.message || data.error
          : null;

      const error = new Error(
        message || `Request failed with status ${response.status}.`
      );

      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  window.KalaSetuAPI = Object.freeze({
    request,

    get(path, options = {}) {
      return request(path, { ...options, method: "GET" });
    },

    post(path, body, options = {}) {
      return request(path, { ...options, method: "POST", body });
    },

    put(path, body, options = {}) {
      return request(path, { ...options, method: "PUT", body });
    },

    delete(path, options = {}) {
      return request(path, { ...options, method: "DELETE" });
    },
  });
})();
