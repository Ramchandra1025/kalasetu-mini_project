
"use strict";

// ============================================================
// KALASETU AUTHENTICATION
// Registration -> Email OTP -> Login -> Correct Dashboard
// ============================================================

const API_BASE = `${window.location.origin}/api/auth`;


// ============================================================
// SHARED HELPERS
// ============================================================

function showMessage(element, message, type = "error") {
    if (!element) return;

    element.textContent = message;
    element.className = `message ${type}`;
}

async function apiRequest(endpoint, options = {}) {
    let response;

    try {
        response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        });
    } catch (error) {
        throw new Error(
            "Unable to connect to KalaSetu. Check that the Flask server is running."
        );
    }

    const data = await response.json().catch(() => ({}));

    return { response, data };
}

function getErrorMessage(data, fallback) {
    return data?.message || data?.error || fallback;
}

function setButtonLoading(button, loading, loadingText, normalText) {
    if (!button) return;

    button.disabled = loading;

    const text = button.querySelector(".button-text");

    if (text) {
        text.textContent = loading ? loadingText : normalText;
    } else {
        button.textContent = loading ? loadingText : normalText;
    }
}

function normalizeAccountType(account) {
    return String(
        account?.account_type ||
        account?.user?.account_type ||
        account?.account?.account_type ||
        ""
    ).trim().toLowerCase();
}


// ============================================================
// REGISTER
// Endpoint: POST /api/auth/register
// ============================================================

const registerForm = document.getElementById("registerForm");

if (registerForm) {
    const artisanOption = document.getElementById("artisanOption");
    const buyerOption = document.getElementById("buyerOption");
    const registerButton = registerForm.querySelector(
        'button[type="submit"]'
    );

    function updateAccountTypeUI() {
        const selected = document.querySelector(
            'input[name="account_type"]:checked'
        );

        artisanOption?.classList.toggle(
            "selected",
            selected?.value === "artisan"
        );

        buyerOption?.classList.toggle(
            "selected",
            selected?.value !== "artisan"
        );
    }

    document
        .querySelectorAll('input[name="account_type"]')
        .forEach(input => {
            input.addEventListener("change", updateAccountTypeUI);
        });

    updateAccountTypeUI();

    registerForm.addEventListener("submit", async event => {
        event.preventDefault();

        const message = document.getElementById("registerMessage");
        const name = document.getElementById("name")?.value.trim();
        const email = document.getElementById("email")?.value.trim().toLowerCase();
        const password = document.getElementById("password")?.value || "";
        const confirmPassword =
            document.getElementById("confirmPassword")?.value || "";
        const selectedType = document.querySelector(
            'input[name="account_type"]:checked'
        );
        const language = document.getElementById("language")?.value || "English";

        if (!name || !email || !password || !confirmPassword) {
            showMessage(message, "Please complete all required fields.");
            return;
        }

        if (!selectedType) {
            showMessage(message, "Please select Buyer or Artisan.");
            return;
        }

        if (password.length < 8) {
            showMessage(
                message,
                "Password must contain at least 8 characters."
            );
            return;
        }

        if (password !== confirmPassword) {
            showMessage(message, "Passwords do not match.");
            return;
        }

        const accountType = selectedType.value;

        if (!["buyer", "artisan"].includes(accountType)) {
            showMessage(message, "Please select a valid account type.");
            return;
        }

        setButtonLoading(
            registerButton,
            true,
            "Creating account...",
            "Create Account"
        );

        showMessage(message, "Creating your account...", "success");

        try {
            const { response, data } = await apiRequest("/register", {
                method: "POST",
                body: JSON.stringify({
                    name,
                    email,
                    password,
                    account_type: accountType,
                    preferred_language: language
                })
            });

            if (!response.ok) {
                showMessage(
                    message,
                    getErrorMessage(data, "Registration failed.")
                );
                return;
            }

            // Store only the email needed by the OTP page.
            // Do not store the password.
            sessionStorage.setItem("verification_email", email);

            // Preserve account type for the UI if needed.
            sessionStorage.setItem(
                "verification_account_type",
                accountType
            );

            showMessage(
                message,
                "Account created. Redirecting to email verification...",
                "success"
            );

            window.location.href = "verify-email.html";
        } catch (error) {
            console.error("Registration error:", error);
            showMessage(message, error.message || "Registration failed.");
        } finally {
            setButtonLoading(
                registerButton,
                false,
                "Creating account...",
                "Create Account"
            );
        }
    });
}


// ============================================================
// VERIFY EMAIL OTP
// Endpoint: POST /api/auth/verify-otp
// ============================================================

const verifyForm = document.getElementById("verifyForm");

if (verifyForm) {
    const email = sessionStorage.getItem("verification_email");
    const emailText = document.getElementById("emailText");
    const otpInput = document.getElementById("otp");
    const verifyButton = verifyForm.querySelector(
        'button[type="submit"]'
    );

    if (emailText) {
        emailText.textContent = email
            ? `Enter the 6-digit OTP sent to ${email}.`
            : "No verification email was selected. Please register again or use the verification link on the login page.";
    }

    verifyForm.addEventListener("submit", async event => {
        event.preventDefault();

        const message = document.getElementById("verifyMessage");
        const otp = otpInput?.value.trim() || "";

        if (!email) {
            showMessage(
                message,
                "Verification email is missing. Return to registration or enter your email from the login page."
            );
            return;
        }

        if (!/^\d{6}$/.test(otp)) {
            showMessage(message, "Enter a valid 6-digit OTP.");
            return;
        }

        setButtonLoading(
            verifyButton,
            true,
            "Verifying...",
            "Verify Email"
        );

        try {
            const { response, data } = await apiRequest("/verify-otp", {
                method: "POST",
                body: JSON.stringify({ email, otp })
            });

            if (!response.ok) {
                showMessage(
                    message,
                    getErrorMessage(
                        data,
                        "Verification failed. Check the OTP and try again."
                    )
                );
                return;
            }

            showMessage(
                message,
                "Email verified successfully. Redirecting to login...",
                "success"
            );

            sessionStorage.removeItem("verification_email");
            sessionStorage.removeItem("verification_account_type");

            window.setTimeout(() => {
                window.location.href = "login.html";
            }, 1200);
        } catch (error) {
            console.error("OTP verification error:", error);
            showMessage(message, error.message || "Verification failed.");
        } finally {
            setButtonLoading(
                verifyButton,
                false,
                "Verifying...",
                "Verify Email"
            );
        }
    });

    // Resend OTP
    const resendButton = document.getElementById("resendButton");

    resendButton?.addEventListener("click", async () => {
        const message = document.getElementById("verifyMessage");

        if (!email) {
            showMessage(message, "Verification email is missing.");
            return;
        }

        resendButton.disabled = true;
        resendButton.textContent = "Sending...";

        try {
            const { response, data } = await apiRequest("/resend-otp", {
                method: "POST",
                body: JSON.stringify({ email })
            });

            if (!response.ok) {
                showMessage(
                    message,
                    getErrorMessage(data, "Unable to resend OTP.")
                );
                return;
            }

            showMessage(
                message,
                data.message || "A new OTP has been sent.",
                "success"
            );
        } catch (error) {
            console.error("Resend OTP error:", error);
            showMessage(message, error.message || "Unable to resend OTP.");
        } finally {
            resendButton.disabled = false;
            resendButton.textContent = "Resend OTP";
        }
    });
}


// ============================================================
// LOGIN
// Endpoint: POST /api/auth/login
// Fallback: GET /api/auth/me
// ============================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    const emailInput = document.getElementById("loginEmail");
    const passwordInput = document.getElementById("loginPassword");
    const loginButton = document.getElementById("loginButton");

    // Show/hide password.
    const passwordToggle = document.getElementById("passwordToggle");
    const eyeOpen = document.getElementById("eyeOpen");
    const eyeClosed = document.getElementById("eyeClosed");

    passwordToggle?.addEventListener("click", () => {
        const showing = passwordInput?.type === "password";

        if (passwordInput) {
            passwordInput.type = showing ? "text" : "password";
        }

        passwordToggle.setAttribute(
            "aria-label",
            showing ? "Hide password" : "Show password"
        );

        if (eyeOpen) eyeOpen.hidden = showing;
        if (eyeClosed) eyeClosed.hidden = !showing;
    });

    loginForm.addEventListener("submit", async event => {
        event.preventDefault();

        const message = document.getElementById("loginMessage");
        const email = emailInput?.value.trim().toLowerCase() || "";
        const password = passwordInput?.value || "";

        if (!email || !password) {
            showMessage(message, "Enter your email and password.");
            return;
        }

        setButtonLoading(loginButton, true, "Signing in...", "Sign in");
        showMessage(message, "Signing in...", "success");

        try {
            const { response, data } = await apiRequest("/login", {
                method: "POST",
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                if (data.requires_verification) {
                    sessionStorage.setItem(
                        "verification_email",
                        data.email || email
                    );

                    window.location.href = "verify-email.html";
                    return;
                }

                showMessage(
                    message,
                    getErrorMessage(data, "Login failed.")
                );
                return;
            }

            // Prefer the server's login response.
            let accountType = normalizeAccountType(data.account || data.user || data);

            // If login doesn't include the role, ask the server.
            if (!accountType) {
                const { response: meResponse, data: meData } =
                    await apiRequest("/me", { method: "GET" });

                if (!meResponse.ok) {
                    showMessage(
                        message,
                        "Login succeeded, but the session could not be verified. Please try again."
                    );
                    return;
                }

                accountType = normalizeAccountType(
                    meData.account || meData.user || meData
                );
            }

            showMessage(message, "Login successful. Opening your dashboard...", "success");

            // These paths match your provided frontend folder structure.
            if (accountType === "artisan") {
                window.location.replace("artisan/index.html");
                return;
            }

            if (accountType === "buyer") {
                window.location.replace("buyer/buyer_dashboard.html");
                return;
            }

            // Never guess which dashboard to open.
            showMessage(
                message,
                "Your session is active, but the server did not return a valid account type. Check the /api/auth/me response."
            );
        } catch (error) {
            console.error("Login error:", error);
            showMessage(message, error.message || "Unable to sign in.");
        } finally {
            setButtonLoading(loginButton, false, "Signing in...", "Sign in");
        }
    });
}


// ============================================================
// VERIFY LINK FROM LOGIN PAGE
// ============================================================

const verifyLink = document.getElementById("verifyLink");

if (verifyLink) {
    verifyLink.addEventListener("click", event => {
        event.preventDefault();

        const email = document
            .getElementById("loginEmail")
            ?.value.trim()
            .toLowerCase();

        if (!email) {
            showMessage(
                document.getElementById("loginMessage"),
                "Enter your email first, then click Verify."
            );
            document.getElementById("loginEmail")?.focus();
            return;
        }

        sessionStorage.setItem("verification_email", email);
        window.location.href = "verify-email.html";
    });
}
