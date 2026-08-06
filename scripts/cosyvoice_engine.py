"""
cosyvoice_engine.py - Wrapper for CosyVoice TTS inference.

Runs under the conda Python 3.10 environment (cosyvoice).
Called as subprocess from build.py.

Available voices (CosyVoice-300M-SFT built-in speakers):
    中文女 - female, standard Chinese (default)
    中文男 - male, standard Chinese
    英文女 - female, English
    英文男 - male, English

Usage as module:
    from cosyvoice_engine import synthesize_cosyvoice, COSYVOICE_VOICES
    synthesize_cosyvoice("你好世界", "中文女", "/tmp/output.mp3")

Usage as CLI (single):
    python cosyvoice_engine.py --text "你好" --voice 中文女 --output out.mp3

Usage as CLI (batch - loads model once, processes all segments):
    python cosyvoice_engine.py --batch segments.json --voice 中文女
    # segments.json format: [{"text": "...", "output": "out.mp3"}, ...]
"""

import os
import sys
import subprocess
import argparse

from tts_common import COSYVOICE_DEFAULT_VOICE, COSYVOICE_VOICES, find_bin

# -- Path setup -------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COSYVOICE_DIR = os.path.join(SCRIPT_DIR, "cosyvoice")
MODEL_DIR = os.path.join(COSYVOICE_DIR, "pretrained_models", "CosyVoice-300M-SFT")

# Add CosyVoice source to path
sys.path.insert(0, os.path.join(COSYVOICE_DIR, "third_party", "Matcha-TTS"))
sys.path.insert(0, COSYVOICE_DIR)

FFMPEG = find_bin("ffmpeg") or "ffmpeg"

# -- Model singleton --------------------------------------------------
_model = None

def _get_model():
    global _model
    if _model is None:
        if not os.path.isdir(MODEL_DIR):
            raise RuntimeError(
                f"CosyVoice model not found at: {MODEL_DIR}\n"
                f"Run: python {os.path.join(SCRIPT_DIR, 'setup_local_tts.py')} --engine cosyvoice\n"
                f"Or switch to Edge TTS (set tts_engine to 'edge' in manifest.json)."
            )
        import torch
        torch.set_num_threads(os.cpu_count() or 8)
        from cosyvoice.cli.cosyvoice import CosyVoice
        _model = CosyVoice(MODEL_DIR)
    return _model

# -- Synthesis --------------------------------------------------------

def synthesize_cosyvoice(text, voice, output_mp3_path, verbose=False):
    """Synthesize speech using CosyVoice and save as MP3."""
    if voice not in COSYVOICE_VOICES:
        raise ValueError(f"Unknown CosyVoice: {voice}. Available: {list(COSYVOICE_VOICES.keys())}")

    model = _get_model()
    tmp_wav = output_mp3_path + ".tmp.wav"

    try:
        # Run inference
        audio_chunks = list(model.inference_sft(text, voice, stream=False))
        if not audio_chunks:
            raise RuntimeError("CosyVoice produced no audio output")

        # Concatenate chunks and save WAV
        import torchaudio
        import torch
        all_speech = torch.cat([chunk['tts_speech'] for chunk in audio_chunks], dim=1)
        torchaudio.save(tmp_wav, all_speech, model.sample_rate)

        if not os.path.exists(tmp_wav):
            raise RuntimeError(f"CosyVoice did not produce output: {tmp_wav}")

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
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)


# -- Batch synthesis --------------------------------------------------

def synthesize_batch(segments, voice, verbose=False):
    """Synthesize multiple segments in one model session.
    segments: list of {"text": str, "output": str}
    Returns list of {"output": str, "ok": bool, "error": str|None}
    """
    import json
    if not segments:
        return []
    model = _get_model()
    import torch, torchaudio

    results = []
    total = len(segments)
    # Write progress to a log file (since stdout may be suppressed)
    progress_log = os.path.join(os.path.dirname(segments[0]["output"]), "progress.log")
    with open(progress_log, "w", encoding="utf-8") as pf:
        pf.write(f"START {total} segments\n")
    for i, seg in enumerate(segments):
        text = seg["text"]
        out_mp3 = seg["output"]
        tmp_wav = out_mp3 + ".tmp.wav"
        try:
            audio_chunks = list(model.inference_sft(text, voice, stream=False))
            if not audio_chunks:
                raise RuntimeError("No audio output")
            all_speech = torch.cat([c['tts_speech'] for c in audio_chunks], dim=1)
            torchaudio.save(tmp_wav, all_speech, model.sample_rate)
            # WAV -> MP3
            ffmpeg_cmd = [
                FFMPEG, "-y", "-i", tmp_wav,
                "-c:a", "libmp3lame", "-b:a", "192k",
                "-ar", "24000", "-ac", "1", out_mp3,
            ]
            conv = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if conv.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {conv.stderr[-300:]}")
            results.append({"output": out_mp3, "ok": True, "error": None})
            with open(progress_log, "a", encoding="utf-8") as pf:
                pf.write(f"OK {i+1}/{total} {os.path.basename(out_mp3)}\n")
            print(f"  [{i+1}/{total}] OK: {text[:20]}... -> {os.path.basename(out_mp3)}", flush=True)
        except Exception as e:
            results.append({"output": out_mp3, "ok": False, "error": str(e)})
            with open(progress_log, "a", encoding="utf-8") as pf:
                pf.write(f"FAIL {i+1}/{total} {os.path.basename(out_mp3)} {e}\n")
            print(f"  [{i+1}/{total}] FAIL: {text[:20]}... -> {e}", flush=True)
        finally:
            if os.path.exists(tmp_wav):
                os.remove(tmp_wav)
    return results


# -- CLI entry point --------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CosyVoice TTS synthesis wrapper")
    parser.add_argument("--text", help="Text to synthesize (single mode)")
    parser.add_argument("--batch", help="JSON file with list of {text, output} (batch mode)")
    parser.add_argument("--voice", default=COSYVOICE_DEFAULT_VOICE,
                        choices=list(COSYVOICE_VOICES.keys()),
                        help=f"Voice preset (default: {COSYVOICE_DEFAULT_VOICE})")
    parser.add_argument("--output", help="Output MP3 path (single mode)")
    parser.add_argument("--verbose", action="store_true", help="Show CosyVoice logs")
    args = parser.parse_args()

    if args.batch:
        # Batch mode
        import json
        with open(args.batch, "r", encoding="utf-8") as f:
            segments = json.load(f)
        print(f"[cosyvoice] Batch mode: {len(segments)} segments, voice={args.voice}", flush=True)
        results = synthesize_batch(segments, args.voice, verbose=args.verbose)
        ok_count = sum(1 for r in results if r["ok"])
        print(f"[cosyvoice] Batch complete: {ok_count}/{len(segments)} succeeded")
        if ok_count != len(segments):
            failed = [r for r in results if not r["ok"]]
            for r in failed:
                print(f"[cosyvoice] Failed: {r['output']} - {r['error']}")
            sys.exit(1)
    elif args.text and args.output:
        # Single mode
        result = synthesize_cosyvoice(args.text, args.voice, args.output, verbose=args.verbose)
        print(f"[cosyvoice] Saved: {result}")
    else:
        parser.error("Either --batch or (--text + --output) is required")


if __name__ == "__main__":
    main()
