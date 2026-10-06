#!/usr/bin/env python3
"""Convert a prepared grayscale portrait into an animated monochrome SVG."""
import html
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter

from profile_config import load_profile, root_path

SRC = sys.argv[1] if len(sys.argv) > 1 else root_path("source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else root_path("profile-ascii.svg")
COLS, ART_W, PAD, TITLE, STATUS = 180, 800, 20, 30, 30
CELL_W, CELL_H = ART_W / COLS, (ART_W / COLS) * 15 / 8
ROWS = round(COLS * 8 / 15)
RAMP = " .`:-=+*cs#%@"
BG, BG2, FRAME, MUTED, INK = "#0d1117", "#111722", "#30363d", "#7d8590", "#c9d1d9"

if not os.path.exists(SRC):
    raise SystemExit(f"Missing {SRC}. Add your photo and run prep_photo.py first.")

profile = load_profile()
terminal_user = str(profile.get("terminal_user", "user"))
display_name = str(profile.get("display_name", "Your Name"))
im = Image.open(SRC).convert("L")
im = ImageEnhance.Contrast(im).enhance(1.05).resize((COLS, ROWS), Image.LANCZOS)
if os.environ.get("SHARPEN"):
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))

rows = []
for y in range(ROWS):
    line = []
    for x in range(COLS):
        lum = pow(im.getpixel((x, y)) / 255.0, 1.18)
        line.append(" " if lum >= 0.80 else RAMP[max(0, min(len(RAMP) - 1, int((1 - lum) * (len(RAMP) - 1) + 0.5)))])
    rows.append("".join(line))

width, height = ART_W + PAD * 2, TITLE + ROWS * CELL_H + STATUS + PAD
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"><defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs><rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{FRAME}"/><line x1="0" y1="{TITLE}" x2="{width}" y2="{TITLE}" stroke="{FRAME}"/>']
for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    parts.append(f'<circle cx="{PAD+i*16}" cy="{TITLE/2}" r="5" fill="{color}"/>')
parts.append(f'<text x="{width/2}" y="{TITLE/2+4}" fill="{MUTED}" font-size="12" text-anchor="middle">{html.escape(terminal_user)}@github: ~$ ./portrait.sh</text>')
row_dur, art_top = 5.8 / ROWS, TITLE + PAD * 0.35
for row, line in enumerate(rows):
    y, row_y, delay = art_top + row * CELL_H + CELL_H * .74, art_top + row * CELL_H, row * row_dur
    text = f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" font-size="{CELL_H*.86:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{html.escape(line)}</text>'
    parts.append(f'<clipPath id="r{row}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0"><animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" dur="{row_dur:.2f}s" fill="freeze"/></rect></clipPath><g clip-path="url(#r{row})">{text}</g>')
status_line, status_y = TITLE + ROWS * CELL_H + PAD * .35, TITLE + ROWS * CELL_H + PAD * .35 + 19
label = f"{terminal_user}@github:~$ whoami {display_name} "
parts.extend([f'<line x1="0" y1="{status_line:.1f}" x2="{width}" y2="{status_line:.1f}" stroke="{FRAME}"/>', f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" font-size="13">{html.escape(terminal_user)}@github:~$ whoami <tspan fill="{INK}">{html.escape(display_name)}</tspan></text>', f'<rect x="{PAD+len(label)*13*.6:.1f}" y="{status_y-12}" width="8" height="14" fill="{INK}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>', "</svg>"])
with open(OUT, "w", encoding="utf-8") as handle:
    handle.write("".join(parts))
print(f"wrote {OUT}: {width} x {height}")
