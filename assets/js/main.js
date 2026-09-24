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

  /* ---------- hover / tap video previews ---------- */
  var canHover = window.matchMedia("(hover: hover)").matches;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".pub-media").forEach(function (box) {
    var video = box.querySelector("video");
    if (!video) return;

    function play() {
      if (reduced) return;
      if (video.preload === "none") video.preload = "auto";
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
      box.addEventListener("mouseenter", play);
      box.addEventListener("mouseleave", stop);
      var pub = box.closest(".pub");
      if (pub) {
        var title = pub.querySelector(".pub-title a");
        if (title) {
          title.addEventListener("mouseenter", play);
          title.addEventListener("mouseleave", stop);
        }
      }
    } else if (!reduced && "IntersectionObserver" in window) {
      // On touch devices, autoplay while the thumbnail is mostly visible.
      var io = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting) play();
            else stop();
          });
        },
        { threshold: 0.6 },
      );
      io.observe(box);
    }
  });

  /* ---------- disclosure toggles (BibTeX, full bio) ---------- */
  document.querySelectorAll(".bib-toggle, .bio-toggle").forEach(function (btn) {
    var target = document.getElementById(btn.getAttribute("aria-controls"));
    if (!target) return;
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      target.hidden = open;
    });
  });
})();
