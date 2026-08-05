import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import build
import gen_draft
import split_pages


class SplitPagesTest(unittest.TestCase):
    def test_split_roundtrip(self):
        manifest = {
            "title": "T",
            "theme": "consulting-report",
            "brand": {"name": "N", "sub": "S"},
            "pages": [
                {
                    "type": "cover",
                    "title": "T",
                    "subtitle": "S",
                    "tags": "",
                    "firm": "",
                    "label": "",
                    "meta": ["", ""],
                    "narration": [],
                },
                {
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
                        "components": [{"type": "exec", "id": "s1-exec", "text": "X"}],
                    }],
                    "narration": [],
                },
            ],
        }
        timeline = {
            "pages": [
                {
                    "audio_base64": "data:audio/mp3;base64,AAAA",
                    "duration": 1.0,
                    "segments": [],
                },
                {
                    "audio_base64": "",
                    "duration": 0.0,
                    "segments": [],
                },
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False)
            old_argv = sys.argv
            try:
                sys.argv = ["gen_draft.py", tmp]
                gen_draft.main()
                build.inject_into_html(
                    os.path.join(tmp, "draft.html"),
                    timeline,
                    os.path.join(tmp, "final.html"),
                )
                sys.argv = ["split_pages.py", tmp]
                split_pages.main()
            finally:
                sys.argv = old_argv

            for name in ("page_0.html", "page_1.html"):
                self.assertTrue(os.path.isfile(os.path.join(tmp, "pages", name)), name)
            with open(os.path.join(tmp, "pages", "page_0.html"), encoding="utf-8") as f:
                page0 = f.read()
            with open(os.path.join(tmp, "pages", "page_1.html"), encoding="utf-8") as f:
                page1 = f.read()
            self.assertIn('data-page="0"', page0)
            self.assertIn('data-page="0"', page1)
            self.assertIn("data:audio/mp3;base64,AAAA", page0)
            self.assertIn('var AUDIO_SRC = [""];', page1)


if __name__ == "__main__":
    unittest.main()
