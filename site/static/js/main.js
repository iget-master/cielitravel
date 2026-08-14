/* Cieli Travel — interações mínimas (sem dependências) */
(function () {
  "use strict";

  /* Header: fundo sólido ao rolar */
  var header = document.querySelector(".site-header");
  if (header && !header.classList.contains("light")) {
    var onScroll = function () {
      header.classList.toggle("scrolled", window.scrollY > 40);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* Overlay do hambúrguer */
  var burger = document.querySelector(".hamburger");
  var overlay = document.querySelector(".overlay-menu");
  if (burger && overlay) {
    burger.addEventListener("click", function () { overlay.classList.add("open"); });
    overlay.querySelector(".overlay-close").addEventListener("click", function () {
      overlay.classList.remove("open");
    });
  }

  /* Carrosséis: botões prev/next rolam o trilho */
  document.querySelectorAll("[data-rail]").forEach(function (wrap) {
    var rail = wrap.querySelector(".rail");
    wrap.querySelectorAll("[data-dir]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var step = rail.firstElementChild
          ? rail.firstElementChild.getBoundingClientRect().width + 22 : 320;
        rail.scrollBy({
          left: btn.dataset.dir === "next" ? step : -step,
          behavior: "smooth"
        });
      });
    });
  });

  /* Typewriter (headline de destino e citações) */
  var typeEls = document.querySelectorAll("[data-typewriter]");
  if (typeEls.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var el = e.target;
        var full = el.dataset.typewriter;
        el.textContent = "";
        el.classList.add("typewriter");
        var i = 0;
        (function tick() {
          if (i <= full.length) {
            el.textContent = full.slice(0, i++);
            setTimeout(tick, 45);
          } else {
            el.classList.add("done");
          }
        })();
      });
    }, { threshold: 0.6 });
    typeEls.forEach(function (el) { io.observe(el); });
  }

  /* Rotator do hero da home (troca de destinos) */
  var rot = document.querySelector("[data-rotator]");
  if (rot) {
    var words = JSON.parse(rot.dataset.rotator);
    var idx = 0;
    rot.textContent = words[0];
    setInterval(function () {
      idx = (idx + 1) % words.length;
      rot.style.opacity = 0;
      setTimeout(function () {
        rot.textContent = words[idx];
        rot.style.opacity = 1;
      }, 300);
    }, 2400);
    rot.style.transition = "opacity .3s";
  }

  /* Fade-in suave das seções */
  if ("IntersectionObserver" in window) {
    var fio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.style.opacity = 1;
          e.target.style.transform = "none";
          fio.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll(".section > .container, .quote, .facts").forEach(function (el) {
      el.style.opacity = 0;
      el.style.transform = "translateY(24px)";
      el.style.transition = "opacity .7s ease, transform .7s ease";
      fio.observe(el);
    });
  }
})();
