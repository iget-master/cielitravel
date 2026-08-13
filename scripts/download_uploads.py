# -*- coding: utf-8 -*-
"""Baixa as imagens de wp-content/uploads referenciadas nos .md de content/
para assets/uploads/, preservando a estrutura ano/mes.

Uso:  py -3 scripts/download_uploads.py
"""
import re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DEST = ROOT / "assets" / "uploads"
BASE = "https://cielitravel.com/wp-content/uploads/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")

refs = set()
for md in CONTENT.rglob("*.md"):
    for m in re.findall(r"uploads/([^)\s\"']+\.(?:webp|png|jpe?g|svg|gif))",
                        md.read_text(encoding="utf-8")):
        refs.add(m)

print(f"{len(refs)} imagens referenciadas")
ok = fail = skip = 0
for rel in sorted(refs):
    out = DEST / rel
    if out.exists():
        skip += 1
        continue
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(BASE + rel, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            out.write_bytes(r.read())
        ok += 1
        print(f"OK   {rel}")
    except Exception as e:
        fail += 1
        print(f"FAIL {rel}: {e}")
    time.sleep(0.25)
print(f"\nbaixadas={ok} puladas={skip} falhas={fail}")
