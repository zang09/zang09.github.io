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

  const publicationPreviews = document.querySelectorAll('img[data-play-on-hover="true"]');
  const preloadedAnimatedPreviews = new Set();

  const preloadAnimatedPreview = (animatedSrc) => {
    if (!animatedSrc || preloadedAnimatedPreviews.has(animatedSrc)) {
      return;
    }

    preloadedAnimatedPreviews.add(animatedSrc);

    const preloadImage = new Image();
    preloadImage.src = animatedSrc;
  };

  const scheduleAnimatedPreviewPreload = (animatedSrc) => {
    if ("requestIdleCallback" in window) {
      window.requestIdleCallback(() => preloadAnimatedPreview(animatedSrc), { timeout: 2000 });
      return;
    }

    window.setTimeout(() => preloadAnimatedPreview(animatedSrc), 300);
  };

  publicationPreviews.forEach((preview) => {
    const staticSrc = preview.dataset.staticSrc;
    const animatedSrc = preview.dataset.animatedSrc;
    const publicationRow = preview.closest(".row");

    if (!staticSrc || !animatedSrc) {
      return;
    }

    scheduleAnimatedPreviewPreload(animatedSrc);

    const playPreview = () => {
      if (preview.src !== animatedSrc) {
        preview.src = animatedSrc;
      }
    };

    const stopPreview = () => {
      if (preview.src !== staticSrc) {
        preview.src = staticSrc;
      }
    };

    preview.addEventListener("mouseenter", playPreview);
    preview.addEventListener("mouseleave", stopPreview);
    preview.addEventListener("focus", playPreview);
    preview.addEventListener("blur", stopPreview);

    if (publicationRow) {
      publicationRow.addEventListener("mouseenter", playPreview);
      publicationRow.addEventListener("mouseleave", stopPreview);
      publicationRow.addEventListener("focusin", playPreview);
      publicationRow.addEventListener("focusout", (event) => {
        if (!publicationRow.contains(event.relatedTarget)) {
          stopPreview();
        }
      });
    }
  });
});
