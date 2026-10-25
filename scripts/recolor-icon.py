#!/usr/bin/env python3
"""Recolor a PNG icon to a new colour while keeping its shading and transparency.

Usage:
    python3 scripts/recolor-icon.py icon.png --color "#39FF14" --out icon-green.png --size 256

Requires: pip install pillow numpy matplotlib
"""
import argparse, colorsys
import numpy as np
from PIL import Image
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb


def recolor(path, hex_color, out, size=None):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    target_h, target_s, _ = colorsys.rgb_to_hsv(r, g, b)

    img = np.array(Image.open(path).convert("RGBA")).astype(float) / 255
    rgb, alpha = img[..., :3], img[..., 3:]

    hsv = rgb_to_hsv(rgb)
    hsv[..., 0] = target_h                 # swap the hue
    hsv[..., 1] = hsv[..., 1] * target_s   # scale saturation so pure colour -> target
    # value (brightness) is untouched, so shadows and gradients are preserved

    result = np.concatenate([hsv_to_rgb(hsv), alpha], axis=-1)
    result = Image.fromarray((result * 255).round().astype("uint8"), "RGBA")
    if size:
        result = result.resize((size, size), Image.LANCZOS)
    result.save(out)
    print(f"Saved {out} ({result.size[0]}x{result.size[1]})")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="source PNG")
    p.add_argument("--color", default="#39FF14", help="target colour, e.g. #39FF14")
    p.add_argument("--out", default="icon-recolored.png", help="output file")
    p.add_argument("--size", type=int, help="optional square size, e.g. 256")
    a = p.parse_args()
    recolor(a.input, a.color, a.out, a.size)
