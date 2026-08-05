#!/usr/bin/env python3
"""
text-to-ppt-card-video split_pages.py
=============================
Splits final.html into per-page standalone HTML files for video recording.

Each page becomes a self-contained HTML with its own single-entry TIMELINE
and AUDIO_SRC, so the playback engine initialises correctly without
cross-page navigation issues.

Usage:
    python split_pages.py <output_dir>

Input (in output_dir):
    final.html  — the built presentation from build.py

Output (in output_dir/pages/):
    page_0.html, page_1.html, ..., page_N.html
"""
import json
import re
import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python split_pages.py <output_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]
    html_path = os.path.join(output_dir, "final.html")
    pages_dir = os.path.join(output_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # -- Extract TIMELINE JSON --
    timeline_match = re.search(
        r'var\s+TIMELINE\s*=\s*(\{.*?\});', html, re.DOTALL
    )
    if not timeline_match:
        print("ERROR: No TIMELINE found in final.html")
        sys.exit(1)

    timeline = json.loads(timeline_match.group(1))
    pages_data = timeline["pages"]
    print(f"Found {len(pages_data)} pages in TIMELINE")

    # -- Extract AUDIO_SRC entries --
    audio_src_match = re.search(
        r'var\s+AUDIO_SRC\s*=\s*\[(.*?)\];', html, re.DOTALL
    )
    if not audio_src_match:
        print("ERROR: No AUDIO_SRC found in final.html")
        sys.exit(1)

    audio_src_text = audio_src_match.group(1)
    audio_entries = re.findall(
        r'("(?:data:audio/mp3;base64,[A-Za-z0-9+/=]+|)")', audio_src_text
    )
    print(f"Found {len(audio_entries)} AUDIO_SRC entries")

    if len(audio_entries) != len(pages_data):
        sys.exit(
            f"ERROR: AUDIO_SRC count ({len(audio_entries)}) "
            f"!= TIMELINE pages count ({len(pages_data)})"
        )

    # -- Find deck boundaries --
    deck_start = html.find('<div class="deck"')
    deck_content_start = html.find('>', deck_start) + 1
    controls_pos = html.find('<div class="controls"', deck_start)
    deck_end = controls_pos
    deck_inner = html[deck_content_start:deck_end]

    # -- Split into page sections --
    page_splits = list(
        re.finditer(r'<div class="page"\s+data-page="(\d+)">', deck_inner)
    )
    print(f"Found {len(page_splits)} page divs in deck")

    if len(page_splits) != len(pages_data):
        sys.exit(
            f"ERROR: page div count ({len(page_splits)}) "
            f"!= TIMELINE pages count ({len(pages_data)})"
        )

    # -- Extract each page's HTML --
    page_htmls = []
    for i, m in enumerate(page_splits):
        start = m.start()
        end = page_splits[i + 1].start() if i + 1 < len(page_splits) else len(deck_inner)
        page_html = deck_inner[start:end].strip()
        page_htmls.append(page_html)

    # -- Generate per-page HTML files --
    for i in range(len(pages_data)):
        if i >= len(page_htmls):
            print(f"  Skipping page {i}: no HTML div found")
            continue
        if i >= len(audio_entries):
            print(f"  Skipping page {i}: no audio entry found")
            continue

        page_html_content = page_htmls[i]

        # Reset data-page to "0" so the engine treats it as the only page
        page_html_content = page_html_content.replace(
            f'data-page="{i}"', 'data-page="0"'
        )

        # Create single-page TIMELINE
        single_timeline = {"pages": [pages_data[i]]}
        single_timeline_json = json.dumps(single_timeline, ensure_ascii=False)

        # Build the new HTML by replacing in the full template
        result = html

        # Replace TIMELINE
        result = re.sub(
            r'var\s+TIMELINE\s*=\s*\{.*?\};',
            f'var TIMELINE = {single_timeline_json};',
            result, count=1, flags=re.DOTALL
        )

        # Replace AUDIO_SRC with single entry
        result = re.sub(
            r'var\s+AUDIO_SRC\s*=\s*\[.*?\];',
            f'var AUDIO_SRC = [{audio_entries[i]}];',
            result, count=1, flags=re.DOTALL
        )

        # Replace deck content with single page
        result = result.replace(deck_inner, '\n  ' + page_html_content + '\n', 1)

        # Disable auto-start: per-page HTML should NOT auto-play.
        # record_video.js controls playback explicitly.
        result = re.sub(
            r'setTimeout\(function\(\)\s*\{\s*start\(\);\s*\},\s*1200\);',
            '/* auto-start disabled for per-page HTML */',
            result,
        )

        # Write per-page file
        out_path = os.path.join(pages_dir, f"page_{i}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result)

        dur = pages_data[i]["duration"]
        size_kb = len(result) // 1024
        print(f"  page_{i}.html  ({size_kb}KB, {dur:.1f}s)")

    print(f"\nDone! {len(pages_data)} pages written to {pages_dir}")


if __name__ == "__main__":
    main()
