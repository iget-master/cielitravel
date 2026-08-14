# -*- coding: utf-8 -*-
"""Baixa vídeos de fundo, lottie e fontes originais do site em produção.

- Vídeos/lottie → assets/videos/<ano>/<mes>/<arquivo>  (gitignored)
- Fontes → site/static/fonts/ + site/static/css/fonts.css (@font-face locais)
- Mapa página→mídias → site/data/media.json  (usado pelo build.py)

Uso:  py -3 scripts/fetch_media.py
"""
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://cielitravel.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")
VID_DIR = ROOT / "assets" / "videos"
FONT_DIR = ROOT / "site" / "static" / "fonts"
DATA = ROOT / "site" / "data"

PAGES = ["/", "/italia/", "/franca/", "/toscana/", "/sicilia/",
         "/veneza-e-verona/", "/sardenha/", "/puglia/", "/costa-amalfitana/",
         "/paris/", "/cote-dazur/", "/provence/", "/verao-na-italia/",
         "/inverno-na-italia/", "/verao-na-franca/", "/inverno-na-franca/",
         "/andrea-bocelli-na-toscana/", "/quem-somos/", "/o-que-fazemos/",
         "/equipe/", "/imprensa/", "/trabalhe-conosco/", "/faq/", "/contato/",
         "/destinos/", "/blog/"]


def fetch(url, referer=BASE + "/"):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Referer": referer,
        "Accept-Language": "pt-BR,pt;q=0.9"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return "skip"
    dest.write_bytes(fetch(url))
    return "ok"


def main():
    media = {}
    for page in PAGES:
        html = fetch(BASE + page).decode("utf-8", "replace")
        html = html.replace("\\/", "/")
        urls = set(re.findall(
            r"https://cielitravel\.com/wp-content/uploads/"
            r"[^\"'\s\\]+\.(?:mp4|webm|json)", html))
        entry = []
        for u in sorted(urls):
            rel = u.split("/wp-content/uploads/")[-1]
            dest = VID_DIR / rel
            try:
                st = download(u, dest)
                mb = dest.stat().st_size / 1048576
                print(f"{st:4} {page:22} {rel} ({mb:.1f} MB)")
            except Exception as e:
                print(f"FAIL {rel}: {e}")
                continue
            entry.append(rel)
            time.sleep(0.2)
        media[page] = entry

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "media.json").write_text(
        json.dumps(media, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---------- fontes ----------
    css_url = None
    home = fetch(BASE + "/").decode("utf-8", "replace")
    m = re.search(r'href="(https://cielitravel\.com/wp-content/cache/min/'
                  r'[^"]+\.css[^"]*)"', home)
    if m:
        css_url = m.group(1)
    css = fetch(css_url).decode("utf-8", "replace") if css_url else ""
    faces = re.findall(r"@font-face\{[^}]*\}", css)
    keep, n = [], 0
    for face in faces:
        if not re.search(r"Sfizia|trade-gothic|tgn-", face, re.I):
            continue
        urls = re.findall(r"url\((https://[^)\"']+?)\)", face)
        # preferir woff2; baixar e reescrever todas as urls presentes
        newface = face
        for u in urls:
            ext = ".woff2" if "format(\"woff2\")" in face.split(u)[-1][:40] \
                else None
            fam = re.search(r'font-family:\s*"?([^";]+)', face).group(1)
            w = re.search(r"font-weight:\s*([0-9]+)", face)
            s = re.search(r"font-style:\s*(\w+)", face)
            name = re.sub(r"[^a-z0-9-]", "", fam.lower().replace(" ", "-"))
            fname = f"{name}-{w.group(1) if w else '400'}" \
                    f"{'-' + s.group(1) if s and s.group(1) != 'normal' else ''}"
            # só 1 download por face (o woff2 = url com /l ou .woff2)
            if u.endswith(".woff2") or re.search(r"/l\?", u) or "woff2" in u:
                n += 1
                dest = FONT_DIR / f"{fname}.woff2"
                try:
                    download(u, dest)
                    print(f"font {dest.name}")
                except Exception as e:
                    print(f"FAIL font {u[:60]}: {e}")
                    continue
                newface = (f'@font-face{{font-family:"{fam}";'
                           f'font-weight:{w.group(1) if w else 400};'
                           f'font-style:{s.group(1) if s else "normal"};'
                           f'font-display:swap;'
                           f'src:url(/static/fonts/{dest.name}) '
                           f'format("woff2")}}')
                break
        keep.append(newface)

    # Sfizia (self-hosted no site, fora do typekit)
    for u in set(re.findall(r"https://cielitravel\.com/[^\"'\s)]+Sfizia"
                            r"[^\"'\s)]*\.woff2?", home + css)):
        fname = u.split("/")[-1]
        try:
            download(u, FONT_DIR / fname)
            print(f"font {fname}")
        except Exception as e:
            print(f"FAIL {fname}: {e}")

    if (FONT_DIR / "Sfizia-Regular.woff2").exists():
        keep.insert(0, '@font-face{font-family:"Sfizia";font-weight:400;'
                       'font-style:normal;font-display:swap;'
                       'src:url(/static/fonts/Sfizia-Regular.woff2) '
                       'format("woff2")}')

    (ROOT / "site" / "static" / "css" / "fonts.css").write_text(
        "\n".join(dict.fromkeys(keep)), encoding="utf-8")
    print(f"\n{len(keep)} @font-face gravados em site/static/css/fonts.css")


if __name__ == "__main__":
    main()
