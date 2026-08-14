/* Cieli Travel — interações (Lenis + lottie-web self-hosted, sem jQuery) */
(function () {
  "use strict";

  var isDesktop = window.matchMedia("(min-width: 769px)").matches;

  /* Smooth scroll (Lenis) — mesma configuração do site original.
     No touch/mobile o Lenis mantém o scroll nativo (como no original). */
  if (window.Lenis) {
    try {
      window.lenisInstance = new Lenis({
        autoRaf: true,
        lerp: 0.1,
        duration: 1.2,
        wheelMultiplier: 1,
        easing: function (x) {
          return Math.min(1, 1.001 - Math.pow(2, -10 * x));
        }
      });
    } catch (e) { /* segue com scroll nativo */ }
  }

  /* Header: sólido ao rolar; esconde descendo, mostra subindo */
  var header = document.querySelector(".site-header");
  var lastHeadY = 0;
  function headerTick(y) {
    if (!header) return;
    header.classList.toggle("scrolled", y > 40);
    if (y > 300 && y > lastHeadY + 2) header.classList.add("hidden");
    else if (y < lastHeadY - 2 || y < 300) header.classList.remove("hidden");
    lastHeadY = y;
  }

  /* Menu-gaveta (hambúrguer) */
  var burger = document.querySelector(".hamburger");
  var overlay = document.querySelector(".overlay-menu");
  if (burger && overlay) {
    var setMenu = function (open) {
      overlay.classList.toggle("open", open);
      overlay.setAttribute("aria-hidden", open ? "false" : "true");
      document.body.style.overflow = open ? "hidden" : "";
    };
    burger.addEventListener("click", function () { setMenu(true); });
    overlay.querySelectorAll(".overlay-close").forEach(function (b) {
      b.addEventListener("click", function () { setMenu(false); });
    });
    overlay.querySelector(".menu-backdrop")
      .addEventListener("click", function () { setMenu(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setMenu(false);
    });
    var search = overlay.querySelector("[data-sitesearch]");
    if (search) {
      search.addEventListener("submit", function (e) {
        e.preventDefault();
        var q = search.querySelector("input").value.trim();
        if (q) {
          location.href = "https://www.google.com/search?q=" +
            encodeURIComponent("site:cielitravel.com " + q);
        }
      });
    }
  }

  /* Carrosséis: prev/next + tabs DIA n */
  document.querySelectorAll("[data-rail]").forEach(function (wrap) {
    var rail = wrap.querySelector(".rail");
    if (!rail) return;
    var slideW = function () {
      return rail.firstElementChild
        ? rail.firstElementChild.getBoundingClientRect().width + 20 : 320;
    };
    wrap.querySelectorAll("[data-dir]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        rail.scrollBy({
          left: btn.dataset.dir === "next" ? slideW() : -slideW(),
          behavior: "smooth"
        });
      });
    });
    var tabs = wrap.querySelectorAll("[data-slide]");
    if (tabs.length) {
      tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
          rail.scrollTo({
            left: +tab.dataset.slide *
              rail.firstElementChild.getBoundingClientRect().width,
            behavior: "smooth"
          });
        });
      });
      rail.addEventListener("scroll", function () {
        var i = Math.round(rail.scrollLeft /
          rail.firstElementChild.getBoundingClientRect().width);
        tabs.forEach(function (t, k) { t.classList.toggle("active", k === i); });
      }, { passive: true });
      tabs[0].classList.add("active");
    }
  });

  /* Typewriter */
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
            setTimeout(tick, 55);
          } else {
            el.classList.add("done");
          }
        })();
      });
    }, { threshold: 0.4 });
    typeEls.forEach(function (el) { io.observe(el); });
  }

  /* Rotator do hero: pilha de palavras (atual centrada, vizinhas a 25%) */
  var rot = document.querySelector("[data-rotator]");
  if (rot) {
    var words = JSON.parse(rot.dataset.rotator);
    var track = document.createElement("span");
    track.className = "words-track";
    words.concat(words.slice(0, 4)).forEach(function (w) {
      var s = document.createElement("span");
      s.textContent = w;
      track.appendChild(s);
    });
    rot.appendChild(track);
    var spans = track.children;
    var idx = 0;
    var lineH = function () { return spans[0].getBoundingClientRect().height; };
    var apply = function (animate) {
      if (!animate) track.style.transition = "none";
      track.style.transform = "translateY(" + (-(idx - 1) * lineH()) + "px)";
      if (!animate) { void track.offsetWidth; track.style.transition = ""; }
      for (var i = 0; i < spans.length; i++) {
        spans[i].classList.toggle("cur", i === idx);
      }
    };
    apply(false);
    setInterval(function () {
      idx += 1;
      apply(true);
      if (idx >= words.length) {
        setTimeout(function () { idx = 0; apply(false); }, 650);
      }
    }, 2600);
  }

  /* Fade-in das seções */
  if ("IntersectionObserver" in window) {
    var fio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.style.opacity = 1;
          e.target.style.transform = "none";
          fio.unobserve(e.target);
        }
      });
    }, { threshold: 0, rootMargin: "0px 0px -60px 0px" });
    document.querySelectorAll(".section > .container, .quote, .facts").forEach(function (el) {
      el.style.opacity = 0;
      el.style.transform = "translateY(24px)";
      el.style.transition = "opacity .7s ease, transform .7s ease";
      fio.observe(el);
    });
  }

  /* ============================================================
     Loop rAF único: inércia dos cards + scrubs suavizados
     (replica o conjunto lenis + inertiaScroll + ScrollTrigger
     scrub:1.5 do site original)
     ============================================================ */
  var pinned = document.querySelector(".pinned");
  var pinnedMsgs = pinned ? pinned.querySelectorAll(".pinned-msg") : [];
  var lotAnim = null;
  if (pinned && isDesktop) {
    var media = pinned.querySelector(".pinned-media");
    if (media && media.dataset.lottie && window.lottie) {
      lotAnim = window.lottie.loadAnimation({
        container: media,
        renderer: "svg",
        loop: false,
        autoplay: false,
        path: media.dataset.lottie,
        rendererSettings: { preserveAspectRatio: "xMidYMid slice" }
      });
    }
  } else if (pinned) {
    pinnedMsgs.forEach(function (m) { m.classList.add("active"); });
  }

  var specials = document.querySelector(".specials");
  var specTrack = specials ? specials.querySelector(".specials-track") : null;

  var fxCards = [].slice.call(
    document.querySelectorAll(".card-trip, .photo-card"));

  var lastY = window.scrollY;
  var smoothV = 0;       // velocidade suavizada (inércia dos cards)
  var lotCur = 0;        // progresso suavizado do lottie (scrub 1.5)
  var specCur = 0;       // progresso suavizado das especialidades

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  function frame() {
    var y = window.scrollY;
    var v = y - lastY;
    lastY = y;
    headerTick(y);

    /* Cards: deslocam com a VELOCIDADE do scroll e voltam a 0 em repouso */
    smoothV += (clamp(v, -60, 60) - smoothV) * 0.1;
    if (Math.abs(smoothV) > 0.05 || true) {
      var vh = window.innerHeight;
      for (var i = 0; i < fxCards.length; i++) {
        var el = fxCards[i];
        var r = el.getBoundingClientRect();
        if (r.bottom < -80 || r.top > vh + 80) continue;
        var k = [0.55, 0.85, 1.2][i % 3];
        el.style.transform =
          "translateY(" + (-smoothV * k * 1.6).toFixed(2) + "px)";
      }
    }

    /* Lottie pinado: persegue o scroll com atraso (scrub ~1.5) */
    if (pinned && isDesktop) {
      var pr = pinned.getBoundingClientRect();
      var total = pr.height - window.innerHeight;
      var target = clamp(-pr.top / total, 0, 1);
      lotCur += (target - lotCur) * 0.06;
      if (lotAnim && lotAnim.totalFrames) {
        lotAnim.goToAndStop(lotCur * (lotAnim.totalFrames - 1), true);
      }
      var seg = Math.min(pinnedMsgs.length - 1,
        Math.floor(target * pinnedMsgs.length));
      pinnedMsgs.forEach(function (m, j) {
        m.classList.toggle("active", j === seg);
      });
    }

    /* Especialidades: deslize horizontal também suavizado */
    if (specTrack && isDesktop) {
      var sr = specials.getBoundingClientRect();
      var stotal = sr.height - window.innerHeight;
      var st = clamp(-sr.top / stotal, 0, 1);
      specCur += (st - specCur) * 0.09;
      var max = specTrack.scrollWidth - window.innerWidth;
      specTrack.style.transform =
        "translateX(" + (-specCur * max).toFixed(1) + "px)";
    }

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  /* Vídeos de fundo: play/pause conforme visibilidade */
  if ("IntersectionObserver" in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var vd = e.target;
        if (e.isIntersecting) { vd.play && vd.play().catch(function () {}); }
        else { vd.pause && vd.pause(); }
      });
    }, { threshold: 0.05 });
    document.querySelectorAll("video[autoplay]").forEach(function (vd) { vio.observe(vd); });
  }
})();
