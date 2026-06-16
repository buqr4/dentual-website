# -*- coding: utf-8 -*-
"""One-off: create .webp siblings for all photographic assets (originals kept).
Run: python tools/convert_webp.py"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (folder, exts, max_width, quality)
JOBS = [
    ("assets/hero",        (".jpg", ".jpeg"), 1920, 80),
    ("assets/treatments",  (".jpg", ".jpeg"), 1000, 80),
    ("assets/doctors",     (".png",),          640, 82),
]
tot_old = tot_new = 0
for folder, exts, maxw, q in JOBS:
    d = os.path.join(ROOT, folder)
    if not os.path.isdir(d):
        continue
    for name in sorted(os.listdir(d)):
        base, ext = os.path.splitext(name)
        if ext.lower() not in exts:
            continue
        src = os.path.join(d, name)
        dst = os.path.join(d, base + ".webp")
        im = Image.open(src)
        if im.width > maxw:
            h = round(im.height * maxw / im.width)
            im = im.resize((maxw, h), Image.LANCZOS)
        if im.mode in ("P", "LA"):
            im = im.convert("RGBA")
        elif im.mode == "CMYK":
            im = im.convert("RGB")
        im.save(dst, "WEBP", quality=q, method=6)
        o = os.path.getsize(src); n = os.path.getsize(dst)
        tot_old += o; tot_new += n
        print("  %-38s %5d KB -> %4d KB  (-%d%%)" % (folder + "/" + base + ".webp", o // 1024, n // 1024, round((1 - n / o) * 100)))
print("TOTAL: %d KB -> %d KB  (saved %d KB, -%d%%)" % (tot_old // 1024, tot_new // 1024, (tot_old - tot_new) // 1024, round((1 - tot_new / tot_old) * 100)))
