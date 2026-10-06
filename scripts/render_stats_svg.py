#!/usr/bin/env python3
"""Render contribution streaks and monthly totals as an animated SVG card."""
import datetime as dt
import html
import json
import sys

from profile_config import load_profile, root_path

SRC = sys.argv[1] if len(sys.argv) > 1 else root_path("data/contributions.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else root_path("stats.svg")
data = json.load(open(SRC, encoding="utf-8"))
profile = load_profile()
user = html.escape(str(profile.get("terminal_user", "user")))
BG, BG2, TILE, FRAME, MUTED, INK, GREEN = "#0d1117", "#111722", "#161b22", "#30363d", "#7d8590", "#e6edf3", "#39d353"
W, H, PAD, TITLE, GAP, TILE_H = 840, 880, 20, 30, 16, 150
TILE_W, TOP = (W - PAD * 2 - GAP) / 2, TITLE + PAD + 4
CHART_TOP = TOP + 3 * TILE_H + 2 * GAP + GAP


def short(value):
    return dt.date.fromisoformat(value).strftime("%b %d").replace(" 0", " ")


def span(item):
    return f"{short(item['start'])} – {short(item['end'])}" if item["length"] else "—"


cur, longest, best = data["current_streak"], data["longest_streak"], data["best_day"]
n_days = len(data["days"])
tiles = [("current streak", cur["length"], " days", span(cur), GREEN), ("longest streak", longest["length"], " days", span(longest), INK), ("contributions", data["total_contributions"], "", "in the last year", INK), ("active days", data["active_days"], f" / {n_days}", f"{data['active_days'] / n_days:.0%} of the year", INK), ("best day", best["count"], "", short(best["date"]), INK), ("avg / active day", data["avg_per_active_day"], "", "contributions", INK)]

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"><style>.t{{opacity:0;animation:in .45s ease-out both}}@keyframes in{{0%{{opacity:0;transform:translateY(14px)}}100%{{opacity:1;transform:translateY(0)}}}}.b{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .6s ease-out both}}@keyframes grow{{to{{transform:scaleY(1)}}}}@media (prefers-reduced-motion:reduce){{.t,.b{{opacity:1!important;transform:none!important;animation:none!important}}}}</style><defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs><rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/><line x1="0" y1="{TITLE}" x2="{W}" y2="{TITLE}" stroke="{FRAME}"/>']
for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    parts.append(f'<circle cx="{PAD+i*16}" cy="{TITLE/2}" r="5" fill="{color}"/>')
parts.append(f'<text x="{W/2}" y="{TITLE/2+4}" fill="{MUTED}" font-size="12" text-anchor="middle">{user}@github: ~$ ./stats.sh</text>')
for i, (label, value, suffix, caption, accent) in enumerate(tiles):
    col, row, x, y = i % 2, i // 2, PAD + (i % 2) * (TILE_W + GAP), TOP + (i // 2) * (TILE_H + GAP)
    shown = f"{value:,.1f}" if isinstance(value, float) else f"{int(value):,}"
    parts.append(f'<g class="t" style="animation-delay:{i*.15:.2f}s"><rect x="{x:.1f}" y="{y}" width="{TILE_W:.1f}" height="{TILE_H}" rx="10" fill="{TILE}" stroke="{FRAME}"/><text x="{x+24:.1f}" y="{y+40}" fill="{MUTED}" font-size="22">$ {html.escape(label)}</text><text x="{x+24:.1f}" y="{y+100}" fill="{accent}" font-size="54" font-weight="700">{shown}<tspan font-size="24" font-weight="400" fill="{MUTED}">{html.escape(suffix)}</tspan></text><text x="{x+24:.1f}" y="{y+132}" fill="{MUTED}" font-size="20">{html.escape(caption)}</text></g>')
monthly = data["monthly"]
chart_h = H - PAD - CHART_TOP
parts.append(f'<g class="t" style="animation-delay:1.5s"><rect x="{PAD}" y="{CHART_TOP}" width="{W-PAD*2}" height="{chart_h}" rx="10" fill="{TILE}" stroke="{FRAME}"/><text x="{PAD+24}" y="{CHART_TOP+40}" fill="{MUTED}" font-size="22">$ contributions / month</text></g>')
plot_top, plot_bot = CHART_TOP + 64, CHART_TOP + chart_h - 40
slot, peak = (W - PAD * 2 - 48) / max(len(monthly), 1), max((m["total"] for m in monthly), default=1)
for i, month in enumerate(monthly):
    bar_w, bx = slot * .62, PAD + 24 + i * slot + (slot * .38) / 2
    height = max(2, (plot_bot - plot_top) * month["total"] / peak)
    parts.append(f'<rect class="b" x="{bx:.1f}" y="{plot_bot-height:.1f}" width="{bar_w:.1f}" height="{height:.1f}" rx="3" fill="{GREEN if month["total"] == peak else "#26a641"}" style="animation-delay:{1.7+i*.06:.2f}s"/><text x="{bx+bar_w/2:.1f}" y="{plot_bot+28}" fill="{MUTED}" font-size="18" text-anchor="middle">{dt.date.fromisoformat(month["month"]+"-01").strftime("%b")[0]}</text>')
parts.append("</svg>")
with open(OUT, "w", encoding="utf-8") as handle:
    handle.write("".join(parts))
print(f"wrote {OUT}: {W} x {H}")
