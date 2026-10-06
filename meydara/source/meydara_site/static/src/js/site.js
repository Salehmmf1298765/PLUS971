/** @odoo-module **/
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function initializeMeydara() {
    if (!document.documentElement.classList.contains("meydara-new")) return;
    document.querySelectorAll("[data-md-tour]").forEach((tour) => {
        if (tour.dataset.initialized) return;
        tour.dataset.initialized = "true";
        const buttons = [...tour.querySelectorAll("[data-md-step]")];
        const panels = [...tour.querySelectorAll("[data-md-panel]")];
        const singleImage = tour.querySelector("[data-md-tour-image]");
        const singleImageSteps = [
            ["/meydara_site/static/src/img/product/reference/visits.png", "Midara daily visits and route"],
            ["/meydara_site/static/src/img/product/reference/customers.png", "Midara customer 360 context"],
            ["/meydara_site/static/src/img/product/reference/mobile-reports.png", "Midara mobile reports"],
        ];
        let switchTimer;
        function applySelection(index) {
            buttons.forEach((button, i) => {
                button.classList.toggle("is-active", i === index);
                button.setAttribute("aria-pressed", String(i === index));
            });
            panels.forEach((panel, i) => { panel.hidden = i !== index; });
            if (singleImage && singleImageSteps[index]) {
                singleImage.src = singleImageSteps[index][0];
                singleImage.alt = singleImageSteps[index][1];
            }
        }
        function select(index, animate = true) {
            window.clearTimeout(switchTimer);
            if (!animate || reducedMotion.matches) {
                applySelection(index);
                return;
            }
            tour.classList.add("is-switching");
            switchTimer = window.setTimeout(() => {
                applySelection(index);
                requestAnimationFrame(() => tour.classList.remove("is-switching"));
            }, 85);
        }
        buttons.forEach((button, i) => button.addEventListener("click", () => select(i)));
        tour.classList.add("is-ready");
        select(0, false);
    });
    if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
        document.querySelectorAll(".mw-module-card").forEach((card) => {
            card.addEventListener("pointermove", (event) => {
                const box = card.getBoundingClientRect();
                card.style.setProperty("--mx", `${((event.clientX - box.left) / box.width) * 100}%`);
                card.style.setProperty("--my", `${((event.clientY - box.top) / box.height) * 100}%`);
            });
            card.addEventListener("pointerleave", () => {
                card.style.setProperty("--mx", "50%");
                card.style.setProperty("--my", "50%");
            });
        });
    }
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initializeMeydara);
else initializeMeydara();
