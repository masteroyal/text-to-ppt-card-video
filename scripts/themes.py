#!/usr/bin/env python3
"""
themes.py - Resolve lieflat theme CSS from themes.md.

gen_draft.py reads the manifest "theme" field, normalizes it against the
12 documented theme IDs, and injects the matching CSS block from themes.md.
"""

import os
import re

THEME_IDS = [
    "consulting-report",
    "editorial",
    "geek-report",
    "rain-notes",
    "sunrise",
    "terminal",
    "clean-review",
    "dot-matrix",
    "pixel-report",
    "shiny-tiles",
    "story-field",
    "y2k-brand",
]
DEFAULT_THEME = "consulting-report"

_THEMES_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "themes.md")
_CACHE = {}


def themes_md_path():
    """Return themes.md path; tests can override via PPT_CARD_VIDEO_THEMES_MD."""
    return os.environ.get("PPT_CARD_VIDEO_THEMES_MD", _THEMES_MD)


def load_all_theme_css(path=None):
    """Parse themes.md into {theme_id: css_block}."""
    path = path or themes_md_path()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"themes.md not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    themes = {}
    pattern = re.compile(
        r"^## Theme \d+: ([a-z0-9-]+)\b.*?^```css\s*\n(.*?)^```",
        re.MULTILINE | re.DOTALL,
    )
    for match in pattern.finditer(content):
        themes[match.group(1)] = match.group(2).strip()
    return themes


def normalize_theme(theme_id):
    """Return a known theme id, falling back to consulting-report."""
    return theme_id if theme_id in THEME_IDS else DEFAULT_THEME


def get_theme_css(theme_id):
    """Return CSS for a theme id (empty string if themes.md is unavailable)."""
    theme_id = normalize_theme(theme_id)
    if theme_id in _CACHE:
        return _CACHE[theme_id]
    try:
        css = load_all_theme_css().get(theme_id, "")
    except FileNotFoundError:
        css = ""
    _CACHE[theme_id] = css
    return css
