# -*- coding: utf-8 -*-
"""Gerador estático do cielitravel.

content/*.md (+ assets/uploads) ──►  dist/  (HTML pronto para S3/CloudFront)

Uso:  py -3 scripts/build.py
Requisito:  py -3 -m pip install markdown
"""
import html as html_mod
import json
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown as md_lib
except ImportError:
    sys.exit("Falta o pacote 'markdown':  py -3 -m pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "site" / "static"
UPLOADS = ROOT / "assets" / "uploads"
VIDEOS = ROOT / "assets" / "videos"
DIST = ROOT / "dist"

MEDIA = {}
_mj = ROOT / "site" / "data" / "media.json"
if _mj.exists():
    MEDIA = json.loads(_mj.read_text(encoding="utf-8"))

CARDS = {}
_cj = ROOT / "site" / "data" / "cards.json"
if _cj.exists():
    CARDS = json.loads(_cj.read_text(encoding="utf-8"))


def card_photo(page_url, kind, title):
    """Foto de um card (hospedagem/experiência) pelo título."""
    rel = CARDS.get(page_url, {}).get(kind, {}).get(title.upper().strip())
    if rel and (UPLOADS / rel).exists():
        return "/uploads/" + rel
    # fallback: procura arquivo com nome parecido
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:18]
    for f in UPLOADS.glob("*/*/*.webp"):
        if slug and slug in f.name.lower():
            return f"/uploads/{f.relative_to(UPLOADS).as_posix()}"
    return ""


def emify(text):
    """*itálico* → <em>, preservando o resto escapado."""
    parts = re.split(r"\*([^*\n]+)\*", text)
    out = ""
    for i, p in enumerate(parts):
        out += f"<em>{esc(p)}</em>" if i % 2 else esc(p)
    return out

OG_BY_URL = {}  # /toscana/ -> uploads/... (preenchido no main)


def page_video(url, kind):
    """Vídeo da página por tipo: hero | cta | depoimentos | lottie."""
    pats = {"hero": r"Hero", "cta": r"CTA", "depoimentos": r"Depoimentos",
            "lottie": r"lottie.*\.json$|\.json$"}
    for rel in MEDIA.get(url, []):
        if kind == "lottie":
            if rel.endswith(".json"):
                return f"/videos/{rel}"
        elif rel.endswith((".mp4", ".webm")) and re.search(
                pats[kind], rel, re.I):
            return f"/videos/{rel}"
    return ""


def bg_video_tag(url, kind, poster=""):
    mp4 = page_video(url, kind)
    if not mp4:
        return ""
    webm = mp4.replace(".mp4", ".webm")
    has_webm = (VIDEOS / webm.replace("/videos/", "")).exists()
    srcs = (f'<source src="{webm}" type="video/webm">' if has_webm else "") \
        + f'<source src="{mp4}" type="video/mp4">'
    p = f' poster="{poster}"' if poster else ""
    return (f'<video class="bg-video" autoplay muted loop playsinline'
            f'{p}>{srcs}</video>')

DESTINOS = {
    "toscana", "sicilia", "veneza-e-verona", "sardenha", "puglia",
    "costa-amalfitana", "paris", "cote-dazur", "provence",
    "verao-na-italia", "inverno-na-italia", "verao-na-franca",
    "inverno-na-franca", "andrea-bocelli-na-toscana", "italia", "franca",
}

INK_SVG = (
    '<svg viewBox="0 0 14 30" xmlns="http://www.w3.org/2000/svg">'
    '<path fill="currentColor" d="M7 0C9.8 2.8 14 9.5 14 16.2 14 24 11 30 7 30 '
    "3 30 0 24 0 16.2 0 9.5 4.2 2.8 7 0Z\"/></svg>"
)

# --------------------------------------------------------------- util


def esc(s):
    return html_mod.escape(s, quote=True)


def md_html(text):
    return md_lib.markdown(text, extensions=["tables"])


def parse_front(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n?", raw, re.S)
    fm = {}
    body = raw
    if m:
        body = raw[m.end():]
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    return fm, body


def fix_uploads(html):
    return html.replace('src="uploads/', 'src="/uploads/').replace(
        "(uploads/", "(/uploads/")


def blocks_of(body):
    """Converte o corpo markdown espelhado em blocos (kind, text)."""
    out = []
    for chunk in re.split(r"\n\s*\n", body):
        t = chunk.strip()
        if not t:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", t, re.S)
        if m:
            out.append((f"h{len(m.group(1))}", m.group(2).strip()))
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)", t)
        if m:
            out.append(("img", m.group(2)))
            continue
        if t == "Ir para o conteúdo":
            continue
        out.append(("p", t))
    return out


# --------------------------------------------------------------- shell

FONTS = (
    '<link rel="preload" href="/static/fonts/Sfizia-Regular.woff2" as="font" '
    'type="font/woff2" crossorigin>'
    '<link rel="preload" href="/static/fonts/trade-gothic-next-compressed-700.woff2" '
    'as="font" type="font/woff2" crossorigin>'
    '<link rel="stylesheet" href="/static/css/fonts.css">'
)

NAV_PAGES = [
    ("/quem-somos/", "Quem Somos"), ("/o-que-fazemos/", "O que fazemos"),
    ("/destinos/", "Destinos"), ("/blog/", "Blog"), ("/contato/", "Contato"),
    ("/equipe/", "Equipe"), ("/faq/", "Perguntas Frequentes"),
]

TIPOS = ["Aventura", "Bem-estar", "Cultural", "Enoturismo", "Exclusiva",
         "Gastronômica", "Natureza", "Praia", "Romântica",
         "Shows e Espetáculos", "Urbana"]


def header(light=False):
    cls = " light" if light else ""
    return f"""
<header class="site-header{cls}">
  <div class="header-inner">
    <a href="/" aria-label="Cieli Travel"><span class="logo"></span></a>
    <ul class="main-nav">
      <li>
        <a class="nav-link" href="/destinos/">Destinos</a>
        <div class="dropdown">
          <a class="card-mini" href="/italia/" style="background-image:url(/uploads/2026/03/bg-itaila-1.webp)"><span>Itália</span></a>
          <a class="card-mini" href="/franca/" style="background-image:url(/uploads/2026/03/bg-franca-1.webp)"><span>França</span></a>
        </div>
      </li>
      <li>
        <a class="nav-link" href="/destinos/">Experiências</a>
        <div class="dropdown">
          <a class="card-mini" href="/destinos/" style="background-image:url(/uploads/2026/03/bg-casal.webp)"><span>Com quem</span></a>
          <a class="card-mini" href="/destinos/" style="background-image:url(/uploads/2026/03/bg-verao.webp)"><span>Quando</span></a>
          <a class="card-mini" href="/destinos/" style="background-image:url(/uploads/2026/05/enoturismo.webp)"><span>Tipo de viagem</span></a>
        </div>
      </li>
    </ul>
    <a class="btn header-cta" href="/contato/">Planeje sua viagem</a>
    <button class="hamburger" aria-label="Menu"><svg viewBox="0 0 512 512" fill="currentColor" aria-hidden="true"><rect x="0" y="76" width="512" height="40" rx="20"/><rect x="0" y="236" width="512" height="40" rx="20"/><rect x="0" y="396" width="512" height="40" rx="20"/></svg></button>
  </div>
</header>
<div class="overlay-menu" aria-hidden="true">
  <div class="menu-backdrop"></div>
  <aside class="menu-panel">
    <button class="overlay-close close-top" aria-label="Fechar">×</button>
    <div class="menu-drops">
      <details><summary>Destinos <span class="chev">⌄</span></summary>
        <div class="drop-links"><a href="/italia/">Itália</a>
        <a href="/franca/">França</a></div></details>
      <details><summary>Experiências <span class="chev">⌄</span></summary>
        <div class="drop-links"><a href="/destinos/">Todos os destinos</a></div></details>
    </div>
    <div class="menu-logo"><a href="/" aria-label="Cieli"><span class="logo"></span></a></div>
    <nav class="overlay-nav">
      <a href="/quem-somos/">Quem Somos</a>
      <a href="/o-que-fazemos/">O que fazemos</a>
      <a href="/blog/">Blog</a>
      <a href="/contato/">Contato</a>
    </nav>
    <form class="menu-search" data-sitesearch>
      <input type="search" placeholder="Buscar" aria-label="Buscar">
      <button type="submit" aria-label="Buscar">⌕</button>
    </form>
    <button class="overlay-close close-center" aria-label="Fechar">×</button>
    <div class="menu-foot">
      <a href="tel:+558540116310">+55 85 4011-6310</a>
      <div class="menu-stars">
        <svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="12" y="16.5" text-anchor="middle" fill="currentColor" font-size="12" font-family="serif">G</text></svg>
        <span>★★★★★</span>
      </div>
    </div>
  </aside>
</div>"""


def footer():
    tipos = "".join(f'<li><a href="/destinos/">{t}</a></li>' for t in TIPOS)
    menu = "".join(f'<li><a href="{u}">{n}</a></li>' for u, n in NAV_PAGES[:5])
    menu2 = "".join(
        f'<li><a href="{u}">{n}</a></li>'
        for u, n in [("/imprensa/", "Imprensa"), ("/equipe/", "Equipe"),
                     ("/trabalhe-conosco/", "Trabalhe conosco"),
                     ("/faq/", "Perguntas frequentes")])
    return f"""
<footer class="footer">
  <div class="container">
    <div class="newsletter-row">
      <span class="nl-label">Inscreva-se na nossa newsletter</span>
      <form action="#" onsubmit="alert('Newsletter: integração pendente');return false">
        <input type="email" placeholder="E-mail" required>
        <button class="btn btn-solid" type="submit">Assinar</button>
      </form>
    </div>
    <div class="footer-cols">
      <div class="col-menu"><h3>Menu</h3><ul>{menu}{menu2}</ul></div>
      <div><h3>Destinos</h3><ul>
        <li><a href="/franca/">França</a></li>
        <li><a href="/italia/">Itália</a></li></ul></div>
      <div><h3>Com quem</h3><ul>
        <li><a href="/destinos/">Casal</a></li><li><a href="/destinos/">Família</a></li>
        <li><a href="/destinos/">Grupo</a></li><li><a href="/destinos/">Solo</a></li></ul></div>
      <div><h3>Quando</h3><ul>
        <li><a href="/destinos/">Inverno</a></li><li><a href="/destinos/">Outono</a></li>
        <li><a href="/destinos/">Primavera</a></li><li><a href="/destinos/">Verão</a></li></ul></div>
      <div><h3>Tipo de viagem</h3><ul>{tipos}</ul></div>
    </div>
    <div class="footer-bottom">
      <div class="socials"><span class="lbl">Conecte-se:</span>
        <a href="https://www.instagram.com/cielitravel/" rel="noopener">Instagram</a>
        <a href="https://www.linkedin.com/company/cieli-di-toscana" rel="noopener">LinkedIn</a>
        <a href="https://share.google/XwcJriN8q5MNmiYX9" rel="noopener">Google</a>
      </div>
      <div class="legal"><a href="/politica-de-privacidade/">Política de Privacidade</a></div>
    </div>
  </div>
</footer>"""


def shell(title, desc, body, light_header=False, og_image="", lottie=False):
    og = (f'<meta property="og:image" content="{esc(og_image)}">'
          if og_image else "")
    lot = ('<script src="/static/js/vendor/lenis.min.js"></script>'
           + ('<script src="/static/js/vendor/lottie.min.js"></script>'
              if lottie else ""))
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{og}{FONTS}
<link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
{header(light_header)}
<main>{body}</main>
{footer()}
{lot}<script src="/static/js/main.js"></script>
</body>
</html>"""


# --------------------------------------------------------------- destino


def dedupe(seq, key=lambda x: x):
    seen, out = set(), []
    for item in seq:
        k = key(item)
        if k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out


def parse_destino(blocks):
    d = {"days": [], "cities": [], "testi": [], "sections": [], "faq": [],
         "facts": {}, "editorial": None, "quote": None, "hero_img": "",
         "title": "", "subtitle": "", "disclaimer": ""}
    i, n = 0, len(blocks)
    last_img = ""

    def peek(j):
        return blocks[j] if j < n else ("", "")

    while i < n:
        kind, text = blocks[i]
        if kind == "h1" and not d["title"]:
            d["title"] = text
        elif kind == "img":
            if not d["hero_img"]:
                d["hero_img"] = text
            last_img = text
        elif kind == "p" and re.match(
                r"^(Melhor período|Duração ideal|Preço a partir de)\b", text):
            m = re.match(r"^(Melhor período|Duração ideal|Preço a partir de)"
                         r"\s*\n?\s*(.*)$", text, re.S)
            val = m.group(2).strip()
            if not val and peek(i + 1)[0] == "p":
                val = peek(i + 1)[1]
                i += 1
            d["facts"][m.group(1)] = val
        elif kind == "p" and text.startswith("Valor aproximado"):
            d["disclaimer"] = text
        elif kind == "p" and not d["subtitle"] and not d["facts"] \
                and not d["days"] and text.startswith("Viagem"):
            d["subtitle"] = text
        elif kind == "p" and re.match(r"^DIA \d+$", text):
            day = {"n": text, "t": "", "txt": [], "img": last_img}
            j = i + 1
            while j < n and blocks[j][0] in ("h2", "p", "img") \
                    and not re.match(r"^DIA \d+$", blocks[j][1]) \
                    and not (blocks[j][0] == "h2"
                             and re.search(r"TRANSFORME", blocks[j][1])):
                k2, t2 = blocks[j]
                if k2 == "h2" and not day["t"]:
                    day["t"] = t2
                elif k2 == "p":
                    day["txt"].append(t2)
                elif k2 == "img":
                    if not day["txt"] and not day["t"]:
                        day["img"] = t2
                    else:
                        last_img = t2
                        break
                j += 1
            d["days"].append(day)
            i = j - 1
        elif kind == "h2" and text == "DESTINOS":
            # grupos DESTINOS / INFINITOS / Cidade / desc
            if peek(i + 1)[1] == "INFINITOS":
                city = peek(i + 2)[1]
                descr = peek(i + 3)[1] if peek(i + 3)[0] == "p" else ""
                d["cities"].append((city, descr))
                i += 3 if descr else 2
        elif kind == "h2" and text.upper() == "DEPOIMENTOS":
            j = i + 1

            def next_h2(k):
                while peek(k)[0] == "img":
                    k += 1
                return k if peek(k)[0] == "h2" else -1

            while True:
                j2 = next_h2(j)
                if j2 < 0 or not peek(j2)[1].endswith(","):
                    break
                place = peek(j2)[1].rstrip(",")
                parts, k = [], j2 + 1
                for _ in range(3):
                    k2 = next_h2(k)
                    if k2 < 0:
                        break
                    parts.append(peek(k2)[1])
                    k = k2 + 1
                if len(parts) < 3:
                    break
                year, quote, who = parts
                d["testi"].append((place, year, quote,
                                   who.lstrip("- ").strip()))
                j = k
            i = j - 1
        elif kind == "h2" and re.match(r"^[\"“”]", text):
            author = ""
            if peek(i + 1)[0] == "p" and peek(i + 1)[1].startswith("—"):
                author = peek(i + 1)[1]
                i += 1
            d["quote"] = (text.strip('"“” '), author)
        elif kind == "h2" and re.search(r"Inspire-se com este roteiro",
                                        text, re.I):
            d["roteiro_title"] = text
            if peek(i + 1)[0] == "p":
                d["roteiro_sub"] = peek(i + 1)[1]
                i += 1
        elif kind == "h2" and re.search(
                r"TRANSFORME ESSA VIAGEM|^Crie um roteiro|^FICOU ALGUMA",
                text, re.I):
            pass  # renderizado de forma fixa
        elif kind == "h2" and re.search(
                r"INSPIRE-SE PARA A SUA PRÓXIMA", text, re.I):
            # teaser do blog no fim das páginas de país — pular tudo
            j = i + 1
            while j < n and not (blocks[j][0] == "h2" and re.search(
                    r"Perguntas frequentes|^Crie um roteiro", blocks[j][1],
                    re.I)):
                j += 1
            i = j - 1
        elif kind == "h2" and re.search(r"QUE VIAGEM VOCÊ QUER", text, re.I):
            # tabs de categorias — recolher nomes como chips
            stops = (r"POR QUE PLANEJAR|Nossas histórias|SERVIÇOS"
                     r"|\d PASSOS|^DESTINOS$|DEPOIMENTOS|Perguntas frequentes"
                     r"|^Crie um roteiro|INSPIRE-SE")
            cats, j = [], i + 1
            while j < n and not (blocks[j][0] == "h2" and re.search(
                    stops, blocks[j][1], re.I)):
                k2, t2 = blocks[j]
                if k2 in ("h2", "h3") and len(t2) < 30 and not re.search(
                        r"\bA (MARÇO|JUNHO|SETEMBRO|DEZEMBRO)$", t2):
                    cats.append(t2.title())
                j += 1
            d["sections"].append({"title": text, "sub":
                                  "Com quem, quando e que tipo de viagem",
                                  "items": [(c, "", "") for c in dedupe(cats)],
                                  "paras": [], "kind": "chips"})
            i = j - 1
        elif kind == "h2" and re.match(r"^\d PASSOS", text):
            sec = {"title": text, "sub": "", "items": [], "paras": []}
            j = i + 1
            if peek(j)[0] == "p":
                sec["sub"] = peek(j)[1]
                j += 1
            while j < n and re.match(r"^\dº? ?passo", peek(j)[1].lower()):
                step_t = peek(j + 1)[1] if peek(j + 1)[0] == "h2" else ""
                step_x = peek(j + 2)[1] if peek(j + 2)[0] == "p" else ""
                sec["items"].append((f"{peek(j)[1]} — {step_t}", step_x, ""))
                j += 3 if step_x else 2
            sec["items"] = dedupe(sec["items"], key=lambda x: x[0])
            d["sections"].append(sec)
            i = j - 1
        elif kind == "h2" and re.search(r"ospedagens", text):
            sec = {"title": text, "sub": "", "items": [], "paras": []}
            j = i + 1
            if peek(j)[0] == "p":
                sec["sub"] = peek(j)[1]
                j += 1
            while peek(j)[0] in ("h2", "img"):
                if peek(j)[0] == "img":
                    j += 1
                    continue
                if re.search(r"^Crie um roteiro|Perguntas frequentes|^FICOU",
                             peek(j)[1], re.I):
                    break
                name_h = peek(j)[1]
                k = j + 1
                while peek(k)[0] == "img":
                    k += 1
                city = peek(k)[1] if peek(k)[0] == "h2" else ""
                sec["items"].append((name_h, city, ""))
                j = k + 1
            sec["items"] = dedupe(sec["items"], key=lambda x: x[0])
            d["sections"].append(sec)
            i = j - 1
        elif kind == "h2" and re.search(r"Perguntas frequentes", text, re.I):
            sec = {"title": text, "sub": "", "items": [], "paras": []}
            j = i + 1
            if peek(j)[0] == "p" and not peek(j)[1].startswith("-"):
                sec["sub"] = peek(j)[1]
                j += 1
            while peek(j)[0] == "p" and peek(j)[1].lstrip().startswith("-"):
                chunk = peek(j)[1]
                lines = chunk.split("\n", 1)
                q = lines[0].lstrip("- ").strip()
                a = lines[1].strip() if len(lines) > 1 else ""
                sec["items"].append((q, a))
                j += 1
            sec["items"] = dedupe(sec["items"], key=lambda x: x[0])
            d["sections"].append(sec)
            i = j - 1
        elif kind == "h2":
            # seção genérica: título + sub + itens h3/p, ou pares h2+h2
            sec = {"title": text, "sub": "", "items": [], "paras": []}
            j = i + 1
            if peek(j)[0] == "p" and len(peek(j)[1]) < 160 \
                    and peek(j)[1] not in ("PLANEJE SUA VIAGEM",
                                           "FALE COM A CIELI"):
                sec["sub"] = peek(j)[1]
                j += 1
            sec_img = ""
            while j < n:
                k2, t2 = peek(j)
                if k2 == "img":
                    sec_img = t2
                    j += 1
                elif k2 == "h3":
                    descr = peek(j + 1)[1] if peek(j + 1)[0] == "p" else ""
                    sec["items"].append((t2, descr, sec_img))
                    sec_img = ""
                    j += 2 if descr else 1
                elif k2 == "h2" and text == "POR QUE PLANEJAR COM A CIELI?" \
                        and peek(j + 1)[0] == "h2":
                    sec["items"].append((t2, peek(j + 1)[1], ""))
                    j += 2
                elif k2 == "p" and t2 in ("PLANEJE SUA VIAGEM",
                                          "FALE COM A CIELI"):
                    j += 1
                elif k2 == "p" and not sec["items"]:
                    sec["paras"].append(t2)
                    j += 1
                elif k2 == "p":
                    j += 1  # duplicata de carrossel
                else:
                    break
            sec["items"] = dedupe(sec["items"], key=lambda x: x[0] + x[1][:40])
            sec["paras"] = dedupe(sec["paras"])
            if sec["paras"] and not sec["items"] and not d["editorial"]:
                d["editorial"] = (text, sec["paras"])
            else:
                d["sections"].append(sec)
            i = j - 1
        i += 1

    d["cities"] = dedupe(d["cities"], key=lambda x: x[0])
    d["testi"] = dedupe(d["testi"], key=lambda x: x[3] + x[2][:40])
    return d


def anchor_id(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def render_destino(fm, body):
    d = parse_destino(blocks_of(body))
    name = fm.get("title", "").split(" - ")[0]
    out = []

    page_url = fm.get("url", "")
    hero_bg = f"/uploads/{d['hero_img'].split('uploads/')[-1]}" if d["hero_img"] else ""
    hero_vid = bg_video_tag(page_url, "hero", poster=hero_bg)
    out.append(f"""
<section class="hero" style="min-height:80vh">
  <div class="hero-bg" style="background-image:url('{hero_bg}')">{hero_vid}</div>
  <div class="hero-content">
    <h1 class="display" data-typewriter="{esc(d['title'] or name)}">{esc(d['title'] or name)}</h1>
  </div>
</section>""")

    anchors = []
    if d["days"]:
        anchors.append(("roteiro", "Roteiro"))
    if d["cities"]:
        anchors.append(("cidades", "Cidades"))
    if d["testi"]:
        anchors.append(("depoimentos", "Depoimentos"))
    for sec in d["sections"]:
        label = sec["title"]
        short = ("Serviços" if "SERVIÇOS" in label.upper() else
                 "Diferenciais" if "POR QUE" in label.upper() else
                 "Experiências" if "Experiências" in label else
                 "Galeria" if "histórias" in label.lower() else
                 "Hospedagens" if "ospedagens" in label else
                 "FAQ" if "erguntas" in label else None)
        if short:
            anchors.append((anchor_id(short), short))
    if anchors:
        out.append('<nav class="anchor-bar"><ul>' + "".join(
            f'<li><a href="#{a}">{esc(t)}</a></li>' for a, t in anchors)
            + "</ul></nav>")

    if d["facts"]:
        cells = "".join(
            f'<div><h3>{esc(k)}</h3><div class="val">{esc(v)}</div></div>'
            for k, v in d["facts"].items())
        out.append(f"""
<section class="facts">
  <div class="cities">{esc(d['subtitle'])}</div>
  <div class="facts-grid">{cells}</div>
  <div class="disclaimer">{esc(d['disclaimer'])}</div>
</section>""")

    if d["days"]:
        def day_pic(day):
            if day.get("img"):
                return f"/uploads/{day['img'].split('uploads/')[-1]}"
            return hero_bg
        slides = "".join(f"""
    <div class="itin-slide">
      <div class="pic" style="background-image:url('{day_pic(day)}')"></div>
      <div class="txt"><div class="day">{esc(day['n'])}</div>
      <h3>{esc(day['t'])}</h3><p>{esc(' '.join(day['txt']))}</p></div>
    </div>""" for day in d["days"])
        rot_title = d.get("roteiro_title") or "Inspire-se com este roteiro"
        rot_sub = d.get("roteiro_sub") or ("Não existe roteiro pronto na "
                                           "Cieli. Entre em contato para "
                                           "criamos um exclusivamente "
                                           "pensado para você.")
        day_tabs = "".join(
            f'<button data-slide="{k}">{esc(day["n"])}</button>'
            for k, day in enumerate(d["days"]))
        out.append(f"""
<section class="section" id="roteiro">
  <div class="container">
    <div class="section-head">
      <h2 class="h2-sm">{esc(rot_title)}</h2>
      <p class="sub">{esc(rot_sub)}</p>
    </div>
    <div class="itinerary" data-rail>
      <div class="itin-rail rail">{slides}</div>
      <div class="itin-nav">
        <button data-dir="prev" aria-label="Anterior">‹</button>
        <div class="itin-tabs">{day_tabs}</div>
        <button data-dir="next" aria-label="Próximo">›</button>
      </div>
    </div>
    <div style="text-align:center;margin-top:50px">
      <h2 class="h2-sm">Transforme essa viagem na sua</h2>
      <p style="max-width:560px;margin:14px auto 30px">Cada um dos roteiros
      Cieli é feito sob medida para você. Entre em contato para criar algo
      totalmente seu.</p>
      <a class="btn" href="/contato/">Fale com a Cieli</a>
    </div>
  </div>
</section>""")

    if d["editorial"]:
        title, paras = d["editorial"]
        ptags = "".join(f"<p style='margin:18px 0'>{esc(p)}</p>" for p in paras)
        out.append(f"""
<section class="section" style="padding-top:40px">
  <div class="container" style="max-width:820px;text-align:center">
    <h2 class="display" style="font-size:clamp(30px,4vw,46px)">{esc(title)}</h2>
    <div class="ink ink-orange">{INK_SVG}</div>
    {ptags}
    <p style="margin-top:34px"><a class="btn" href="/contato/">Planeje sua viagem</a></p>
  </div>
</section>""")

    if d["quote"]:
        q, author = d["quote"]
        out.append(f"""
<section class="quote">
  <h2 class="display" data-typewriter="“{esc(q)}”">“{esc(q)}”</h2>
  <div class="author">{esc(author)}</div>
</section>""")

    if d["cities"]:
        cards = "".join(f"""
      <div class="city-card"><div class="eyebrow"><span>Destinos</span>
      <span>Infinitos</span></div><h3>{esc(c)}</h3><p>{esc(t)}</p></div>"""
                        for c, t in d["cities"])
        out.append(f"""
<section class="ticker" id="cidades">
  <div class="ticker-track">{cards}{cards}</div>
</section>""")

    if d["testi"]:
        items = "".join(f"""
      <div class="testi"><div class="place">{esc(p)}, {esc(y)}</div>
      <blockquote>“{esc(q)}”</blockquote>
      <div class="who">— {esc(w)}</div>
      <div class="stars">★★★★★</div></div>""" for p, y, q, w in d["testi"])
        depo_vid = bg_video_tag(page_url, "depoimentos")
        depo_style = "" if not depo_vid else ' style="position:relative;overflow:hidden"'
        depo_wrap = (f'{depo_vid}<div style="position:absolute;inset:0;'
                     'background:rgba(5,0,20,.62)"></div>') if depo_vid else ""
        out.append(f"""
<section class="section on-dark" id="depoimentos"{depo_style}>
  {depo_wrap}
  <div class="container testimonials" style="position:relative;z-index:2">
    <h2 style="margin-bottom:40px">Depoimentos</h2>
    <div data-rail><div class="testi-rail rail">{items}</div>
    <div class="rail-nav" style="justify-content:center">
      <button data-dir="prev" style="color:var(--cream)">‹</button>
      <button data-dir="next" style="color:var(--cream)">›</button></div></div>
  </div>
</section>""")

    for sec in d["sections"]:
        label = sec["title"]
        up = label.upper()
        if sec.get("kind") == "chips":
            chips = "".join(f'<div class="chip"><h3>{esc(t)}</h3></div>'
                            for t, _, _ in sec["items"])
            out.append(f"""
<section class="section" id="experiencias"><div class="container">
  <div class="section-head"><h2>{esc(label)}</h2>
  <p class="sub">{esc(sec['sub'])}</p></div>
  <div class="chips">{chips}</div></div></section>""")
            continue
        aid = ("servicos" if "SERVIÇOS" in up else
               "diferenciais" if "POR QUE" in up else
               "experiencias" if "EXPERIÊNCIAS" in up else
               "galeria" if "histórias" in label.lower() else
               "hospedagens" if "ospedagens" in label else
               "faq" if "erguntas" in label else anchor_id(label))
        sub = f'<p class="sub">{esc(sec["sub"])}</p>' if sec["sub"] else ""
        if aid == "faq":
            qa = "".join(f"""
    <details><summary><span class="num">{i + 1:02d}</span>
    <span class="q">{esc(q)}</span></summary>
    <div class="a"><p>{esc(a)}</p></div></details>"""
                         for i, (q, a) in enumerate(sec["items"]))
            out.append(f"""
<section class="section" id="faq"><div class="container">
  <div class="section-head" style="text-align:left;max-width:none;margin-left:0">
  <h2>{esc(label)}</h2>{sub}</div>
  <div class="faq">{qa}</div></div></section>""")
        elif aid == "diferenciais":
            rows = "".join(f"""
      <div class="diff-row"><span class="num">{i + 1:02d}</span>
      <h3>{esc(t)}</h3><p>{esc(x)}</p></div>"""
                           for i, (t, x, _) in enumerate(sec["items"]))
            out.append(f"""
<section class="section" id="diferenciais"><div class="container">
  <h2 class="h2-sm" style="margin-bottom:30px">{esc(label)}</h2>
  <div class="diff-list">{rows}</div>
  <p style="text-align:center;margin-top:54px">
  <a class="btn" href="/contato/">Planeje sua viagem</a></p>
</div></section>""")
        elif aid in ("galeria", "hospedagens", "experiencias"):
            cards = []
            for t, w, img in sec["items"]:
                photo = (f"/uploads/{img.split('uploads/')[-1]}" if img
                         else card_photo(page_url,
                                         "hospedagens" if aid == "hospedagens"
                                         else "experiencias", t))
                where = f'<div class="where">{esc(w)}</div>' if w else ""
                cards.append(f"""
      <div class="photo-card" style="background-image:url('{photo}')">
        <div class="pc-label"><h3>{esc(t)}</h3>{where}</div></div>""")
            out.append(f"""
<section class="section" id="{aid}"><div class="container rail-head">
  <div><h2>{esc(label)}</h2>{sub}</div></div>
  <div data-rail>
    <div class="rail-nav"><button data-dir="prev">‹</button>
    <button data-dir="next">›</button></div>
    <div class="cards-rail rail photo-rail">{''.join(cards)}</div>
  </div>
</section>""")
        else:
            items = "".join(f"""
      <div class="item"><div class="bullet">◆</div>
      <h3>{esc(t)}</h3><p>{esc(x)}</p></div>"""
                            for t, x, _ in sec["items"])
            out.append(f"""
<section class="section" id="{aid}"><div class="container">
  <div class="section-head"><h2>{esc(label)}</h2>{sub}</div>
  <div class="items-grid">{items}</div></div></section>""")

    out.append(cta_section(name, page_url))
    return "".join(out)


def cta_section(name="", page_url=""):
    dest = f" para {name}" if name else " com a Cieli"
    vid = bg_video_tag(page_url, "cta") if page_url else ""
    bg = ("" if vid else
          " style=\"background-image:url('/uploads/2026/03/Costa-Amalfitana.webp')\"")
    return f"""
<section class="cta-hero"{bg}>
  {vid}
  <div class="inner">
    <h2 class="display">Crie um roteiro exclusivo{esc(dest)}</h2>
    <p class="sub">A Cieli quer entender qual é a sua viagem dos sonhos.
    Entre em contato abaixo, sem compromisso.</p>
    <a class="btn" href="/contato/">Fale com a Cieli</a>
  </div>
</section>"""


# --------------------------------------------------------------- home


def render_home(fm, body):
    words = ["PARIS", "FLORENÇA", "VENEZA", "CANNES", "SIENA", "VERSALHES"]
    m = re.search(r"Destinos rotativos:\s*(.+)", body)
    if m:
        words = [w.strip() for w in re.split(r"[·,]", m.group(1)) if w.strip()]

    paixao = ("Nascemos de uma paixão pela Itália, mas como todo "
              "*appassionati*, hoje nós vamos mais longe. Especialistas em "
              "roteiros feitos sob medida para cada viajante, nós traçamos "
              "caminhos que não estão nos guias tradicionais.")
    m = re.search(r"(Nascemos de uma paixão.+?)\n\n", body, re.S)
    if m:
        paixao = re.sub(r"\s+", " ", m.group(1)).strip()

    cards = re.findall(r"^\|\s*([A-ZÀ-Ü'ÂÃÉÊÍÓÔÕÚÇ &.\d]+?)\s*\|\s*(.+?)\s*\|"
                       r"\s*(/[\w\-/]*)\s*\|$", body, re.M)

    def card_bg(title, link):
        og = OG_BY_URL.get(link.rstrip("/") + "/")
        if og and (UPLOADS / og.replace("uploads/", "")).exists():
            return "/" + og
        cand = title.title().replace(" ", "-").replace("'", "")
        for sub in UPLOADS.glob(f"*/*/{cand}*.webp"):
            return f"/uploads/{sub.relative_to(UPLOADS).as_posix()}"
        return "/uploads/2026/03/bg-verao.webp"

    card_html = "".join(f"""
    <a class="card-trip" href="{u}/" style="background-image:url('{card_bg(t, u)}')">
      <h3>{esc(t)}</h3><p>{esc(s)}</p>
      <span class="link-more">Saiba +</span></a>""" for t, s, u in cards)

    jeito = re.findall(r"### (.+?)\n(.+?)(?=\n###|\n##|\Z)", body, re.S)
    jeito = [(t.strip(), re.sub(r"\s+", " ", x).strip())
             for t, x in jeito if t.isupper()][:3]
    jeito_html = "".join(f"""
    <div class="pinned-msg"><h3>{esc(t)}</h3><p>{esc(x)}</p></div>"""
                         for t, x in jeito)
    lottie_path = page_video("/", "lottie")

    finder_selects = "".join(f"""
      <label>{esc(q)}<select><option value="">Selecionar</option>{opts}</select></label>"""
        for q, opts in [
            ("Qual será o seu tipo de viagem?",
             "".join(f"<option>{t}</option>" for t in TIPOS)),
            ("Quando você quer viajar?",
             "".join(f"<option>{t}</option>"
                     for t in ["Inverno", "Outono", "Primavera", "Verão"])),
            ("Com quem você quer viajar?",
             "".join(f"<option>{t}</option>"
                     for t in ["Casal", "Família", "Grupo", "Solo"])),
        ])

    specials = [
        ("special-yellow", "Curadoria",
         "Encontre caminhos e segredos abertos que não estão nos guias tradicionais.",
         "/uploads/2026/02/img-diferencias2.webp"),
        ("special-pink", "Hospitalidade",
         "Sinta-se em casa, falamos a sua língua e damos suporte durante a viagem.",
         "/uploads/2026/02/img-diferencias3.webp"),
        ("special-orange", "Sob medida",
         "Seus desejos viram sua viagem com roteiros feitos exclusivamente para você.",
         "/uploads/2026/02/img-diferenciais01.webp"),
    ]
    specials_html = "".join(f"""
    <div class="special {cls}">
      <div class="txt"><span class="eyebrow">Nossa especialidade</span>
        <div><h3>{esc(t)}</h3>
        <div class="ink ink-navy">{INK_SVG}</div>
        <p>{esc(x)}</p></div><span></span></div>
      <div class="pic" style="background-image:url('{img}')"></div>
    </div>""" for cls, t, x, img in specials)

    # FAQ da home: as 8 primeiras perguntas do content/faq.md
    faq_items = []
    faq_md = CONTENT / "faq.md"
    if faq_md.exists():
        _, fbody = parse_front(faq_md)
        for chunk in re.split(r"\n\s*\n", fbody):
            c = chunk.strip()
            if c.startswith("-") and "?" in c.split("\n")[0]:
                q, _, a = c.partition("\n")
                faq_items.append((q.lstrip("- ").strip(), a.strip()))
    faq_items = faq_items[:8]
    faq_html = "".join(f"""
    <details><summary><span class="num">{i + 1:02d}</span>
    <span class="q">{esc(q)}</span></summary>
    <div class="a"><p>{esc(a)}</p></div></details>"""
                       for i, (q, a) in enumerate(faq_items))

    press = [p for p in ["2026/07/logo-folha-1.webp", "2026/07/viagem_logo.webp",
                         "2026/07/consuelo_logo.webp",
                         "2026/07/roteiros_incr_veis_logo-2.webp",
                         "2026/07/valor_econ_mico_logo.webp"]
             if (UPLOADS / p).exists()]
    if len(press) < 3:  # fallback: qualquer *logo* de 2026/07
        press = sorted(p.relative_to(UPLOADS).as_posix()
                       for p in UPLOADS.glob("2026/07/*logo*.webp"))
    press_html = "".join(f'<img src="/uploads/{p}" alt="" loading="lazy">'
                         for p in press)

    # depoimentos full-bleed empilhados (como no original)
    G_ICON = ('<svg width="22" height="22" viewBox="0 0 24 24" '
              'style="vertical-align:-5px;margin-right:8px">'
              '<circle cx="12" cy="12" r="11" fill="none" '
              'stroke="currentColor" stroke-width="1.2"/>'
              '<text x="12" y="16.5" text-anchor="middle" fill="currentColor" '
              'font-size="12" font-family="serif">G</text></svg>')
    home_testis = [
        ("Roma, Capri e outros", "Experience of a lifetime!", "Rob Walsh",
         "2026/02/matisse-mcmullin-dupe-2-1.webp"),
        ("Florença", "Superou todas as expectativas!",
         "Kamylla e Pedro de Lemos", "2026/02/img-depo1.webp"),
        ("Veneza", "Seguro e enriquecedor", "Roberta Miranda",
         "2026/02/DepoimentosVeneza.webp"),
    ]
    testi_hero_html = "".join(f"""
<section class="testimonial-hero" style="background-image:url('/uploads/{bg}')">
  <div class="inner">
    <div class="testi"><div class="place">{esc(pl)}</div>
    <blockquote>“{esc(q)}”</blockquote>
    <div class="who">— {esc(w)}</div>
    <div class="stars">{G_ICON} ★★★★★</div></div>
  </div>
</section>""" for pl, q, w, bg in home_testis)

    hero_vid = bg_video_tag(
        "/", "hero", poster="/uploads/2026/07/vlcsnap-2026-07-28-14h10m46s125.webp")
    return f"""
<section class="hero">
  <div class="hero-bg" style="background-image:url('/uploads/2026/07/vlcsnap-2026-07-28-14h10m46s125.webp')">{hero_vid}</div>
  <div class="hero-content">
    <div class="hero-rotator">
      <span class="fixed">Conheça o infinito de</span>
      <span class="words words-stack" data-rotator='{esc(str(words).replace("'", '"'))}'></span>
    </div>
  </div>
</section>

<section class="section">
  <div class="container" style="display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center" id="paixao">
    <img src="/uploads/2026/02/img-paixao.webp" alt="Estrada de ciprestes na Toscana" loading="lazy">
    <div style="text-align:center">
      <h2 class="h1" style="font-size:clamp(40px,4.5vw,58px)">Paixão<br>Profunda</h2>
      <div class="ink ink-orange">{INK_SVG}</div>
      <p style="max-width:440px;margin:0 auto">{emify(paixao)}</p>
      <p class="eyebrow" style="margin-top:30px"><a href="/destinos/" style="text-decoration:underline;text-underline-offset:5px">Destinos Infinitos</a></p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:20px">
  <div class="container" style="border-top:1px solid rgba(20,0,89,.35);padding-top:56px">
    <h2>Explore as viagens mais desejadas</h2>
    <p class="eyebrow" style="margin:10px 0 0;max-width:260px">Conheça as regiões que podem estar no seu roteiro</p>
  </div>
  <div data-rail>
    <div class="rail-nav"><button data-dir="prev">‹</button><button data-dir="next">›</button></div>
    <div class="cards-rail rail">{card_html}</div>
  </div>
</section>

<section class="pinned" id="nosso-jeito">
  <div class="pinned-sticky">
    <div class="pinned-media" data-lottie="{lottie_path}"></div>
    <span class="eyebrow pinned-eyebrow">Nosso jeito</span>
    {jeito_html}
  </div>
</section>

<section class="section" id="encontre">
  <div class="container" style="max-width:860px;text-align:center">
    <h2 class="display" style="font-size:clamp(30px,4vw,48px)">Encontre a viagem ideal</h2>
    <div class="ink ink-orange">{INK_SVG}</div>
    <p style="max-width:460px;margin:0 auto 40px">Escolha o tipo de viagem, com quem
    você quer ir e a estação do ano para ver algumas sugestões</p>
    <form class="form-card" action="/destinos/" style="display:grid;gap:18px;text-align:left">
      {finder_selects}
      <div style="text-align:center;margin-top:10px">
        <button class="btn" type="submit">Encontrar</button></div>
    </form>
  </div>
</section>

{testi_hero_html}

<section class="pressbar"><div class="container"><div class="row">{press_html}</div></div></section>

<div class="specials"><div class="specials-sticky">
  <div class="specials-track">{specials_html}</div>
</div></div>

{cta_section("", "/")}

<section class="section"><div class="container">
  <h2 class="h2-sm" style="margin-bottom:30px">Perguntas frequentes</h2>
  <div class="faq">{faq_html}</div>
</div></section>"""


# --------------------------------------------------------------- blog


def clean_post_body(body):
    # remove blocos de "posts relacionados" e CTAs repetidos no fim
    body = re.split(r"\n##?\s*INSPIRE-SE PARA A SUA PRÓXIMA", body)[0]
    lines = []
    for ln in body.splitlines():
        if ln.strip() in ("LER O ARTIGO", "Ir para o conteúdo",
                          "PLANEJE SUA VIAGEM", "FALE COM A CIELI"):
            continue
        lines.append(ln)
    out, prev = [], None
    for ln in lines:
        if ln.strip() and ln.strip() == prev:
            continue
        out.append(ln)
        prev = ln.strip() if ln.strip() else prev
    return "\n".join(out)


def render_post(fm, body):
    body = clean_post_body(body)
    # remove h1 duplicado (título já vai no hero)
    body = re.sub(r"^#\s+.*\n?", "", body.strip(), count=1)
    inner = fix_uploads(md_html(body))
    og = fm.get("og_image", "")
    hero_img = (f'<img src="/{og}" alt="" style="margin:-30px auto 30px;">'
                if og and (UPLOADS / og.replace("uploads/", "")).exists()
                else "")
    return f"""
<section class="article-hero">
  <h1>{esc(fm.get('title', '').split(' - ')[0])}</h1>
  <p class="desc">{esc(fm.get('description', ''))}</p>
</section>
<article class="prose">{hero_img}{inner}</article>
{cta_section()}"""


def render_blog_index(posts):
    cards = []
    for fm in posts:
        og = fm.get("og_image", "")
        thumb = (f"background-image:url('/{og}')"
                 if og and (UPLOADS / og.replace("uploads/", "")).exists()
                 else "")
        title = fm.get("title", "").split(" - ")[0]
        date = ""
        if fm.get("published"):
            y, mo, dd = fm["published"].split("-")
            meses = ["janeiro", "fevereiro", "março", "abril", "maio",
                     "junho", "julho", "agosto", "setembro", "outubro",
                     "novembro", "dezembro"]
            date = (f'<div class="post-date">{int(dd)} de '
                    f'{meses[int(mo) - 1]} de {y}</div>')
        cards.append(f"""
    <a class="post-card" href="/blog/{fm['slug']}/">
      <div class="thumb" style="{thumb}"></div>
      <div class="body"><h3>{esc(title)}</h3>{date}
      <p>{esc(fm.get('description', ''))}</p>
      <span class="link-more">Ler o artigo</span></div></a>""")
    return f"""
<section class="article-hero"><h1>Blog</h1>
<p class="desc">De especialistas para apaixonados por viagens</p></section>
<section class="section"><div class="container">
<div class="post-grid">{''.join(cards)}</div></div></section>"""


# --------------------------------------------------------------- páginas


def render_page(fm, body):
    body = clean_post_body(body)
    body = re.sub(r"^#\s+.*\n?", "", body.strip(), count=1)
    inner = fix_uploads(md_html(body))
    # FAQ heurístico: perguntas em headings ou em lista "- pergunta?\nresposta"
    if body.count("?") > 4 and (re.search(r"^##+ .+\?$", body, re.M)
                                or re.search(r"^- +.+\?\n", body, re.M)):
        inner = accordionize(body)
    title = fm.get("title", "").split(" - ")[0]
    return f"""
<section class="article-hero">
  <h1>{esc(title)}</h1>
  <p class="desc">{esc(fm.get('description', ''))}</p>
</section>
<article class="prose">{inner}</article>
{cta_section()}"""


def accordionize(body):
    blocks = blocks_of(body)
    out, i, n = [], 0, len(blocks)
    num = 0
    while i < n:
        kind, text = blocks[i]
        if kind == "p" and re.match(r"^- +.+\?", text.split("\n")[0]):
            lines = text.split("\n", 1)
            q = lines[0].lstrip("- ").strip()
            a = lines[1].strip() if len(lines) > 1 else ""
            num += 1
            out.append(f"""<details><summary><span class="num">{num:02d}</span>
<span class="q">{esc(q)}</span></summary>
<div class="a"><p>{esc(a)}</p></div></details>""")
            i += 1
        elif kind in ("h2", "h3") and text.endswith("?"):
            answer = []
            j = i + 1
            while j < n and blocks[j][0] == "p":
                answer.append(f"<p>{esc(blocks[j][1])}</p>")
                j += 1
            num += 1
            out.append(f"""<details><summary><span class="num">{num:02d}</span>
<span class="q">{esc(text)}</span></summary>
<div class="a">{''.join(answer)}</div></details>""")
            i = j
        else:
            if kind.startswith("h"):
                out.append(f"<h2>{esc(text)}</h2>")
            elif kind == "img":
                out.append(f'<img src="/{text}" loading="lazy" alt="">')
            else:
                out.append(f"<p>{esc(text)}</p>")
            i += 1
    return f'<div class="faq">{"".join(out)}</div>'


def render_contato(fm, body):
    def sel(label, opts):
        o = "".join(f"<option>{esc(x)}</option>" for x in opts)
        return (f'<div><label>{esc(label)}</label>'
                f'<select><option value="">Selecionar</option>{o}</select></div>')

    form = f"""
<form class="form-card" action="#" onsubmit="alert('Formulário: integração pendente (site estático)');return false">
  <fieldset><legend>Sobre a sua viagem</legend>
    <div class="form-grid">
      {sel("Para onde você gostaria de ir", ["Itália", "França"])}
      {sel("Mês da viagem", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio",
                             "Junho", "Julho", "Agosto", "Setembro", "Outubro",
                             "Novembro", "Dezembro"])}
      {sel("Ano da viagem", ["2026", "2027", "2028", "2029"])}
      {sel("Duração da viagem", ["Até 7 dias", "De 8 a 15 dias", "Mais de 15 dias"])}
      {sel("Quantas pessoas irão", ["1 pessoa", "2 pessoas", "3 pessoas",
                                    "4 pessoas", "5 pessoas", "6 pessoas",
                                    "7 pessoas", "8 pessoas", "9 pessoas",
                                    "10+ pessoas", "15+ pessoas"])}
      {sel("Quanto pretende investir por pessoa?",
           ["€ 3.000 – € 5.000", "€ 5.000 – € 10.000", "€ 10.000 – € 20.000",
            "€ 20.000 – € 30.000", "€ 30.000+"])}
      <div class="full"><label>Espaço para observações</label>
      <textarea rows="4"></textarea></div>
    </div>
  </fieldset>
  <fieldset><legend>Sobre você</legend>
    <div class="form-grid">
      <div><label>Primeiro nome</label><input type="text" required></div>
      <div><label>Sobrenome</label><input type="text" required></div>
      <div><label>E-mail</label><input type="email" required></div>
      <div><label>Telefone</label><input type="tel" required></div>
      {sel("Meio de contato desejado", ["WhatsApp", "SMS", "Ligação", "E-mail"])}
      {sel("Melhor horário para contato",
           ["Entre 9h e 10h", "Entre 10h e 12h", "Entre 13h e 15h",
            "Entre 15h e 18h"])}
    </div>
    <p class="form-note"><label style="display:inline;text-transform:none;letter-spacing:0;font-size:14px">
    <input type="checkbox" style="width:auto" required>
    Li e concordo com a <a href="/politica-de-privacidade/" style="text-decoration:underline">Política de Privacidade</a>.</label></p>
  </fieldset>
  <div style="text-align:center"><button class="btn" type="submit">Enviar</button></div>
</form>"""
    return f"""
<section class="article-hero">
  <h1>Vamos planejar sua viagem?</h1>
  <p class="desc">Você não precisa viajar como todo mundo. É possível criar um
  roteiro só seu! Conte-nos seus planos de viagem, e um consultor Cieli entrará
  em contato.</p>
</section>
<section class="section"><div class="container">{form}</div></section>"""


# --------------------------------------------------------------- main


def write_page(url, html):
    dest = DIST / url.strip("/") / "index.html" if url != "/" \
        else DIST / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def main():
    if DIST.exists():
        for child in DIST.iterdir():  # preserva dist/videos entre builds
            if child.name == "videos":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    DIST.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STATIC, DIST / "static")
    shutil.copytree(UPLOADS, DIST / "uploads")
    if VIDEOS.exists():
        shutil.copytree(VIDEOS, DIST / "videos", dirs_exist_ok=True)

    posts, pages = [], []
    for f in sorted(CONTENT.glob("*.md")):
        fm, body = parse_front(f)
        fm.setdefault("slug", f.stem)
        fm.setdefault("url", f"/{f.stem}/")
        if fm.get("og_image"):
            OG_BY_URL[fm["url"].rstrip("/") + "/"] = fm["og_image"]
        pages.append((fm, body))
    for f in sorted(CONTENT.glob("blog/*.md")):
        fm, body = parse_front(f)
        fm.setdefault("slug", f.stem)
        posts.append((fm, body))

    urls = []
    for fm, body in pages:
        slug = fm["slug"]
        if slug == "blog":
            continue  # índice gerado dos posts
        if slug == "home":
            html = shell(fm.get("title", "Cieli Travel"),
                         fm.get("description", ""), render_home(fm, body),
                         lottie=True)
            write_page("/", html)
            urls.append("/")
            continue
        if slug == "contato":
            body_html = render_contato(fm, body)
        elif slug in DESTINOS:
            body_html = render_destino(fm, body)
        else:
            body_html = render_page(fm, body)
        html = shell(fm.get("title", slug), fm.get("description", ""),
                     body_html, light_header=False,
                     og_image=fm.get("og_image", ""))
        write_page(fm["url"], html)
        urls.append(fm["url"])

    post_fms = [fm for fm, _ in posts]
    write_page("/blog/", shell("Blog - Cieli Travel",
                               "De especialistas para apaixonados por viagens",
                               render_blog_index(post_fms)))
    urls.append("/blog/")
    for fm, body in posts:
        html = shell(fm.get("title", fm["slug"]), fm.get("description", ""),
                     render_post(fm, body), og_image=fm.get("og_image", ""))
        write_page(f"/blog/{fm['slug']}/", html)
        urls.append(f"/blog/{fm['slug']}/")

    # 404 + sitemap + robots
    write_page("/404/", shell("Página não encontrada - Cieli Travel", "", """
<section class="error-page"><h1>404</h1>
<p>A página que você procura não existe.</p>
<a class="btn" href="/">Voltar para a home</a></section>"""))
    (DIST / "404.html").write_text(
        (DIST / "404" / "index.html").read_text(encoding="utf-8"),
        encoding="utf-8")
    shutil.rmtree(DIST / "404")

    base = "https://cielitravel.com"
    sm = "".join(f"<url><loc>{base}{u}</loc></url>" for u in sorted(urls))
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>',
        encoding="utf-8")
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n",
        encoding="utf-8")

    print(f"{len(urls)} paginas geradas em {DIST}")


if __name__ == "__main__":
    main()
