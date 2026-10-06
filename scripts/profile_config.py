#!/usr/bin/env python3
"""Shared profile configuration helpers for the generated SVG assets."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(ROOT, "profile.json")


def load_profile():
    with open(CONFIG_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def require_username(profile):
    username = str(profile.get("username", "")).strip()
    if not username or username.upper().startswith("YOUR_"):
        raise SystemExit("Set profile.json username before fetching contributions.")
    return username


def root_path(relative):
    return os.path.join(ROOT, relative)
