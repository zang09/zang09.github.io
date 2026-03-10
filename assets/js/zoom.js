// Initialize medium zoom.
$(document).ready(function () {
  const getZoomMargin = () => (window.matchMedia("(max-width: 576px)").matches ? 16 : 48);

  medium_zoom = mediumZoom("[data-zoomable]", {
    background: getComputedStyle(document.documentElement).getPropertyValue("--global-bg-color") + "ee", // + 'ee' for trasparency.
    margin: getZoomMargin(),
  });

  // Keep a small viewport margin so zoomed images do not touch screen edges.
  window.addEventListener("resize", function () {
    medium_zoom.update({ margin: getZoomMargin() });
  });
});
