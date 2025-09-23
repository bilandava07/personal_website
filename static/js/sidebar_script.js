const sidebar_toggle = document.getElementById("sidebar_toggle");

sidebar_toggle.addEventListener("click", () => {
  sidebar.classList.toggle("show_sidebar");
  sidebar_toggle.classList.toggle("show_sidebar");
});

// Close sidebar when clicking outside
document.addEventListener("click", (e) => {
  if (sidebar.classList.contains("show_sidebar") &&
      sidebar_toggle.classList.contains("show_sidebar") &&
      !sidebar.contains(e.target) &&
      !sidebar_toggle.contains(e.target) &&
      !theme_switch.contains(e.target)) {
    sidebar.classList.remove("show_sidebar");
    sidebar_toggle.classList.remove("show_sidebar");
  }
});