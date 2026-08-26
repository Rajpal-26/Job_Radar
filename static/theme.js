/* ==============================================================================
 * WATERMARK: Rajpal Singh Tanwar
 * Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
 *
 * JobRadar Centralized Theme Engine
 * Synchronizes Light/Dark Mode seamlessly across all pages and components.
 * ============================================================================== */

(function () {
  // Enforce Dark Mode by default across all screens & tabs (override stale light theme)
  let savedTheme = localStorage.getItem("jobradar_theme");
  if (!savedTheme || savedTheme === "light") {
    savedTheme = "dark";
    localStorage.setItem("jobradar_theme", "dark");
  }
  document.documentElement.setAttribute("data-theme", savedTheme);

  // Sync UI components when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateThemeUI);
  } else {
    updateThemeUI();
  }
})();

function updateThemeUI() {
  const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
  const isDark = currentTheme === "dark";

  // Update theme label text
  document.querySelectorAll(".theme-label, #themeLabel").forEach(el => {
    if (el) el.textContent = isDark ? "Light Mode" : "Dark Mode";
  });

  // Update theme icons
  document.querySelectorAll(".theme-icon, #themeIcon").forEach(el => {
    if (el) el.textContent = isDark ? "☀️" : "🌙";
  });

  // Update simple theme buttons
  document.querySelectorAll("#themeBtn, .theme-btn").forEach(btn => {
    if (btn && !btn.querySelector(".theme-label")) {
      btn.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
    }
  });
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
  const newTheme = currentTheme === "light" ? "dark" : "light";

  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("jobradar_theme", newTheme);

  updateThemeUI();
}
