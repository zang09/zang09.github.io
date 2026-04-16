$(document).ready(function () {
  // add toggle functionality to abstract, award and bibtex buttons
  $("a.abstract").click(function () {
    $(this).parent().parent().find(".abstract.hidden").toggleClass("open");
    $(this).parent().parent().find(".award.hidden.open").toggleClass("open");
    $(this).parent().parent().find(".bibtex.hidden.open").toggleClass("open");
  });
  $("a.award").click(function () {
    $(this).parent().parent().find(".abstract.hidden.open").toggleClass("open");
    $(this).parent().parent().find(".award.hidden").toggleClass("open");
    $(this).parent().parent().find(".bibtex.hidden.open").toggleClass("open");
  });
  $("a.bibtex").click(function () {
    $(this).parent().parent().find(".abstract.hidden.open").toggleClass("open");
    $(this).parent().parent().find(".award.hidden.open").toggleClass("open");
    $(this).parent().parent().find(".bibtex.hidden").toggleClass("open");
  });
  $("a").removeClass("waves-effect waves-light");

  // bootstrap-toc
  if ($("#toc-sidebar").length) {
    // remove related publications years from the TOC
    $(".publications h2").each(function () {
      $(this).attr("data-toc-skip", "");
    });
    var navSelector = "#toc-sidebar";
    var $myNav = $(navSelector);
    Toc.init($myNav);
    $("body").scrollspy({
      target: navSelector,
    });
  }

  // add css to jupyter notebooks
  const cssLink = document.createElement("link");
  cssLink.href = "../css/jupyter.css";
  cssLink.rel = "stylesheet";
  cssLink.type = "text/css";

  let jupyterTheme = determineComputedTheme();

  $(".jupyter-notebook-iframe-container iframe").each(function () {
    $(this).contents().find("head").append(cssLink);

    if (jupyterTheme == "dark") {
      $(this).bind("load", function () {
        $(this).contents().find("body").attr({
          "data-jp-theme-light": "false",
          "data-jp-theme-name": "JupyterLab Dark",
        });
      });
    }
  });

  // trigger popovers
  $('[data-toggle="popover"]').popover({
    trigger: "hover",
  });

  const publicationPreviews = document.querySelectorAll('[data-play-on-hover="true"]');
  const preloadedAnimatedPreviews = new Set();

  const preloadAnimatedPreview = (preview) => {
    if (preview.dataset.previewType === "video") {
      if (preloadedAnimatedPreviews.has(preview.currentSrc || preview.poster || preview.outerHTML)) {
        return;
      }

      preloadedAnimatedPreviews.add(preview.currentSrc || preview.poster || preview.outerHTML);
      preview.preload = "auto";
      preview.load();
      return;
    }

    const animatedSrc = preview.dataset.animatedSrc;
    if (!animatedSrc || preloadedAnimatedPreviews.has(animatedSrc)) {
      return;
    }

    preloadedAnimatedPreviews.add(animatedSrc);

    const preloadImage = new Image();
    preloadImage.src = animatedSrc;
  };

  const scheduleAnimatedPreviewPreload = (preview) => {
    if ("requestIdleCallback" in window) {
      window.requestIdleCallback(() => preloadAnimatedPreview(preview), { timeout: 2000 });
      return;
    }

    window.setTimeout(() => preloadAnimatedPreview(preview), 300);
  };

  publicationPreviews.forEach((preview) => {
    const publicationRow = preview.closest(".row");
    const hoverTarget = publicationRow || preview;
    const isVideoPreview = preview.dataset.previewType === "video";
    const previewMedia = preview.closest(".preview-media");
    const staticSrc = preview.dataset.staticSrc;
    const animatedSrc = preview.dataset.animatedSrc;

    if (!isVideoPreview && (!staticSrc || !animatedSrc)) {
      return;
    }

    scheduleAnimatedPreviewPreload(preview);

    const playPreview = () => {
      if (isVideoPreview) {
        if (previewMedia) {
          previewMedia.classList.add("is-playing");
        }
        preview.play().catch(() => {});
        return;
      }

      if (preview.src !== animatedSrc) {
        preview.src = animatedSrc;
      }
    };

    const stopPreview = () => {
      if (isVideoPreview) {
        preview.pause();
        preview.currentTime = 0;
        if (previewMedia) {
          previewMedia.classList.remove("is-playing");
        }
        return;
      }

      if (preview.src !== staticSrc) {
        preview.src = staticSrc;
      }
    };

    hoverTarget.addEventListener("mouseenter", playPreview);
    hoverTarget.addEventListener("mouseleave", stopPreview);
    hoverTarget.addEventListener("focusin", playPreview);
    hoverTarget.addEventListener("focusout", (event) => {
      if (!hoverTarget.contains(event.relatedTarget)) {
        stopPreview();
      }
    });
  });
});
