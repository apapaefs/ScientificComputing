document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form.bd-search").forEach((form) => {
    // If there's already a submit control, do nothing
    const hasSubmit = form.querySelector('button[type="submit"], input[type="submit"], input[type="image"]');
    if (hasSubmit) return;

    const btn = document.createElement("button");
    btn.type = "submit";
    btn.className = "visually-hidden"; // Bootstrap-compatible
    btn.textContent = "Search";
    form.appendChild(btn);
  });
});
