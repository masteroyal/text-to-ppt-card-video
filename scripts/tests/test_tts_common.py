import os
import unittest
from unittest import mock

import tts_common


class TtsCommonTest(unittest.TestCase):
    def test_default_voices_are_known(self):
        self.assertIn(tts_common.DEFAULT_VOICE, tts_common.VALID_VOICES)
        self.assertIn(tts_common.MOSS_DEFAULT_VOICE, tts_common.MOSS_VOICES)
        self.assertIn(tts_common.COSYVOICE_DEFAULT_VOICE, tts_common.COSYVOICE_VOICES)
        self.assertIn(tts_common.DASHSCOPE_DEFAULT_VOICE, tts_common.DASHSCOPE_VOICES)

    def test_find_cosyvoice_python_uses_environment(self):
        with mock.patch.dict(os.environ, {"COSYVOICE_PYTHON": r"C:\custom\python.exe"}):
            self.assertEqual(
                tts_common.find_cosyvoice_python(),
                r"C:\custom\python.exe",
            )


if __name__ == "__main__":
    unittest.main()
