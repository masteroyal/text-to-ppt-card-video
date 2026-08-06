import asyncio
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import build
import cosyvoice_engine
import tts_common


class BuildTest(unittest.TestCase):
    def test_voice_maps_are_shared(self):
        self.assertIs(build.VALID_VOICES, tts_common.VALID_VOICES)
        self.assertIs(build.MOSS_VOICES, tts_common.MOSS_VOICES)
        self.assertIs(build.COSYVOICE_VOICES, tts_common.COSYVOICE_VOICES)
        self.assertIs(build.DASHSCOPE_VOICES, tts_common.DASHSCOPE_VOICES)

    def test_inject_into_html_replaces_placeholders(self):
        draft = (
            "<script>var TIMELINE = __TIMELINE__;</script>\n"
            'var AUDIO_SRC = ["__AUDIO_0__"];'
        )
        timeline = {
            "pages": [{
                "audio_base64": "data:audio/mp3;base64,AAAA",
                "duration": 1.0,
                "segments": [],
            }]
        }
        with tempfile.TemporaryDirectory() as tmp:
            draft_path = os.path.join(tmp, "draft.html")
            out_path = os.path.join(tmp, "final.html")
            with open(draft_path, "w", encoding="utf-8") as f:
                f.write(draft)
            build.inject_into_html(draft_path, timeline, out_path)
            with open(out_path, encoding="utf-8") as f:
                html = f.read()
            self.assertIn("data:audio/mp3;base64,AAAA", html)
            self.assertNotIn("__AUDIO_0__", html)

    def test_inject_into_html_fails_on_remaining_placeholders(self):
        draft = (
            "<script>var TIMELINE = __TIMELINE__;</script>\n"
            'var AUDIO_SRC = ["__AUDIO_0__"];'
        )
        with tempfile.TemporaryDirectory() as tmp:
            draft_path = os.path.join(tmp, "draft.html")
            out_path = os.path.join(tmp, "final.html")
            with open(draft_path, "w", encoding="utf-8") as f:
                f.write(draft)
            with self.assertRaises(RuntimeError):
                build.inject_into_html(draft_path, {"pages": []}, out_path)

    def test_inject_into_html_replaces_empty_audio(self):
        draft = (
            "<script>var TIMELINE = __TIMELINE__;</script>\n"
            'var AUDIO_SRC = ["__AUDIO_0__"];'
        )
        timeline = {
            "pages": [{
                "audio_base64": "",
                "duration": 0.0,
                "segments": [],
            }]
        }
        with tempfile.TemporaryDirectory() as tmp:
            draft_path = os.path.join(tmp, "draft.html")
            out_path = os.path.join(tmp, "final.html")
            with open(draft_path, "w", encoding="utf-8") as f:
                f.write(draft)
            build.inject_into_html(draft_path, timeline, out_path)
            with open(out_path, encoding="utf-8") as f:
                html = f.read()
            self.assertIn('var AUDIO_SRC = [""];', html)
            self.assertNotIn("__AUDIO_0__", html)

    def test_process_pages_fails_fast_on_missing_audio(self):
        async def fake_generate(*args, **kwargs):
            return [["missing.mp3"]]

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("build.generate_all_segments", side_effect=fake_generate):
                with self.assertRaises(RuntimeError):
                    build.process_pages(
                        [{"title": "P", "narration": [{"text": "hi", "elements": []}]}],
                        "YunxiNeural",
                        tmp,
                    )

    def test_process_pages_fails_fast_on_empty_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_path = os.path.join(tmp, "seg_0_0.mp3")
            with open(empty_path, "w", encoding="utf-8") as f:
                f.write("")

            async def fake_generate(*args, **kwargs):
                return [[empty_path]]

            with mock.patch("build.generate_all_segments", side_effect=fake_generate):
                with self.assertRaisesRegex(RuntimeError, "no audio"):
                    build.process_pages(
                        [{"title": "P", "narration": [{"text": "hi", "elements": []}]}],
                        "YunxiNeural",
                        tmp,
                    )

    def test_generate_all_segments_fails_on_tts_error(self):
        async def fake_tts(*args, **kwargs):
            raise RuntimeError("tts unavailable")

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("build.generate_tts", side_effect=fake_tts):
                with self.assertRaisesRegex(RuntimeError, "TTS segments failed"):
                    asyncio.run(build.generate_all_segments(
                        [{"title": "P", "narration": [{"text": "hi", "elements": []}]}],
                        "YunxiNeural",
                        tmp,
                    ))

    def test_no_narration_page_gets_static_duration(self):
        async def fake_generate(*args, **kwargs):
            return [[]]

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("build.generate_all_segments", side_effect=fake_generate):
                timeline = build.process_pages(
                    [{"title": "P", "narration": []}],
                    "YunxiNeural",
                    tmp,
                )
        self.assertEqual(timeline["pages"][0]["duration"], build.STATIC_PAGE_SECONDS)
        self.assertEqual(timeline["pages"][0]["audio_base64"], "")

    def test_cosyvoice_batch_failure_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch(
                "build.subprocess.run", return_value=mock.Mock(returncode=1)
            ):
                with self.assertRaisesRegex(RuntimeError, "CosyVoice batch exited"):
                    build._generate_all_segments_cosyvoice(
                        [{"narration": [{"text": "hi", "elements": []}]}],
                        "中文女",
                        tmp,
                    )

    def test_cosyvoice_engine_batch_failure_exits_nonzero(self):
        import json

        segments = [{"text": "hi", "output": "out.mp3"}]
        with tempfile.TemporaryDirectory() as tmp:
            batch_path = os.path.join(tmp, "batch.json")
            with open(batch_path, "w", encoding="utf-8") as f:
                json.dump(segments, f)
            with mock.patch(
                "cosyvoice_engine.synthesize_batch",
                return_value=[{"output": "out.mp3", "ok": False, "error": "boom"}],
            ), mock.patch(
                "sys.argv",
                ["cosyvoice_engine.py", "--batch", batch_path, "--voice", "中文女"],
            ):
                with self.assertRaises(SystemExit) as cm:
                    cosyvoice_engine.main()
            self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
