/* Cieli Travel — interações (sem dependências além do lottie-web local) */
(function () {
  "use strict";

  /* Header: transparente no topo, sólido ao rolar, esconde ao descer */
  var header = document.querySelector(".site-header");
  if (header) {
    var lastY = 0;
    var onScroll = function () {
      var y = window.scrollY;
      header.classList.toggle("scrolled", y > 40);
      if (y > 300 && y > lastY + 4) header.classList.add("hidden");
      else if (y < lastY - 4 || y < 300) header.classList.remove("hidden");
      lastY = y;
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

  /* Carrosséis: botões prev/next + tabs DIA n */
  document.querySelectorAll("[data-rail]").forEach(function (wrap) {
    var rail = wrap.querySelector(".rail");
    var slideW = function () {
      return rail.firstElementChild
        ? rail.firstElementChild.getBoundingClientRect().width + 22 : 320;
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
            left: +tab.dataset.slide * rail.firstElementChild
              .getBoundingClientRect().width,
            behavior: "smooth"
          });
        });
      });
      rail.addEventListener("scroll", function () {
        var i = Math.round(rail.scrollLeft /
          rail.firstElementChild.getBoundingClientRect().width);
        tabs.forEach(function (t, k) {
          t.classList.toggle("active", k === i);
        });
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

  /* Rotator do hero: palavras empilhadas rolando verticalmente */
  var rot = document.querySelector("[data-rotator]");
  if (rot) {
    var words = JSON.parse(rot.dataset.rotator);
    var track = document.createElement("span");
    track.className = "words-track";
    // duplica para looping suave
    words.concat(words.slice(0, 2)).forEach(function (w) {
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
      track.style.transform =
        "translateY(" + (-(idx - 2) * lineH()) + "px)";
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

  /* Fade-in suave (threshold 0 — funciona p/ seções altas) */
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

  /* ---------- Seção pinada "Nosso jeito": lottie scrub + mensagens ---------- */
  var pinned = document.querySelector(".pinned");
  if (pinned && window.matchMedia("(min-width: 769px)").matches) {
    var msgs = pinned.querySelectorAll(".pinned-msg");
    var media = pinned.querySelector(".pinned-media");
    var anim = null;
    if (media && media.dataset.lottie && window.lottie) {
      anim = window.lottie.loadAnimation({
        container: media,
        renderer: "svg",
        loop: false,
        autoplay: false,
        path: media.dataset.lottie,
        rendererSettings: { preserveAspectRatio: "xMidYMid slice" }
      });
    }
    var onPin = function () {
      var r = pinned.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var p = Math.min(1, Math.max(0, -r.top / total));
      if (anim && anim.totalFrames) {
        anim.goToAndStop(p * (anim.totalFrames - 1), true);
      }
      var seg = Math.min(msgs.length - 1, Math.floor(p * msgs.length));
      msgs.forEach(function (m, i) { m.classList.toggle("active", i === seg); });
    };
    window.addEventListener("scroll", onPin, { passive: true });
    onPin();
  } else if (pinned) {
    pinned.querySelectorAll(".pinned-msg").forEach(function (m) {
      m.classList.add("active");
    });
  }

  /* ---------- Especialidades: carrossel horizontal pinado ---------- */
  var specials = document.querySelector(".specials");
  if (specials && window.matchMedia("(min-width: 769px)").matches) {
    var track = specials.querySelector(".specials-track");
    var onSpec = function () {
      var r = specials.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var p = Math.min(1, Math.max(0, -r.top / total));
      var max = track.scrollWidth - window.innerWidth;
      track.style.transform = "translateX(" + (-p * max) + "px)";
    };
    window.addEventListener("scroll", onSpec, { passive: true });
    onSpec();
  }

  /* Motion effects: parallax sutil dos cards ao rolar (como o Elementor) */
  var fxCards = document.querySelectorAll(".card-trip, .photo-card");
  if (fxCards.length) {
    var fxTick = false;
    var applyFx = function () {
      fxTick = false;
      var vh = window.innerHeight;
      fxCards.forEach(function (el, i) {
        var r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        /* progresso -1..1 do centro do card na viewport */
        var p = (r.top + r.height / 2 - vh / 2) / (vh / 2);
        var speed = 18 + (i % 3) * 14;   /* colunas com velocidades diferentes */
        el.style.transform = "translateY(" + (p * speed).toFixed(1) + "px)";
      });
    };
    window.addEventListener("scroll", function () {
      if (!fxTick) { fxTick = true; requestAnimationFrame(applyFx); }
    }, { passive: true });
    applyFx();
  }

  /* Vídeos de fundo: play/pause conforme visibilidade (economia) */
  if ("IntersectionObserver" in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { v.play && v.play().catch(function () {}); }
        else { v.pause && v.pause(); }
      });
    }, { threshold: 0.05 });
    document.querySelectorAll("video[autoplay]").forEach(function (v) { vio.observe(v); });
  }
})();
