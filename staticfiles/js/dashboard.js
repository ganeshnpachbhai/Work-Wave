/**
 * WorkWave — Dashboard & Interactive UI Script
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile Sidebar Toggle
    const sidebar = document.querySelector(".dashboard-sidebar");
    const overlay = document.querySelector(".sidebar-overlay");
    const toggleBtns = document.querySelectorAll(".sidebar-toggle-btn");
    const closeBtns = document.querySelectorAll(".sidebar-close-btn");

    function openSidebar() {
        if (sidebar) sidebar.classList.add("show");
        if (overlay) overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove("show");
        if (overlay) overlay.classList.remove("active");
        document.body.style.overflow = "";
    }

    toggleBtns.forEach((btn) => btn.addEventListener("click", openSidebar));
    closeBtns.forEach((btn) => btn.addEventListener("click", closeSidebar));
    if (overlay) overlay.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && sidebar && sidebar.classList.contains("show")) {
            closeSidebar();
        }
    });

    // 2. Role Selector & Dynamic Field Visibility for Signup
    const roleRadios = document.querySelectorAll('input[name="role"]');
    const roleCards = document.querySelectorAll(".role-card");
    const companyGroup = document.getElementById("company-name-group");
    const companyInput = document.querySelector('input[name="company_name"]');

    function updateRoleUI(selectedRole) {
        roleCards.forEach((card) => {
            const cardRole = card.dataset.role;
            if (cardRole === selectedRole) {
                card.classList.add("selected");
                const radio = card.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;
            } else {
                card.classList.remove("selected");
            }
        });

        if (companyGroup) {
            if (selectedRole === "employer") {
                companyGroup.style.display = "block";
                if (companyInput) companyInput.setAttribute("required", "required");
            } else {
                companyGroup.style.display = "none";
                if (companyInput) companyInput.removeAttribute("required");
            }
        }
    }

    roleCards.forEach((card) => {
        card.addEventListener("click", () => {
            const role = card.dataset.role;
            const radio = document.querySelector(`input[name="role"][value="${role}"]`);
            if (radio) {
                radio.checked = true;
                updateRoleUI(role);
            }
        });
    });

    roleRadios.forEach((radio) => {
        radio.addEventListener("change", (e) => {
            updateRoleUI(e.target.value);
        });
    });

    // Initial role check
    const checkedRole = document.querySelector('input[name="role"]:checked');
    if (checkedRole) {
        updateRoleUI(checkedRole.value);
    } else {
        // Default to seeker if none selected
        updateRoleUI("seeker");
    }
});
