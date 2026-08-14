# -*- coding: utf-8 -*-
"""Extrai o mapeamento título→foto dos cards (hospedagens, experiências)
das páginas de destino em produção → site/data/cards.json

Uso:  py -3 scripts/fetch_cards.py
"""
import html as html_mod
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://cielitravel.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")

PAGES = ["/toscana/", "/sicilia/", "/veneza-e-verona/", "/sardenha/",
         "/puglia/", "/costa-amalfitana/", "/paris/", "/cote-dazur/",
         "/provence/", "/verao-na-italia/", "/inverno-na-italia/",
         "/verao-na-franca/", "/inverno-na-franca/",
         "/andrea-bocelli-na-toscana/", "/italia/", "/franca/"]


def fetch(p):
    req = urllib.request.Request(BASE + p, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def pairs_from(seg):
    """Pareia cada data-bg/img com o título de card seguinte no HTML."""
    toks = re.findall(
        r'data-(?:dce-background-image-url|bg|src)='
        r'"([^"]*?uploads/[^"]+?\.(?:webp|jpe?g|png))"'
        r'|<(?:h\d|p|span|div)[^>]*>\s*([^<>{}]{3,60}?)\s*</',
        seg)
    toks = [(bg, "", txt) for bg, txt in toks]
    out, cur_bg = {}, None
    for bg1, bg2, txt in toks:
        bg = bg1 or bg2
        if bg:
            cur_bg = bg.split("uploads/")[-1]
            continue
        t = html_mod.unescape(txt).strip()
        if cur_bg and t and not t.startswith(("http", "%", "@")) \
                and not re.match(r"^[\d\s.,€R$]+$", t):
            out.setdefault(t.upper(), cur_bg)
            cur_bg = None
    return out


def main():
    data = {}
    for p in PAGES:
        h = fetch(p).replace("\\/", "/")
        entry = {}
        # hospedagens
        m = re.search(r"selo Cieli(.*?)(Perguntas frequentes|Crie um roteiro)",
                      h, re.S | re.I)
        if m:
            entry["hospedagens"] = pairs_from(m.group(1))
        # experiências de luxo
        m = re.search(r"(Experiências de luxo|EXPERIÊNCIAS DE LUXO)(.*?)"
                      r"(hist[óo]rias favoritas|Hospedagens|Crie um roteiro)",
                      h, re.S)
        if m:
            entry["experiencias"] = pairs_from(m.group(2))
        data[p] = entry
        ne = len(entry.get("experiencias", {}))
        nh = len(entry.get("hospedagens", {}))
        print(f"{p:28} hospedagens={nh} experiencias={ne}")
        time.sleep(0.25)

    out = ROOT / "site" / "data" / "cards.json"
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    print(f"\ngravado {out}")


if __name__ == "__main__":
    main()
