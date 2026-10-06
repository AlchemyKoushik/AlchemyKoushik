#!/usr/bin/env python3
"""Render data/contributions.json as an animated GitHub-style heatmap."""
import datetime as dt
import html
import json

from profile_config import load_profile, root_path

data = json.load(open(root_path("data/contributions.json"), encoding="utf-8"))
profile = load_profile()
user = html.escape(str(profile.get("terminal_user", "user")))
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
cell, gap, pad, left, top, title = 12, 3, 22, 30, 20, 30
days = data["days"]
first = dt.date.fromisoformat(days[0]["date"])
lead, grid, column = (first.weekday() + 1) % 7, [], []
column.extend([None] * lead)
for item in days:
    weekday = (dt.date.fromisoformat(item["date"]).weekday() + 1) % 7
    while len(column) < weekday:
        column.append(None)
    column.append(item)
    if len(column) == 7:
        grid.append(column)
        column = []
if column:
    grid.append(column + [None] * (7 - len(column)))
step, art_w, art_h = cell + gap, len(grid) * (cell + gap), 7 * (cell + gap)
width, height = pad + left + art_w + pad, title + top + art_h + 106 + pad
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"><style>@keyframes cell{{0%{{opacity:0;transform:translateY(-6px)}}100%{{opacity:1;transform:translateY(0)}}}}.c{{opacity:0;animation:cell .42s cubic-bezier(.2,.8,.2,1) both}}@media(prefers-reduced-motion:reduce){{.c{{opacity:1;animation:none}}}}</style><defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1420"/><stop offset="1" stop-color="#0a0e14"/></linearGradient></defs><rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="#1f6feb" stroke-opacity=".55"/><line x1="0" y1="{title}" x2="{width}" y2="{title}" stroke="#1f6feb" stroke-opacity=".35"/>']
for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    parts.append(f'<circle cx="{pad+i*16}" cy="{title/2}" r="5" fill="{color}"/>')
parts.append(f'<text x="{width/2}" y="{title/2+4}" fill="#7d8590" font-size="12" text-anchor="middle">{user}@github: ~/contributions --graph</text>')
grid_top, grid_left = title + top, pad + left
for ci, col in enumerate(grid):
    early = next((item for item in col if item and dt.date.fromisoformat(item["date"]).day <= 7), None)
    if early:
        parts.append(f'<text x="{grid_left+ci*step}" y="{title+14}" fill="#7d8590" font-size="10">{dt.date.fromisoformat(early["date"]).strftime("%b")}</text>')
for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    parts.append(f'<text x="{pad}" y="{grid_top+row*step+cell*.78:.1f}" fill="#7d8590" font-size="9">{name}</text>')
for ci, col in enumerate(grid):
    for ri, item in enumerate(col):
        if not item:
            continue
        count, level = item["count"], min(int(item.get("level", 0)), len(palette)-1)
        delay = ci * .018 + ri * .045
        parts.append(f'<rect class="c" x="{grid_left+ci*step}" y="{grid_top+ri*step}" width="{cell}" height="{cell}" rx="2.5" fill="{palette[level]}" style="animation-delay:{delay:.3f}s"><title>{item["date"]}: {count} contribution{"s" if count != 1 else ""}</title></rect>')
leg_y = grid_top + art_h + 6
parts.append(f'<text x="{width-pad-145}" y="{leg_y+10}" fill="#7d8590" font-size="10">Less</text>')
for i, color in enumerate(palette):
    parts.append(f'<rect x="{width-pad-105+i*12}" y="{leg_y}" width="11" height="11" rx="2" fill="{color}"/>')
parts.append(f'<text x="{width-pad-25}" y="{leg_y+10}" fill="#7d8590" font-size="10">More</text><line x1="0" y1="{leg_y+26}" x2="{width}" y2="{leg_y+26}" stroke="#1f6feb" stroke-opacity=".25"/>')
ly = leg_y + 50
parts.append(f'<text x="{pad}" y="{ly}" fill="#39d353" font-size="13"><tspan font-weight="700">{data["total_contributions"]:,}</tspan><tspan fill="#7d8590"> contributions in the last year</tspan></text><text x="{width-pad}" y="{ly}" fill="#7d8590" font-size="12" text-anchor="end">{data["range"]["start"]} → {data["range"]["end"]}</text>')
ly += 24
parts.append(f'<text x="{pad}" y="{ly}" fill="#7d8590" font-size="13">current streak <tspan fill="#22d3ee" font-weight="700">{data["current_streak"]["length"]} days</tspan><tspan fill="#7d8590"> · longest </tspan><tspan fill="#22d3ee" font-weight="700">{data["longest_streak"]["length"]} days</tspan></text><text x="{width-pad}" y="{ly}" fill="#7d8590" font-size="12" text-anchor="end">best day <tspan fill="#f2cc60" font-weight="700">{data["best_day"]["count"]}</tspan> on {data["best_day"]["date"]}</text></svg>')
with open(root_path("contrib-heatmap.svg"), "w", encoding="utf-8") as handle:
    handle.write("".join(parts))
print(f"wrote {root_path('contrib-heatmap.svg')}")
