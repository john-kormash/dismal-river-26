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

HOLES = range(1, 19)

# The source renders are only 1337x827 and soft, and there are no
# higher-resolution originals to go back to. Two things follow.
#
# Upscaling here rather than in the browser: when you pinch past the
# source resolution, *something* has to invent the pixels. Chrome and
# Safari use a cheap bilinear/bicubic filter and the result is mush.
# Lanczos plus an unsharp pass at the larger size measurably beats it,
# and it costs only file size. 2x also means the card view downsamples
# 2.5x on a phone instead of rendering near-native, which is what made
# the photos look soft on mobile but fine on a desktop.
#
# Quality 78 rather than 86: an upscaled image is smooth, so JPEG has an
# easy job. At 2x the two are indistinguishable at 1:1 and q78 saves
# 1.3 MB across the nine holes.
# The back-nine sources run smaller than the front nine (861 to 1337 px
# wide), so a flat multiplier would leave those holes softer than the
# rest. Normalising to a target width instead keeps every card looking
# the same. MAX_UPSCALE caps it, because past about 2.5x Lanczos has
# nothing left to work with and the extra pixels are pure file size.
TARGET_WIDTH = 2600
MAX_UPSCALE = 2.5
QUALITY = 78

# Scaled with the upscale factor: a fixed radius over-sharpens a 3x
# blow-up and under-sharpens a 1.5x one. Hole 14 carries a hand-drawn
# red arrow, and too much of this rings around its hard edges.
SHARPEN_RADIUS_PER_X = 1.1
SHARPEN_PERCENT = 110
SHARPEN_THRESHOLD = 2


def encode(path: Path):
    """Returns (base64 jpeg, displayed width, displayed height)."""
    img = Image.open(path).convert("RGB")
    factor = min(TARGET_WIDTH / img.width, MAX_UPSCALE)
    if factor > 1.01:
        img = img.resize(
            (round(img.width * factor), round(img.height * factor)),
            Image.LANCZOS,
        )
        if SHARPEN_PERCENT:
            img = img.filter(ImageFilter.UnsharpMask(
                radius=SHARPEN_RADIUS_PER_X * factor,
                percent=SHARPEN_PERCENT,
                threshold=SHARPEN_THRESHOLD,
            ))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode("ascii"), img.width, img.height


def main() -> int:
    if not TEMPLATE.exists():
        print(f"missing template: {TEMPLATE}", file=sys.stderr)
        return 1

    photos = ["var PHOTOS = {"]
    sizes = []
    total = 0
    for n in HOLES:
        src = IMAGES / f"DismalRed_{n}.png"
        if not src.exists():
            print(f"missing image: {src}", file=sys.stderr)
            return 1
        b64, w, h = encode(src)
        total += len(b64)
        print(f"  hole {n:>2}: {src.name:<18} -> {w}x{h}  {len(b64) / 1024:6.0f} KB base64")
        photos.append(f'    {n}: "data:image/jpeg;base64,{b64}",')
        sizes.append(f"{n}: [{w}, {h}]")
    photos.append("  };")

    html = TEMPLATE.read_text(encoding="utf-8")
    for marker in ("/*__PHOTOS__*/", "/*__SIZES__*/"):
        if marker not in html:
            print(f"template has no {marker} marker", file=sys.stderr)
            return 1

    # Sizes go near the top, separately from the megabytes of base64, so
    # the card can set each photo's aspect ratio before it has a src and
    # nothing jumps around as you swipe.
    html = html.replace("/*__SIZES__*/", "var SIZES = { " + ", ".join(sizes) + " };")
    html = html.replace("/*__PHOTOS__*/", "\n".join(photos))
    OUTPUT.write_text(html, encoding="utf-8")

    print(f"\nwrote {OUTPUT.name} — {OUTPUT.stat().st_size / 1024 / 1024:.2f} MB "
          f"({total / 1024 / 1024:.2f} MB of it photos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
