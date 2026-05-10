(function () {
  function hidePostHeaders() {
    document.querySelectorAll(".post-header").forEach(function (el) {
      el.hidden = true;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", hidePostHeaders);
  } else {
    hidePostHeaders();
  }
})();
