import json
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import gen_draft
from gen_draft import validate_manifest


def render(manifest):
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False)
        old_argv = sys.argv
        sys.argv = ["gen_draft.py", tmp]
        try:
            gen_draft.main()
        finally:
            sys.argv = old_argv
        with open(os.path.join(tmp, "draft.html"), "r", encoding="utf-8") as f:
            return f.read()


def cover_page(**overrides):
    page = {
        "type": "cover",
        "title": "T",
        "subtitle": "S",
        "tags": "",
        "firm": "",
        "label": "",
        "meta": ["", ""],
        "narration": [],
    }
    page.update(overrides)
    return page


class GenDraftTest(unittest.TestCase):
    def test_safe_id_keeps_safe_chars(self):
        self.assertEqual(gen_draft.safe_id("p1-s1-heading"), "p1-s1-heading")

    def test_safe_id_hashes_non_ascii_input(self):
        self.assertRegex(gen_draft.safe_id("章节标题"), r"^el-[0-9a-f]{10}$")
        self.assertEqual(gen_draft.safe_id("章节标题"), gen_draft.safe_id("章节标题"))
        self.assertNotEqual(gen_draft.safe_id("章节标题"), gen_draft.safe_id("组件"))

    def test_validate_manifest_reports_field_path(self):
        with self.assertRaisesRegex(ValueError, r"pages\[0\]\.title"):
            validate_manifest({"pages": [{"type": "cover"}]})

    def test_validate_manifest_reports_component_path(self):
        manifest = {
            "pages": [{
                "type": "content",
                "title": "P",
                "sections": [{
                    "heading": "H",
                    "components": [{"type": "unknown"}],
                }],
            }]
        }
        with self.assertRaisesRegex(ValueError, r"pages\[0\]\.sections\[0\]\.components\[0\]\.type"):
            validate_manifest(manifest)

    def test_validate_manifest_rejects_duplicate_ids(self):
        manifest = {
            "pages": [{
                "type": "content",
                "title": "P",
                "sections": [{
                    "heading": "H",
                    "heading_id": "same",
                    "components": [{"type": "exec", "id": "same", "text": "x"}],
                }],
            }]
        }
        with self.assertRaisesRegex(ValueError, "must be unique"):
            validate_manifest(manifest)

    def test_validate_manifest_rejects_bad_id_chars(self):
        manifest = {
            "pages": [{
                "type": "content",
                "title": "P",
                "sections": [{
                    "heading": "H",
                    "heading_id": "has space",
                    "components": [],
                }],
            }]
        }
        with self.assertRaisesRegex(ValueError, "must use only ASCII"):
            validate_manifest(manifest)

    def test_validate_manifest_rejects_unknown_narration_ref(self):
        manifest = {
            "pages": [{
                "type": "content",
                "title": "P",
                "sections": [{
                    "heading": "H",
                    "heading_id": "h1",
                    "components": [{"type": "exec", "id": "e1", "text": "x"}],
                }],
                "narration": [{"text": "hi", "elements": ["missing"]}],
            }]
        }
        with self.assertRaisesRegex(ValueError, "references unknown id"):
            validate_manifest(manifest)

    def test_missing_ids_get_unique_fallbacks(self):
        html = render({
            "title": "T",
            "theme": "consulting-report",
            "pages": [{
                "type": "content",
                "title": "P",
                "subtitle": "S",
                "series": "X",
                "page_num": "1/1",
                "category": "C",
                "breadcrumb": "B",
                "sections": [{
                    "heading": "H",
                    "components": [
                        {"type": "exec", "text": "a"},
                        {"type": "exec", "text": "b"},
                    ],
                }],
                "narration": [],
            }],
        })
        ids = re.findall(r'id="([^"]+)"', html)
        self.assertEqual(len(ids), len(set(ids)))

    def test_player_uses_wall_clock_for_pages_without_audio(self):
        html = render({"title": "T", "theme": "consulting-report", "pages": [cover_page()]})
        self.assertIn("var pageStartTime", html)
        self.assertIn("performance.now() - pageStartTime", html)

    def test_controls_have_accessibility_labels(self):
        html = render({"title": "T", "theme": "consulting-report", "pages": [cover_page()]})
        self.assertIn('aria-label="\u4e0a\u4e00\u9875"', html)
        self.assertIn('aria-label="\u4e0b\u4e00\u9875"', html)
        self.assertIn('aria-label="\u64ad\u653e\u6216\u6682\u505c"', html)
        self.assertIn(
            "btn.setAttribute('aria-label', '\u7b2c ' + (i + 1) + ' \u9875');",
            html,
        )

    def test_metric_uses_serif_variable(self):
        html = render({
            "title": "T",
            "theme": "consulting-report",
            "pages": [{
                "type": "content",
                "title": "P",
                "subtitle": "S",
                "series": "X",
                "page_num": "1/1",
                "category": "C",
                "breadcrumb": "B",
                "sections": [{
                    "heading": "H",
                    "heading_id": "s1-heading",
                    "components": [{
                        "type": "metrics",
                        "id": "s1-metrics",
                        "items": [{"label": "A", "value": "1", "desc": "x"}],
                    }],
                }],
                "narration": [],
            }],
        })
        self.assertIn("font-family:var(--serif);font-size:36px", html)

    def test_table_uses_status_class(self):
        html = render({
            "title": "T",
            "theme": "consulting-report",
            "pages": [{
                "type": "content",
                "title": "P",
                "subtitle": "S",
                "series": "X",
                "page_num": "1/1",
                "category": "C",
                "breadcrumb": "B",
                "sections": [{
                    "heading": "H",
                    "heading_id": "s1-heading",
                    "components": [{
                        "type": "table",
                        "id": "s1-table",
                        "rows": [
                            {"label": "A", "value": "B", "status": "done"},
                            {"label": "C", "value": "D", "status": "todo", "status_class": "status-red"},
                        ],
                    }],
                }],
                "narration": [],
            }],
        })
        self.assertIn('<em class="status">done</em>', html)
        self.assertIn('<em class="status-red">todo</em>', html)

    def test_escapes_manifest_content(self):
        html = render({
            "title": "A&B <script>alert(1)</script>",
            "brand": {"name": "N&N", "sub": 'x"y'},
            "theme": "consulting-report",
            "pages": [cover_page(title="<b>Hi</b>", subtitle="sub & more")],
        })
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("A&amp;B", html)

    def test_theme_css_injected(self):
        html = render({"title": "T", "theme": "editorial", "pages": [cover_page()]})
        self.assertIn("--paper:#faf8f3", html)

    def test_unknown_theme_falls_back(self):
        html = render({"title": "T", "theme": "nope", "pages": [cover_page()]})
        self.assertIn("--navy:#1b2a4a", html)

    def test_cover_without_meta_renders(self):
        html = render({"title": "T", "theme": "consulting-report", "pages": [cover_page(meta=[])]})
        self.assertIn('<div class="meta"><br/></div>', html)

    def test_cover_elements_are_animatable(self):
        html = render({"title": "T", "theme": "consulting-report", "pages": [cover_page()]})
        self.assertIn("#cover-title,#cover-subtitle", html)
        self.assertIn("#cover-title.visible", html)
        self.assertIn("var sels = '.cover > *,.body > .breadcrumb", html)
        self.assertIn("#cover-label,#cover-title,#cover-subtitle", html)

    def test_blockquote_and_grid_rendered(self):
        html = render({
            "title": "T",
            "theme": "consulting-report",
            "pages": [{
                "type": "content",
                "title": "P",
                "subtitle": "S",
                "series": "X",
                "page_num": "1/1",
                "category": "C",
                "breadcrumb": "B",
                "sections": [{
                    "heading": "H",
                    "heading_id": "s1-heading",
                    "components": [
                        {"type": "blockquote", "id": "s1-quote", "text": "<quoted>"},
                        {"type": "grid", "id": "s1-grid", "items": [
                            {"label": "A", "text": "B", "dark": True},
                            "plain",
                        ]},
                    ],
                }],
                "narration": [],
            }],
        })
        self.assertIn('<blockquote id="s1-quote">&lt;quoted&gt;</blockquote>', html)
        self.assertIn('<div class="grid" id="s1-grid">', html)
        self.assertIn('class="cell dark"', html)


if __name__ == "__main__":
    unittest.main()
