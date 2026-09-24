(function () {
  "use strict";

  /* ---------- theme toggle ---------- */
  var root = document.documentElement;
  var toggle = document.getElementById("theme-toggle");
  var mq = window.matchMedia("(prefers-color-scheme: dark)");

  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return mq.matches ? "dark" : "light";
  }
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
    });
  }

  /* ---------- de-obfuscate email ---------- */
  document.querySelectorAll(".obf").forEach(function (el) {
    var addr = el.getAttribute("data-user") + "@" + el.getAttribute("data-domain");
    var a = document.createElement("a");
    a.href = "mailto:" + addr;
    a.textContent = addr;
    el.replaceWith(a);
  });

  /* ---------- hover / tap video previews ---------- */
  var canHover = window.matchMedia("(hover: hover)").matches;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".pub-media").forEach(function (box) {
    var video = box.querySelector("video");
    if (!video) return;

    function play() {
      if (reduced) return;
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
      box.classList.add("playing");
    }
    function stop() {
      video.pause();
      video.currentTime = 0;
      box.classList.remove("playing");
    }

    if (canHover) {
      var card = box.closest(".pub") || box;
      card.addEventListener("mouseenter", play);
      card.addEventListener("mouseleave", stop);
      box.addEventListener("focusin", play);
      box.addEventListener("focusout", stop);
    } else {
      // Touch devices: tap the thumbnail to play/pause; the title still opens the project.
      box.classList.add("tap-to-play");
      box.removeAttribute("aria-hidden");
      box.setAttribute("tabindex", "0");
      box.setAttribute("role", "button");
      box.setAttribute("aria-label", "Play preview");
      box.addEventListener("click", function (ev) {
        ev.preventDefault();
        if (box.classList.contains("playing")) stop();
        else play();
      });
      if ("IntersectionObserver" in window) {
        // Pause when scrolled away so only the visible preview plays.
        new IntersectionObserver(
          function (entries) {
            entries.forEach(function (e) {
              if (!e.isIntersecting) stop();
            });
          },
          { threshold: 0.2 },
        ).observe(box);
      }
    }
  });

  /* ---------- disclosure toggles (BibTeX, full bio) ---------- */
  document.querySelectorAll(".bib-toggle, .bio-toggle").forEach(function (btn) {
    var target = document.getElementById(btn.getAttribute("aria-controls"));
    if (!target) return;
    var cls = btn.getAttribute("data-toggle-class");
    // Either toggle the target itself, or every descendant carrying data-toggle-class.
    var nodes = cls ? target.querySelectorAll("." + cls) : [target];
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      nodes.forEach(function (n) {
        n.hidden = open;
        if (!open) {
          // Safari does not always fetch images that were inside a hidden element.
          n.querySelectorAll("img").forEach(function (img) {
            if (!img.complete || img.naturalWidth === 0) {
              img.loading = "eager";
              img.setAttribute("src", img.getAttribute("src"));
            }
          });
        }
      });
    });
  });
})();
