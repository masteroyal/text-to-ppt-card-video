#!/usr/bin/env python3
"""
moss_tts_engine.py — MOSS-TTS-Nano wrapper for text-to-ppt-card-video build pipeline.

Provides synthesize_moss(text, voice, output_mp3_path) that:
1. Calls infer_onnx.py via subprocess
2. Converts WAV output to MP3 via ffmpeg

Model downloads use the existing HF_ENDPOINT environment variable. Set
MOSS_HF_MIRROR=1 to switch to https://hf-mirror.com.

Built-in Chinese voices:
    Junhao  — male, professional (default)
    Zhiming — male, warm
    Weiguo  — male, steady
    Xiaoyu  — female, gentle
    Yuewen  — female, clear
    Lingyu  — female, lively

Usage as module:
    from moss_tts_engine import synthesize_moss, MOSS_VOICES
    synthesize_moss("你好世界", "Junhao", "/tmp/output.mp3")

Usage as CLI:
    python moss_tts_engine.py --text "你好" --voice Junhao --output output.mp3
"""

import os
import sys
import subprocess
import tempfile
import argparse

from tts_common import MOSS_DEFAULT_VOICE, MOSS_VOICES, find_bin

# ── Path setup ───────────────────────────────────────────────────────
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
MOSS_DIR = os.path.join(SKILL_DIR, "moss-tts-nano")
FFMPEG = find_bin("ffmpeg") or "ffmpeg"


def _configure_hf_endpoint(env):
    """Apply the Hugging Face mirror only when the caller opts in."""
    if os.environ.get("MOSS_HF_MIRROR") in ("1", "true", "True", "yes"):
        env["HF_ENDPOINT"] = "https://hf-mirror.com"


def synthesize_moss(text, voice, output_mp3_path, verbose=False):
    """
    Generate speech audio using MOSS-TTS-Nano ONNX backend.

    Args:
        text: Chinese text to synthesize
        voice: Voice preset name (e.g. "Junhao", "Xiaoyu")
        output_mp3_path: Where to save the output MP3 file
        verbose: If True, print MOSS-TTS logs to stdout

    Returns:
        output_mp3_path on success, raises on failure.
    """
    if voice not in MOSS_VOICES:
        raise ValueError(f"Unknown MOSS voice: {voice}. Available: {list(MOSS_VOICES.keys())}")

    infer_script = os.path.join(MOSS_DIR, "infer_onnx.py")
    if not os.path.isfile(infer_script):
        raise RuntimeError(
            f"MOSS-TTS-Nano not found at: {MOSS_DIR}\n"
            f"Run: python {os.path.join(SKILL_DIR, 'setup_local_tts.py')} --engine moss\n"
            f"Or switch to Edge TTS (set tts_engine to 'edge' in manifest.json)."
        )

    # Create temp WAV path
    tmp_wav = output_mp3_path + ".tmp.wav"

    try:
        # Build command
        cpu_threads = os.environ.get("MOSS_CPU_THREADS", "4")
        timeout = int(os.environ.get("MOSS_TIMEOUT_SECONDS", "120"))
        cmd = [
            sys.executable, os.path.join(MOSS_DIR, "infer_onnx.py"),
            "--text", text,
            "--voice", voice,
            "--output-audio-path", tmp_wav,
            "--disable-wetext-processing",
            "--execution-provider", "cpu",
            "--cpu-threads", cpu_threads,
        ]

        # Set environment
        env = os.environ.copy()
        _configure_hf_endpoint(env)

        # Run inference
        result = subprocess.run(
            cmd,
            cwd=MOSS_DIR,
            capture_output=not verbose,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=timeout,
        )

        if result.returncode != 0:
            stderr = result.stderr if not verbose else ""
            raise RuntimeError(f"MOSS-TTS inference failed (exit {result.returncode}): {stderr[-500:]}")

        if not os.path.exists(tmp_wav):
            raise RuntimeError(f"MOSS-TTS did not produce output: {tmp_wav}")

        # Convert WAV to MP3
        ffmpeg_cmd = [
            FFMPEG, "-y",
            "-i", tmp_wav,
            "-c:a", "libmp3lame", "-b:a", "192k",
            "-ar", "24000", "-ac", "1",
            output_mp3_path,
        ]
        conv = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if conv.returncode != 0:
            raise RuntimeError(f"FFmpeg WAV->MP3 failed: {conv.stderr[-500:]}")

        return output_mp3_path

    finally:
        # Clean up temp WAV
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)


# ── CLI entry point ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MOSS-TTS-Nano synthesis wrapper")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--voice", default=MOSS_DEFAULT_VOICE,
                        choices=list(MOSS_VOICES.keys()),
                        help=f"Voice preset (default: {MOSS_DEFAULT_VOICE})")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    parser.add_argument("--verbose", action="store_true", help="Show MOSS-TTS logs")
    args = parser.parse_args()

    result = synthesize_moss(args.text, args.voice, args.output, verbose=args.verbose)
    print(f"[moss-tts] Saved: {result}")


if __name__ == "__main__":
    main()
