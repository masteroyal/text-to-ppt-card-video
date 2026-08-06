#!/usr/bin/env python3
"""
gen_draft.py - Generate draft.html with __AUDIO_N__ and __TIMELINE__ placeholders.

Usage:
    python gen_draft.py <output_dir>

Reads manifest.json from output_dir, generates draft.html with dynamic
card dimensions based on aspect_ratio field.
"""
import html
import hashlib
import json
import os
import re
import sys

from themes import get_theme_css, normalize_theme

# -- Aspect ratio -> card dimensions --
RATIO_DIMS = {
    "3:4":  (600, 800),
    "4:3":  (800, 600),
    "1:1":  (700, 700),
    "9:16": (540, 960),
    "16:9": (960, 540),
}


def esc(text):
    """Escape manifest text for safe HTML output."""
    return html.escape(str(text), quote=True)


def safe_id(text):
    """Return a DOM-safe id, hashing empty or non-ASCII input deterministically."""
    raw = str(text)
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", raw)
    if cleaned:
        return cleaned
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"el-{digest}"


COMPONENT_TYPES = {"exec", "paragraph", "blockquote", "metrics", "table", "list", "grid"}
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
COVER_IDS = ("cover-title", "cover-subtitle", "cover-label", "cover-tags", "cover-footer")


def _register_id(id_value, path, seen):
    """Validate one manifest id and add it to the global seen set."""
    if not isinstance(id_value, str) or not id_value:
        raise ValueError(f"{path} must be a non-empty string")
    if not ID_PATTERN.match(id_value):
        raise ValueError(f"{path} must use only ASCII letters, digits, '-' and '_'")
    if id_value in seen:
        raise ValueError(
            f"{path} repeats id {id_value!r}; ids must be unique across the whole manifest"
        )
    seen.add(id_value)


def _validate_narration_refs(narration, page_ids, path):
    """Check that every narration element id exists on its page."""
    for ni, seg in enumerate(narration):
        for ei, eid in enumerate(seg.get("elements", [])):
            ref_path = f"{path}.narration[{ni}].elements[{ei}]"
            if not isinstance(eid, str) or not eid:
                raise ValueError(f"{ref_path} must be a non-empty string")
            if eid not in page_ids:
                raise ValueError(f"{ref_path} references unknown id {eid!r}")


def validate_manifest(manifest):
    """Validate manifest.json structure and report the field path on errors."""
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")
    pages = manifest.get("pages")
    if not isinstance(pages, list):
        raise ValueError("manifest pages must be a list")

    seen_ids = set()
    for pi, page in enumerate(pages):
        path = f"pages[{pi}]"
        if not isinstance(page, dict):
            raise ValueError(f"{path} must be an object")
        if page.get("type") not in ("cover", "content"):
            raise ValueError(f"{path}.type must be 'cover' or 'content'")
        if not isinstance(page.get("title"), str) or not page["title"]:
            raise ValueError(f"{path}.title is required")

        narration = page.get("narration", [])
        if not isinstance(narration, list):
            raise ValueError(f"{path}.narration must be a list")
        for ni, seg in enumerate(narration):
            seg_path = f"{path}.narration[{ni}]"
            if not isinstance(seg, dict):
                raise ValueError(f"{seg_path} must be an object")
            if not isinstance(seg.get("text"), str) or not seg["text"]:
                raise ValueError(f"{seg_path}.text is required")
            if "elements" in seg and not isinstance(seg["elements"], list):
                raise ValueError(f"{seg_path}.elements must be a list")

        if page["type"] == "cover":
            for cid in COVER_IDS:
                _register_id(cid, f"{path}.{cid}", seen_ids)
            for field in ("subtitle", "tags", "firm", "label"):
                if not isinstance(page.get(field, ""), str):
                    raise ValueError(f"{path}.{field} must be a string")
            if not isinstance(page.get("meta", []), list):
                raise ValueError(f"{path}.meta must be a list")
            _validate_narration_refs(narration, set(COVER_IDS), path)
            continue

        for field in ("subtitle", "series", "page_num", "category", "breadcrumb"):
            if not isinstance(page.get(field, ""), str):
                raise ValueError(f"{path}.{field} must be a string")
        sections = page.get("sections", [])
        if not isinstance(sections, list):
            raise ValueError(f"{path}.sections must be a list")
        page_ids = set()
        for si, sec in enumerate(sections):
            sec_path = f"{path}.sections[{si}]"
            if not isinstance(sec, dict):
                raise ValueError(f"{sec_path} must be an object")
            if not isinstance(sec.get("heading"), str) or not sec["heading"]:
                raise ValueError(f"{sec_path}.heading is required")
            if "heading_id" in sec:
                _register_id(sec["heading_id"], f"{sec_path}.heading_id", seen_ids)
                page_ids.add(sec["heading_id"])
            components = sec.get("components", [])
            if not isinstance(components, list):
                raise ValueError(f"{sec_path}.components must be a list")
            for ci, comp in enumerate(components):
                comp_path = f"{sec_path}.components[{ci}]"
                if not isinstance(comp, dict):
                    raise ValueError(f"{comp_path} must be an object")
                comp_type = comp.get("type")
                if comp_type not in COMPONENT_TYPES:
                    raise ValueError(
                        f"{comp_path}.type must be one of {sorted(COMPONENT_TYPES)}"
                    )
                if "id" in comp:
                    _register_id(comp["id"], f"{comp_path}.id", seen_ids)
                    page_ids.add(comp["id"])
                if comp_type in ("exec", "paragraph", "blockquote"):
                    if not isinstance(comp.get("text"), str) or not comp["text"]:
                        raise ValueError(f"{comp_path}.text is required")
                elif comp_type in ("metrics", "list", "grid"):
                    if not isinstance(comp.get("items"), list):
                        raise ValueError(f"{comp_path}.items must be a list")
                elif comp_type == "table":
                    if not isinstance(comp.get("rows"), list):
                        raise ValueError(f"{comp_path}.rows must be a list")
        _validate_narration_refs(narration, page_ids, path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python gen_draft.py <output_dir>")
        print("  output_dir must contain manifest.json")
        sys.exit(1)

    out = sys.argv[1]
    manifest_path = os.path.join(out, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"ERROR: {manifest_path} not found")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    try:
        validate_manifest(manifest)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    pages = manifest["pages"]
    brand = manifest.get("brand", {"name": "Text-to-PPT-Card-Video", "sub": ""})
    num_pages = len(pages)
    aspect_ratio = manifest.get("aspect_ratio", "3:4")
    title = manifest.get("title", "Untitled")
    theme = normalize_theme(manifest.get("theme", "consulting-report"))
    theme_css = get_theme_css(theme)
    card_w, card_h = RATIO_DIMS.get(aspect_ratio, (600, 800))

    # -- Cover card height: portrait = same as content (uniform for video crop); landscape = slightly taller --
    if card_h > card_w:
        cover_h = card_h  # portrait: unify with content card height for single crop rect
    elif card_w > card_h:
        cover_h = min(int(card_w * (3 / 4)), int(card_h * 1.3))
    else:
        cover_h = int(card_h * 1.15)

    content_h = card_h
    cover_section_h = 210

    # -- Dynamic cover page positions --
    top_offset = max(28, int(cover_h * 0.055))
    hero_top = int(cover_h * 0.35)
    footer_bottom = max(28, int(cover_h * 0.055))
    title_max_w = int(card_w * 0.75)

    # ===========================================================
    # Build HTML
    # ===========================================================

    html_parts = []

    # -- HEAD --
    html_parts.append(f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>
/* === BASE STYLES === */
:root{{--navy:#1b2a4a;--dark:#151f35;--cyan:#00a9f4;--light-cyan:#4fc3f7;--text:#1a1a1a;--gray600:#555;--gray400:#999;--gray200:#e0e0e0;--gray100:#f5f5f5;--white:#fff;--green:#4caf50;--amber:#ffc107;--red:#e53935;--serif:"Noto Serif SC","Source Han Serif SC","Songti SC",Georgia,serif;--sans:"PingFang SC","Noto Sans SC","Microsoft YaHei",Arial,sans-serif}}
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{min-height:100%}}
body{{font-family:var(--sans);color:var(--text);-webkit-font-smoothing:antialiased;background:#0a0f1a;overflow:hidden}}

/* === DECK LAYOUT === */
.deck{{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;height:100vh;width:100vw}}
.deck::-webkit-scrollbar{{display:none}}
.deck{{-ms-overflow-style:none;scrollbar-width:none}}
.page{{flex:0 0 100vw;height:100vh;display:flex;align-items:center;justify-content:center;scroll-snap-align:center;padding:32px}}

/* === CARD SHELL === */
.card{{position:relative;overflow:hidden;border-radius:6px}}
.card--cover{{width:{card_w}px;height:{cover_h}px;max-width:calc(100vw - 48px);max-height:calc(100vh - 120px);background:var(--navy);color:#fff;box-shadow:0 24px 48px rgba(15,25,45,.28)}}
.card--cover::after{{content:"";position:absolute;inset:0;pointer-events:none;border:1px solid rgba(255,255,255,.08)}}
.card--content{{width:{card_w}px;height:{content_h}px;max-width:calc(100vw - 48px);max-height:calc(100vh - 100px);background:#fff;box-shadow:0 25px 50px rgba(0,0,0,.42),0 10px 30px rgba(0,10,20,.3)}}
.article{{height:100%;overflow:hidden;background:#fff}}
.article::-webkit-scrollbar{{width:6px}}
.article::-webkit-scrollbar-track{{background:#eef1f5}}
.article::-webkit-scrollbar-thumb{{background:#9fb4c8;border-radius:6px}}

/* === COVER PAGE === */
.top{{position:absolute;z-index:2;top:{top_offset}px;left:46px;right:46px;display:flex;justify-content:space-between;gap:22px;color:rgba(255,255,255,.62);font-size:12px;line-height:1.7;letter-spacing:.08em}}
.logo{{font-family:var(--serif);font-size:23px;font-weight:600;line-height:1.35;letter-spacing:.04em}}
.logo span{{display:block;padding-left:1em;color:rgba(255,255,255,.78);font-weight:400}}
.meta{{max-width:190px;text-align:right}}
.hero{{position:absolute;z-index:2;left:46px;right:46px;top:{hero_top}px}}
.label{{margin-bottom:18px;color:rgba(255,255,255,.62);font-size:12px;letter-spacing:.12em}}
.title{{max-width:{title_max_w}px;font-family:var(--serif);font-size:52px;font-weight:700;line-height:1.14;letter-spacing:0}}
.sub{{max-width:{int(title_max_w * 0.88)}px;margin-top:20px;color:rgba(255,255,255,.82);font-family:var(--serif);font-size:22px;line-height:1.48}}
.footer{{position:absolute;z-index:2;left:46px;right:46px;bottom:{footer_bottom}px;display:flex;align-items:baseline;justify-content:space-between;gap:18px;border-top:1px solid rgba(255,255,255,.28);padding-top:14px;color:rgba(255,255,255,.48);font-size:11px;line-height:1.5;letter-spacing:.08em}}
.firm{{font-family:var(--serif);color:rgba(255,255,255,.68);letter-spacing:.12em}}

/* === CONTENT CARD COVER SECTION === */
.cover{{min-height:{cover_section_h}px;background:var(--navy);background-image:repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,.035) 39px,rgba(255,255,255,.035) 40px),repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,.035) 39px,rgba(255,255,255,.035) 40px);color:#fff;padding:34px 38px;display:flex;flex-direction:column;justify-content:space-between}}
.cover .logo{{font-size:20px}}
.cover h1{{font-family:var(--serif);font-size:34px;line-height:1.18;margin-bottom:12px}}
.cover .sub{{font-size:17px}}
.cover .date{{font-size:12px;color:rgba(255,255,255,.58);letter-spacing:.08em}}

/* === BODY AREA === */
.body{{padding:20px 34px 24px}}
.breadcrumb{{text-align:right;font-size:11px;color:var(--gray400);letter-spacing:.08em;margin-bottom:14px}}

/* === COMPONENTS === */
h2{{font-family:var(--serif);font-size:23px;line-height:1.35;margin:18px 0 8px;color:#000}}
.rule{{height:1px;background:#000;margin-bottom:10px}}
.exec{{background:var(--gray100);border-left:4px solid var(--cyan);padding:12px 16px;margin:12px 0;border-radius:0 4px 4px 0}}
.exec p{{margin:0;font-size:17px;line-height:1.6;color:#333}}
p{{font-size:17px;line-height:1.65;color:#333;margin-bottom:12px;font-weight:300}}
strong{{color:#000;font-weight:700}}
.metrics{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--gray200);margin:12px 0 16px;border-radius:4px;overflow:hidden}}
.metric{{background:#fff;padding:12px}}
.metric b{{display:block;font-family:var(--serif);font-size:36px;line-height:1;color:var(--cyan);margin-bottom:6px}}
.metric span{{display:block;font-size:14px;font-weight:700;color:#000}}
.metric small{{display:block;font-size:12px;line-height:1.45;color:var(--gray600);margin-top:4px}}
.table{{border-top:1px solid #000;border-bottom:1px solid #000;margin:12px 0 16px}}
.row{{display:grid;grid-template-columns:92px 1fr 58px;gap:10px;padding:8px 0;border-bottom:1px solid var(--gray200);align-items:start}}
.row:last-child{{border-bottom:0}}
.row b{{font-size:12px;color:var(--gray400);letter-spacing:.08em}}
.row span{{font-size:16px;line-height:1.45;color:#111}}
.status{{font-size:12px;font-weight:700;color:var(--green)}}
.status-red{{font-size:12px;font-weight:700;color:var(--red)}}
ul{{margin:4px 0 14px 18px}}
li{{font-size:16px;line-height:1.55;color:#333;margin-bottom:8px;font-weight:300}}
.source{{margin-top:16px;padding-top:8px;border-top:1px solid var(--gray200);display:flex;justify-content:space-between;font-size:10px;color:var(--gray400);letter-spacing:.08em}}

/* === ANIMATION (timeline-driven) === */
.cover > *,.body > .breadcrumb,.body > h2,.body > .rule,.body > .exec,.body > p,.body > ul,.body > .table,.body > blockquote,.body > .source,.body > .metrics,.body > .grid,#cover-label,#cover-title,#cover-subtitle,#cover-tags,#cover-footer{{opacity:0;transform:translateY(20px);transition:opacity .75s cubic-bezier(.22,1,.36,1),transform .75s cubic-bezier(.22,1,.36,1)}}
.cover > *.visible,.body > .breadcrumb.visible,.body > h2.visible,.body > .rule.visible,.body > .exec.visible,.body > p.visible,.body > ul.visible,.body > .table.visible,.body > blockquote.visible,.body > .source.visible,.body > .metrics.visible,.body > .grid.visible,#cover-label.visible,#cover-title.visible,#cover-subtitle.visible,#cover-tags.visible,#cover-footer.visible{{opacity:1!important;transform:translateY(0)!important}}
.card--content .cover>*{{opacity:1!important;transform:none!important}}
.visible li,.visible .row{{opacity:0;animation:fadeUp .55s cubic-bezier(.22,1,.36,1) forwards}}
.visible li:nth-child(1),.visible .row:nth-child(1){{animation-delay:0s}}
.visible li:nth-child(2),.visible .row:nth-child(2){{animation-delay:.12s}}
.visible li:nth-child(3),.visible .row:nth-child(3){{animation-delay:.24s}}
.visible li:nth-child(4),.visible .row:nth-child(4){{animation-delay:.36s}}
.visible li:nth-child(5),.visible .row:nth-child(5){{animation-delay:.48s}}
.visible .row:nth-child(odd){{animation-name:slideFromLeft}}
.visible .row:nth-child(even){{animation-name:slideFromRight}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(24px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes slideFromLeft{{from{{opacity:0;transform:translateX(-40px)}}to{{opacity:1;transform:translateX(0)}}}}
@keyframes slideFromRight{{from{{opacity:0;transform:translateX(40px)}}to{{opacity:1;transform:translateX(0)}}}}

/* === CONTROLS === */
.controls{{position:fixed;bottom:0;left:0;right:0;z-index:1000;display:flex;align-items:center;gap:12px;padding:12px 24px;background:rgba(0,0,0,.78);backdrop-filter:blur(12px)}}
.ctrl-btn{{width:36px;height:36px;border:none;border-radius:50%;background:rgba(255,255,255,.15);color:#fff;font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .2s;flex-shrink:0}}
.ctrl-btn:hover{{background:rgba(255,255,255,.3)}}
.ctrl-btn:disabled{{opacity:.3;cursor:default}}
.ctrl-btn.play{{width:44px;height:44px;font-size:16px;background:rgba(0,169,244,.3)}}
.progress-wrap{{flex:1;height:4px;background:rgba(255,255,255,.15);border-radius:2px;overflow:hidden;cursor:pointer}}
.progress-fill{{height:100%;width:0;background:#fff;border-radius:2px;transition:width .1s linear}}
.page-indicator{{color:rgba(255,255,255,.6);font-size:12px;font-family:monospace;min-width:50px;text-align:right}}

/* === DOT NAVIGATION === */
.dots{{position:fixed;bottom:60px;left:50%;transform:translateX(-50%);display:flex;gap:8px;z-index:1001}}
.dots button{{width:8px;height:8px;border-radius:50%;border:1px solid rgba(255,255,255,.4);background:rgba(255,255,255,.2);cursor:pointer;transition:all .3s;padding:0}}
.dots button.active{{background:#fff;transform:scale(1.3)}}

/* === RESPONSIVE === */
@media(max-width:650px){{.page{{padding:8px}}.card--cover,.card--content{{width:100%;height:auto;max-height:none;aspect-ratio:{card_w}/{cover_h}}}.card--content{{aspect-ratio:{card_w}/{content_h}}}.article{{height:auto;overflow:visible}}.cover{{min-height:200px}}h2{{font-size:21px}}p,li{{font-size:15px}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important;opacity:1!important;transform:none!important}}}}
{theme_css}
</style>
</head>
<body>
<div class="deck" id="deck">
''')

    # -- PAGES --
    for i, page in enumerate(pages):
        meta = (page.get("meta") or []) + ["", ""]
        if page["type"] == "cover":
            html_parts.append(f'''  <div class="page" data-page="{i}">
    <div class="card card--cover">
      <header class="top">
        <div class="logo">{esc(brand["name"])}<span>{esc(brand["sub"])}</span></div>
        <div class="meta">{esc(meta[0])}<br/>{esc(meta[1])}</div>
      </header>
      <section class="hero">
        <div class="label" id="cover-label">{esc(page.get("label", ""))}</div>
        <h1 class="title" id="cover-title">{esc(page["title"])}</h1>
        <p class="sub" id="cover-subtitle">{esc(page.get("subtitle", ""))}</p>
      </section>
      <footer class="footer">
        <span id="cover-tags">{esc(page.get("tags", ""))}</span>
        <span class="firm" id="cover-footer">{esc(page.get("firm", ""))}</span>
      </footer>
    </div>
  </div>
''')
        else:
            sections_html = []
            for si, sec in enumerate(page.get("sections", [])):
                sec_html = f'<h2 id="{safe_id(sec.get("heading_id") or f"heading-{i}-{si}")}">{esc(sec["heading"])}</h2><div class="rule"></div>'
                for ci, comp in enumerate(sec.get("components", [])):
                    ct = comp["type"]
                    if ct == "exec":
                        sec_html += f'<div class="exec" id="{safe_id(comp.get("id") or f"{ct}-{i}-{si}-{ci}")}"><p>{esc(comp["text"])}</p></div>'
                    elif ct == "paragraph":
                        sec_html += f'<p id="{safe_id(comp.get("id") or f"{ct}-{i}-{si}-{ci}")}">{esc(comp["text"])}</p>'
                    elif ct == "blockquote":
                        sec_html += f'<blockquote id="{safe_id(comp.get("id") or f"{ct}-{i}-{si}-{ci}")}">{esc(comp["text"])}</blockquote>'
                    elif ct == "metrics":
                        items_html = ""
                        for item in comp.get("items", []):
                            items_html += (
                                f'<div class="metric"><b>{esc(item.get("label", ""))}</b>'
                                f'<span>{esc(item.get("value", ""))}</span>'
                                f'<small>{esc(item.get("desc", ""))}</small></div>'
                            )
                        sec_html += f'<div class="metrics" id="{safe_id(comp.get("id") or f"{ct}-{i}-{si}-{ci}")}">{items_html}</div>'
                    elif ct == "table":
                        rows_html = ""
                        for row in comp.get("rows", []):
                            status_class = row.get("status_class", "status")
                            if status_class not in ("status", "status-red"):
                                status_class = "status"
                            rows_html += (
                                f'<div class="row"><b>{esc(row.get("label", ""))}</b>'
                                f'<span>{esc(row.get("value", ""))}</span>'
                                f'<em class="{status_class}">{esc(row.get("status", ""))}</em></div>'
                            )
                        sec_html += f'<div class="table" id="{safe_id(comp.get("id") or f"{ct}-{i}-{si}-{ci}")}">{rows_html}</div>'
                    elif ct == "list":
                        items_html = ""
                        for item in comp.get("items", []):
                            items_html += f'<li>{esc(item)}</li>'
                        sec_html += f'<ul id="{safe_id(comp.get("id") or f"{ct}-{i}-{si}-{ci}")}">{items_html}</ul>'
                    elif ct == "grid":
                        cells_html = ""
                        for item in comp.get("items", []):
                            if isinstance(item, dict):
                                label = item.get("label", "")
                                text = item.get("text", item.get("value", ""))
                                cell_class = "cell dark" if item.get("dark") else "cell"
                                cells_html += f'<div class="{cell_class}"><b>{esc(label)}</b><span>{esc(text)}</span></div>'
                            else:
                                cells_html += f'<div class="cell"><span>{esc(item)}</span></div>'
                        sec_html += f'<div class="grid" id="{safe_id(comp.get("id") or f"{ct}-{i}-{si}-{ci}")}">{cells_html}</div>'
                sections_html.append(sec_html)

            body_content = "\n          ".join(sections_html)
            source_html = f'<div class="source"><span>{esc(title)}</span><span class="firm">{esc(page.get("page_num", ""))}</span></div>'

            html_parts.append(f'''  <div class="page" data-page="{i}">
    <div class="card card--content">
      <article class="article">
        <section class="cover">
          <div class="logo">{esc(brand["name"])}<span>{esc(brand["sub"])}</span></div>
          <div>
            <h1>{esc(page["title"])}</h1>
            <p class="sub">{esc(page.get("subtitle", ""))}</p>
            <p class="date">{esc(page.get("series", ""))} &middot; {esc(page.get("page_num", ""))}</p>
          </div>
          <div class="date">{esc(page.get("category", ""))}</div>
        </section>
        <section class="body">
          <div class="breadcrumb">{esc(page.get("breadcrumb", ""))}</div>
          {body_content}
          {source_html}
        </section>
      </article>
    </div>
  </div>
''')

    # -- CLOSE DECK + DOTS + CONTROLS + AUDIO --
    audio_src_items = ",\n      ".join([f'"__AUDIO_{i}__"' for i in range(num_pages)])

    html_parts.append(f'''</div>

<!-- Dot navigation -->
<div class="dots" id="dots"></div>

<!-- Playback controls -->
<div class="controls" id="controls">
  <button id="btnPrev" class="ctrl-btn" aria-label="上一页">&#9664;</button>
  <button id="btnPlay" class="ctrl-btn play" aria-label="播放或暂停">&#9654;</button>
  <button id="btnNext" class="ctrl-btn" aria-label="下一页">&#9654;</button>
  <div class="progress-wrap" id="progressWrap">
    <div class="progress-fill" id="progressFill"></div>
  </div>
  <span class="page-indicator" id="pageIndicator">1 / {num_pages}</span>
</div>

<audio id="narration" preload="auto"></audio>

<script>
var TIMELINE = __TIMELINE__;
var AUDIO_SRC = [
  {audio_src_items}
];

(function() {{
  'use strict';
  var deck = document.getElementById('deck');
  var pages = document.querySelectorAll('.page');
  var audio = document.getElementById('narration');
  var btnPlay = document.getElementById('btnPlay');
  var btnPrev = document.getElementById('btnPrev');
  var btnNext = document.getElementById('btnNext');
  var progressFill = document.getElementById('progressFill');
  var progressWrap = document.getElementById('progressWrap');
  var pageIndicator = document.getElementById('pageIndicator');
  var dotsContainer = document.getElementById('dots');
  var currentPage = 0;
  var totalPages = pages.length;
  var isPlaying = false;
  var triggered = {{}};
  var rafId = null;
  var pageStartTime = 0;

  /* Expose to window for external control (e.g. record_video.js) */
  window.__lf = {{ triggered: triggered }};

  function initElements() {{
    var sels = '.cover > *,.body > .breadcrumb,.body > h2,.body > .rule,.body > .exec,.body > p,.body > ul,.body > .table,.body > blockquote,.body > .source,.body > .metrics,.body > .grid,#cover-label,#cover-title,#cover-subtitle,#cover-tags,#cover-footer';
    document.querySelectorAll(sels).forEach(function(el) {{
      if (!el.id) el.classList.add('anim-auto');
      el.style.opacity = '0';
    }});
  }}

  function autoFitArticles() {{
    var vh = window.innerHeight;
    document.querySelectorAll('.card--content').forEach(function(card) {{
      card.style.transform = '';
      card.style.position = '';
      card.style.transformOrigin = '';
      if (card.parentElement && card.parentElement.classList.contains('card-fit')) {{
        var old = card.parentElement;
        old.parentElement.insertBefore(card, old);
        old.remove();
      }}
      var article = card.querySelector('.article');
      if (!article) return;
      var prevH = article.style.height;
      article.style.height = 'auto';
      var naturalH = article.scrollHeight;
      article.style.height = prevH || '';
      var availH = vh - 120;
      var maxH = card.offsetHeight;
      if (maxH > 0 && maxH < availH) availH = maxH;
      if (naturalH > availH) {{
        var scale = availH / naturalH;
        var cardW = card.offsetWidth;
        var wrap = document.createElement('div');
        wrap.className = 'card-fit';
        wrap.style.cssText = 'width:' + cardW + 'px;height:' + Math.round(naturalH * scale) + 'px;position:relative;overflow:hidden;flex-shrink:0';
        card.parentElement.insertBefore(wrap, card);
        wrap.appendChild(card);
        card.style.transformOrigin = 'top left';
        card.style.transform = 'scale(' + scale.toFixed(4) + ')';
        card.style.position = 'absolute';
        card.style.top = '0';
        card.style.left = '0';
      }}
    }});
  }}

  function triggerEl(id) {{
    var el = document.getElementById(id);
    if (!el) return;
    el.style.opacity = '';
    el.classList.add('visible');
    if (el.tagName === 'UL') {{
      Array.from(el.querySelectorAll('li')).forEach(function(li, i) {{
        setTimeout(function() {{ li.style.opacity = ''; li.classList.add('visible'); }}, i * 200);
      }});
    }}
    if (el.classList.contains('table')) {{
      Array.from(el.querySelectorAll('.row')).forEach(function(r, i) {{
        setTimeout(function() {{ r.style.opacity = ''; r.classList.add('visible'); }}, i * 200);
      }});
    }}
  }}

  /* Expose playback functions for external control */
  window.__lf.triggerEl = triggerEl;

  function loadAudio(idx) {{
    var src = AUDIO_SRC[idx];
    if (src && src.indexOf('__AUDIO') === -1) {{
      audio.src = src;
      audio.load();
    }} else if (!src) {{
      audio.removeAttribute('src');
      audio.load();
    }}
  }}

  function goTo(idx) {{
    if (idx < 0 || idx >= totalPages) return;
    stop();
    currentPage = idx;
    pages[idx].scrollIntoView({{ behavior: 'smooth', inline: 'center' }});
    triggered[idx] = {{}};
    loadAudio(idx);
    updateUI();
    updateDots();
    history.replaceState(null, '', '#page=' + idx);
    setTimeout(function() {{ start(); }}, 500);
  }}

  function start() {{
    if (isPlaying) return;
    isPlaying = true;
    btnPlay.innerHTML = '&#9646;&#9646;';
    pageStartTime = performance.now();
    audio.play().catch(function() {{}});
    tick();
  }}

  function stop() {{
    isPlaying = false;
    btnPlay.innerHTML = '&#9654;';
    audio.pause();
    if (rafId) cancelAnimationFrame(rafId);
  }}

  function toggle() {{
    if (isPlaying) stop(); else start();
  }}

  var ELEMENT_LEAD = 0.4; /* trigger elements 0.4s before audio for natural feel */

  function tick() {{
    if (!isPlaying) return;
    var pd = TIMELINE && TIMELINE.pages ? TIMELINE.pages[currentPage] : null;
    var hasAudio = pd && !!pd.audio_base64;
    var t = hasAudio ? audio.currentTime : ((performance.now() - pageStartTime) / 1000);
    if (pd) {{
      pd.segments.forEach(function(seg, si) {{
        if (t >= seg.start - ELEMENT_LEAD && !(triggered[currentPage] || {{}})[si]) {{
          if (!triggered[currentPage]) triggered[currentPage] = {{}};
          triggered[currentPage][si] = true;
          seg.elements.forEach(function(eid) {{ triggerEl(eid); }});
        }}
      }});
      var pct = pd.duration > 0 ? (t / pd.duration) * 100 : 0;
      progressFill.style.width = Math.min(pct, 100) + '%';
      if (t >= pd.duration - 0.15 && currentPage < totalPages - 1) {{
        goTo(currentPage + 1);
        return;
      }}
    }}
    rafId = requestAnimationFrame(tick);
  }}

  /* Expose remaining playback functions for external control */
  window.__lf.tick = tick;
  window.__lf.start = start;
  window.__lf.stop = stop;
  window.__lf.goTo = goTo;
  Object.defineProperty(window.__lf, 'isPlaying', {{
    get: function() {{ return isPlaying; }},
    set: function(v) {{ isPlaying = v; }}
  }});

  function updateUI() {{
    pageIndicator.textContent = (currentPage + 1) + ' / ' + totalPages;
    btnPrev.disabled = currentPage === 0;
    btnNext.disabled = currentPage === totalPages - 1;
  }}

  /* -- Dot navigation -- */
  function buildDots() {{
    if (!dotsContainer) return;
    pages.forEach(function(_, i) {{
      var btn = document.createElement('button');
      btn.setAttribute('aria-label', '第 ' + (i + 1) + ' 页');
      btn.addEventListener('click', function() {{ goTo(i); }});
      dotsContainer.appendChild(btn);
    }});
  }}
  function updateDots() {{
    if (!dotsContainer) return;
    dotsContainer.querySelectorAll('button').forEach(function(b, i) {{
      b.classList.toggle('active', i === currentPage);
    }});
  }}

  /* -- Scroll sync -- */
  var scrollTimer;
  deck.addEventListener('scroll', function() {{
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(function() {{
      var center = deck.scrollLeft + deck.clientWidth / 2;
      pages.forEach(function(p, i) {{
        if (center >= p.offsetLeft && center < p.offsetLeft + p.offsetWidth) {{
          if (i !== currentPage) {{
            stop();
            currentPage = i;
            triggered[i] = {{}};
            loadAudio(i);
            updateUI();
            updateDots();
          }}
        }}
      }});
    }}, 120);
  }});

  /* -- Events -- */
  btnPlay.addEventListener('click', toggle);
  btnPrev.addEventListener('click', function() {{ goTo(currentPage - 1); }});
  btnNext.addEventListener('click', function() {{ goTo(currentPage + 1); }});

  progressWrap.addEventListener('click', function(e) {{
    var rect = progressWrap.getBoundingClientRect();
    var pct = (e.clientX - rect.left) / rect.width;
    var pd = TIMELINE && TIMELINE.pages ? TIMELINE.pages[currentPage] : null;
    if (pd && audio.duration) audio.currentTime = pct * audio.duration;
  }});

  document.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {{ e.preventDefault(); goTo(currentPage + 1); }}
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{ e.preventDefault(); goTo(currentPage - 1); }}
    if (e.key === ' ') {{ e.preventDefault(); toggle(); }}
    if (e.key === 'Home') {{ e.preventDefault(); goTo(0); }}
    if (e.key === 'End') {{ e.preventDefault(); goTo(totalPages - 1); }}
  }});

  /* -- Init -- */
  initElements();
  autoFitArticles();
  buildDots();
  loadAudio(0);
  updateUI();
  updateDots();
  window.addEventListener('resize', autoFitArticles);

  var hashMatch = location.hash.match(/page=(\\d+)/);
  if (hashMatch) {{
    var initPage = parseInt(hashMatch[1]);
    if (initPage > 0 && initPage < totalPages) goTo(initPage);
  }} else {{
    setTimeout(function() {{ start(); }}, 1200);
  }}

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
    document.querySelectorAll('[style*="opacity: 0"]').forEach(function(el) {{
      el.style.opacity = '1';
    }});
  }}
}})();
</script>
</body>
</html>''')

    # -- Write draft.html --
    html_content = "\n".join(html_parts)
    draft_path = os.path.join(out, "draft.html")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"draft.html written: {len(html_content):,} chars")
    print(f"Pages: {num_pages}")
    print(f"Aspect ratio: {aspect_ratio} ({card_w}x{card_h})")
    print(f"Cover card: {card_w}x{cover_h}")
    print(f"Audio placeholders: {num_pages} (__AUDIO_0__ .. __AUDIO_{num_pages-1}__)")
    print(f"Timeline placeholder: __TIMELINE__")


if __name__ == "__main__":
    main()
