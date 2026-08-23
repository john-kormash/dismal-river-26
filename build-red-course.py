#!/usr/bin/env python3
"""Bake the Red Course caddy into one offline HTML file.

Reads red-course.template.html, encodes every tee view in
Course Images/Red/ as a base64 JPEG, and writes red-course.html.

    python build-red-course.py

Requires Pillow.  Edit the notes in the template, not in the
generated file — the generated file gets overwritten.
"""

import base64
import io
import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "Course Images" / "Red"
TEMPLATE = ROOT / "red-course.template.html"
OUTPUT = ROOT / "red-course.html"

HOLES = range(1, 10)
MAX_WIDTH = 1400   # the source renders are ~1337 wide; leave them alone
QUALITY = 86       # measured at 39 dB PSNR — the encode is not the weak link

# The renders are only 1.1 MP and soft to begin with, so double-tapping
# to 2.6x on a 3x phone upscales well past native and turns to mush.
# An unsharp mask before encoding puts the bunker edges and fence lines
# back. Drop PERCENT toward 0 if you ever re-export the source larger —
# sharp input does not want this.
SHARPEN_RADIUS = 1.6
SHARPEN_PERCENT = 95
SHARPEN_THRESHOLD = 2


def encode(path: Path) -> str:
    img = Image.open(path).convert("RGB")
    if img.width > MAX_WIDTH:
        img = img.resize(
            (MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)),
            Image.LANCZOS,
        )
    if SHARPEN_PERCENT:
        img = img.filter(ImageFilter.UnsharpMask(
            radius=SHARPEN_RADIUS,
            percent=SHARPEN_PERCENT,
            threshold=SHARPEN_THRESHOLD,
        ))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main() -> int:
    if not TEMPLATE.exists():
        print(f"missing template: {TEMPLATE}", file=sys.stderr)
        return 1

    lines = ["var PHOTOS = {"]
    total = 0
    for n in HOLES:
        src = IMAGES / f"DismalRed_{n}.png"
        if not src.exists():
            print(f"missing image: {src}", file=sys.stderr)
            return 1
        b64 = encode(src)
        total += len(b64)
        print(f"  hole {n}: {src.name} -> {len(b64) / 1024:6.0f} KB base64")
        lines.append(f'    {n}: "data:image/jpeg;base64,{b64}",')
    lines.append("  };")

    html = TEMPLATE.read_text(encoding="utf-8")
    if "/*__PHOTOS__*/" not in html:
        print("template has no /*__PHOTOS__*/ marker", file=sys.stderr)
        return 1

    html = html.replace("/*__PHOTOS__*/", "\n".join(lines))
    OUTPUT.write_text(html, encoding="utf-8")

    print(f"\nwrote {OUTPUT.name} — {OUTPUT.stat().st_size / 1024 / 1024:.2f} MB "
          f"({total / 1024 / 1024:.2f} MB of it photos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
