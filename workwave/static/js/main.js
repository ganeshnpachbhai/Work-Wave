/**
 * WorkWave — Main JavaScript Application
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Navbar Scroll Effect
    const navbar = document.querySelector(".ww-navbar");
    if (navbar) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 20) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        });
    }

    // 2. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 3. Password Visibility Toggles
    document.querySelectorAll(".password-toggle-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.dataset.target;
            const input = targetId ? document.getElementById(targetId) : btn.closest(".input-password-wrap").querySelector("input");
            if (!input) return;

            const icon = btn.querySelector("i");
            if (input.type === "password") {
                input.type = "text";
                if (icon) {
                    icon.classList.remove("bi-eye");
                    icon.classList.add("bi-eye-slash");
                }
            } else {
                input.type = "password";
                if (icon) {
                    icon.classList.remove("bi-eye-slash");
                    icon.classList.add("bi-eye");
                }
            }
        });
    });

    // 4. CSRF Token Refresh for Form Submissions (e.g. Logout)
    document.querySelectorAll("[data-csrf-token-url]").forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const submitButton = form.querySelector('button[type="submit"]');
            const tokenInput = form.querySelector('input[name="csrfmiddlewaretoken"]');

            if (!tokenInput) {
                form.submit();
                return;
            }

            if (submitButton) {
                submitButton.disabled = true;
            }

            try {
                const response = await fetch(form.dataset.csrfTokenUrl, {
                    credentials: "same-origin",
                    headers: { "Accept": "application/json" }
                });
                if (!response.ok) {
                    throw new Error("Unable to refresh the security token.");
                }

                const data = await response.json();
                tokenInput.value = data.csrfToken;
                form.submit();
            } catch (error) {
                if (submitButton) {
                    submitButton.disabled = false;
                }
                window.alert("Action failed. Please refresh the page and try again.");
            }
        });
    });
});
