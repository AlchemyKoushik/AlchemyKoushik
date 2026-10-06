#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar and derive profile stats."""
import datetime as dt
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

from profile_config import load_profile, require_username, root_path

OUT_PATH = root_path("data/contributions.json")


def level_for(count):
    if count <= 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def count_from_cell(td, soup):
    for attr in ("data-count", "data-contributions"):
        if td.get(attr) is not None:
            return int(str(td[attr]).replace(",", ""))
    tooltip = soup.find("tool-tip", attrs={"for": td.get("id")})
    text = tooltip.get_text(" ", strip=True) if tooltip else ""
    if re.search(r"no contributions", text, re.IGNORECASE):
        return 0
    match = re.search(r"([\d,]+)\s+contribution", text, re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else 0


def fetch_days(username):
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(url, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td[data-date]")
    if not cells:
        print("No contribution cells found; GitHub markup may have changed.", file=sys.stderr)
        raise SystemExit(1)
    days = []
    for cell in cells:
        date = cell.get("data-date")
        count = count_from_cell(cell, soup)
        days.append({"date": date, "count": count, "level": level_for(count)})
    return sorted(days, key=lambda item: item["date"])


def streak(days, longest=False):
    best = (0, None, None)
    run = 0
    start = None
    sequence = days if longest else list(reversed(days))
    for item in sequence:
        if item["count"]:
            run += 1
            start = item["date"] if run == 1 else start
            if run > best[0]:
                best = (run, start, item["date"])
        elif longest:
            run, start = 0, None
        elif run:
            break
    return (best[0], best[2], best[1]) if not longest and best[0] else best


def build_data(username, days):
    total = sum(item["count"] for item in days)
    active = sum(item["count"] > 0 for item in days)
    best = max(days, key=lambda item: item["count"])
    current = streak(days)
    longest = streak(days, longest=True)
    monthly = {}
    for item in days:
        monthly[item["date"][:7]] = monthly.get(item["date"][:7], 0) + item["count"]
    return {
        "username": username,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active,
        "avg_per_active_day": round(total / active, 1) if active else 0,
        "current_streak": {"length": current[0], "start": current[1], "end": current[2]},
        "longest_streak": {"length": longest[0], "start": longest[1], "end": longest[2]},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": [{"month": key, "total": value} for key, value in sorted(monthly.items())],
        "days": days,
    }


if __name__ == "__main__":
    profile = load_profile()
    username = require_username(profile)
    data = build_data(username, fetch_days(username))
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    print(f"wrote {OUT_PATH}: {data['total_contributions']} contributions")
