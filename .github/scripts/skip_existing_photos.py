#!/usr/bin/env python3
"""Skip near-identical pictures already included in the site's inline data or local assets."""
import base64
import io
import json
import re
import sys
from pathlib import Path
from PIL import Image, UnidentifiedImageError

manifest_path, html_path, root = map(Path, sys.argv[1:4])
photos = json.loads(manifest_path.read_text(encoding="utf-8"))
html = html_path.read_text(encoding="utf-8")

def fingerprint(data):
    try:
        with Image.open(io.BytesIO(data)) as image:
            image = image.convert("L")
            dx = list(image.resize((9, 8), Image.Resampling.LANCZOS).getdata())
            ax = list(image.resize((8, 8), Image.Resampling.LANCZOS).getdata())
    except (OSError, ValueError, UnidentifiedImageError):
        return None
    d = 0
    for y in range(8):
        for x in range(8):
            d = (d << 1) | (dx[y*9+x] > dx[y*9+x+1])
    avg = sum(ax) / 64
    a = 0
    for px in ax:
        a = (a << 1) | (px > avg)
    return d, a

existing = []
for m in re.finditer(r"data:image/(?:jpeg|jpg|png|webp);base64,([A-Za-z0-9+/=\s]+)", html):
    try:
        blob = base64.b64decode(re.sub(r"\s", "", m.group(1)), validate=True)
    except ValueError:
        continue
    if len(blob) <= 12000000:
        fp = fingerprint(blob)
        if fp: existing.append(fp)
for file in (html_path.parent / "assets" / "photos").glob("**/*"):
    if file.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        fp = fingerprint(file.read_bytes())
        if fp: existing.append(fp)

ids = set(re.findall(r'\b["\']id["\']\s*:\s*["\']([^"\']+)["\']', html))
unique = []
for photo in photos:
    fp = fingerprint((root / photo["image"]).read_bytes())
    if fp is None:
        raise ValueError("Invalid photo: " + photo["image"])
    same = any((fp[0]^p[0]).bit_count() <= 5 and (fp[1]^p[1]).bit_count() <= 8 for p in existing)
    if photo["id"] in ids or same:
        print("Skipping existing photo:", photo["image"])
    else:
        unique.append(photo)
        existing.append(fp)
manifest_path.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")
print("Photos to add:", len(unique), "/", len(photos))
