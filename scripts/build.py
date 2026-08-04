#!/usr/bin/env python3
"""
text-to-ppt-card-video build.py
======================
Reads manifest.json → generates Edge TTS audio per narration segment
→ calculates precise timeline → injects base64 audio + timeline into HTML.

Usage:
    python build.py <output_dir>

Input files (in output_dir):
    manifest.json   — page content + narration scripts + element bindings
    draft.html      — HTML with __AUDIO_N__ / __TIMELINE__ placeholders

Output files (in output_dir):
    final.html      — complete self-contained HTML with embedded audio

Requirements:
    pip install edge-tts
    winget install Gyan.FFmpeg   (or ensure ffmpeg/ffprobe on PATH)
"""

import asyncio
import base64
import json
import os
import re
import shutil
import subprocess
import sys

from tts_common import (
    COSYVOICE_DEFAULT_VOICE,
    COSYVOICE_VOICES,
    DASHSCOPE_DEFAULT_MODEL,
    DASHSCOPE_DEFAULT_VOICE,
    DASHSCOPE_VOICES,
    DEFAULT_VOICE,
    MOSS_DEFAULT_VOICE,
    MOSS_VOICES,
    SUPPORTED_TTS_ENGINES,
    VALID_VOICES,
    find_bin,
    find_cosyvoice_python,
)

# ── Segment gap (silence between narration segments) ────────────────
SEGMENT_GAP = 0.6  # seconds


def log(msg):
    print(f"[text-to-ppt-card-video] {msg}", flush=True)


FFMPEG = find_bin("ffmpeg") or "ffmpeg"
FFPROBE = find_bin("ffprobe") or "ffprobe"
CONDA_PYTHON = find_cosyvoice_python() or "python"


# ── TTS generation ──────────────────────────────────────────────────

async def generate_tts(text, voice, output_path, rate="+0%", pitch="+0Hz"):
    """Generate TTS audio for a single segment."""
    import edge_tts
    communicate = edge_tts.Communicate(text, f"zh-CN-{voice}", rate=rate, pitch=pitch)
    await communicate.save(output_path)


async def generate_all_segments(pages, voice, tmp_dir, rate="+0%", pitch="+0Hz", tts_engine="edge"):
    """Generate TTS for all segments across all pages. Returns list of paths."""
    if tts_engine == "moss":
        return _generate_all_segments_moss(pages, voice, tmp_dir)
    if tts_engine == "cosyvoice":
        return _generate_all_segments_cosyvoice(pages, voice, tmp_dir)
    if tts_engine == "dashscope":
        return _generate_all_segments_dashscope(pages, voice, tmp_dir, rate=rate, pitch=pitch)

    tasks = []
    paths = []
    for pi, page in enumerate(pages):
        page_paths = []
        for ni, seg in enumerate(page.get("narration", [])):
            out = os.path.join(tmp_dir, f"seg_{pi}_{ni}.mp3")
            page_paths.append(out)
            tasks.append(generate_tts(seg["text"], voice, out, rate=rate, pitch=pitch))
        paths.append(page_paths)

    total = sum(len(p) for p in paths)
    log(f"Generating {total} TTS segments with engine=edge voice={voice} ...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    failed = 0
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            failed += 1
            log(f"WARNING: TTS segment failed: {r}")
    if failed:
        log(f"WARNING: {failed}/{total} TTS segments failed")
    log(f"TTS generation complete.")
    return paths


def _generate_all_segments_moss(pages, voice, tmp_dir):
    """Generate TTS for all segments using MOSS-TTS-Nano (sequential, not async)."""
    from moss_tts_engine import synthesize_moss

    paths = []
    total = sum(len(page.get("narration", [])) for page in pages)
    log(f"Generating {total} TTS segments with engine=moss voice={voice} ...")
    done = 0
    for pi, page in enumerate(pages):
        page_paths = []
        for ni, seg in enumerate(page.get("narration", [])):
            out = os.path.join(tmp_dir, f"seg_{pi}_{ni}.mp3")
            try:
                synthesize_moss(seg["text"], voice, out)
                done += 1
                log(f"  [{done}/{total}] page {pi} seg {ni}: {seg['text'][:20]}...")
            except Exception as e:
                log(f"WARNING: MOSS segment failed: {e}")
            page_paths.append(out)
        paths.append(page_paths)

    log(f"MOSS-TTS generation complete ({done}/{total} succeeded).")
    return paths


def _generate_all_segments_cosyvoice(pages, voice, tmp_dir):
    """Generate TTS for all segments using CosyVoice (batch mode, single subprocess)."""
    engine_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cosyvoice_engine.py")

    # Collect all segments into a batch list
    batch_items = []
    segment_map = []  # track (page_idx, seg_idx) for logging
    for pi, page in enumerate(pages):
        for ni, seg in enumerate(page.get("narration", [])):
            out = os.path.join(tmp_dir, f"seg_{pi}_{ni}.mp3")
            batch_items.append({"text": seg["text"], "output": out})
            segment_map.append((pi, ni))

    total = len(batch_items)
    log(f"Generating {total} TTS segments with engine=cosyvoice voice={voice} (batch mode) ...")

    # Write batch JSON
    batch_json = os.path.join(tmp_dir, "batch_segments.json")
    with open(batch_json, "w", encoding="utf-8") as f:
        json.dump(batch_items, f, ensure_ascii=False, indent=2)

    # Single conda subprocess for all segments
    python_cmd = CONDA_PYTHON
    if isinstance(python_cmd, list):
        cmd = list(python_cmd) + [
            engine_script, "--batch", batch_json, "--voice", voice
        ]
    else:
        cmd = [
            python_cmd, engine_script,
            "--batch", batch_json,
            "--voice", voice,
        ]
    log(f"Calling: {' '.join(cmd[:4])} ...")
    log("(CosyVoice output suppressed; progress tracked by file creation)")

    # IMPORTANT: Both stdout and stderr must go to DEVNULL.
    # On Windows the pipe buffer is only 4KB. CosyVoice writes tqdm progress
    # bars with \r (no newline), which fills the pipe and deadlocks the child.
    child_env = os.environ.copy()
    child_env["TQDM_DISABLE"] = "1"
    child_env["PYTHONUTF8"] = "1"  # Force UTF-8 mode for Chinese voice names on Windows

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=3600,
        env=child_env,
    )

    if result.returncode != 0:
        raise RuntimeError(f"CosyVoice batch exited with code {result.returncode}")

    # Build paths array matching expected structure
    paths = []
    for pi, page in enumerate(pages):
        page_paths = []
        for ni in range(len(page.get("narration", []))):
            page_paths.append(os.path.join(tmp_dir, f"seg_{pi}_{ni}.mp3"))
        paths.append(page_paths)

    succeeded = sum(1 for pp in paths for p in pp if os.path.exists(p))
    log(f"CosyVoice generation complete ({succeeded}/{total} files exist).")
    return paths


# ── DashScope CosyVoice API TTS ─────────────────────────────────────

def _dashscope_tts_single(text, voice, output_path, api_key, model):
    """Call DashScope CosyVoice API via Python SDK to synthesize a single segment."""
    import dashscope
    from dashscope.audio.tts_v2 import SpeechSynthesizer

    dashscope.api_key = api_key
    synthesizer = SpeechSynthesizer(model=model, voice=voice)
    audio_data = synthesizer.call(text)

    if not audio_data or len(audio_data) < 100:
        raise RuntimeError(f"DashScope returned no audio (size={len(audio_data) if audio_data else 0})")

    with open(output_path, "wb") as f:
        f.write(audio_data)


def _generate_all_segments_dashscope(pages, voice, tmp_dir, rate="+0%", pitch="+0Hz", api_key=None, model=None):
    """Generate TTS for all segments using DashScope CosyVoice API (sequential)."""
    if api_key is None:
        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY not set. Set it via environment variable or manifest.json 'api_key' field.")
    if model is None:
        model = DASHSCOPE_DEFAULT_MODEL

    paths = []
    total = sum(len(page.get("narration", [])) for page in pages)
    log(f"Generating {total} TTS segments with engine=dashscope model={model} voice={voice} ...")

    done = 0
    for pi, page in enumerate(pages):
        page_paths = []
        for ni, seg in enumerate(page.get("narration", [])):
            out = os.path.join(tmp_dir, f"seg_{pi}_{ni}.mp3")
            try:
                _dashscope_tts_single(seg["text"], voice, out, api_key, model)
                done += 1
                log(f"  [{done}/{total}] page {pi} seg {ni}: {seg['text'][:20]}...")
            except Exception as e:
                log(f"WARNING: DashScope segment failed: {e}")
            page_paths.append(out)
            # Small delay to avoid rate limiting
            import time
            time.sleep(0.3)
        paths.append(page_paths)

    log(f"DashScope TTS generation complete ({done}/{total} succeeded).")
    return paths


# ── Audio duration ──────────────────────────────────────────────────

def get_duration(path):
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        [FFPROBE, "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, encoding="utf-8"
    )
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        # Fallback: estimate from file size (~24KB/s for 192kbps MP3)
        size = os.path.getsize(path)
        return size / 24000.0


# ── Generate silence ────────────────────────────────────────────────

def generate_silence(duration, output_path, sample_rate=24000):
    """Generate silent MP3 using ffmpeg."""
    result = subprocess.run(
        [FFMPEG, "-y", "-f", "lavfi", "-i",
         f"anullsrc=r={sample_rate}:cl=mono",
         "-t", str(duration),
         "-ar", str(sample_rate), "-ac", "1",
         "-c:a", "libmp3lame", "-b:a", "192k",
         output_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        log(f"ffmpeg silence error: {result.stderr[-500:]}")
        raise subprocess.CalledProcessError(result.returncode, result.args)


# ── Concatenate page audio ──────────────────────────────────────────

def concat_page_audio(segment_paths, gap_duration, page_idx, tmp_dir):
    """
    Concatenate segment MP3s with silence gaps between them.
    Returns (combined_mp3_path, segment_timings).
    """
    if not segment_paths:
        return None, []

    # Build concat list with alternating audio + gap
    concat_list = os.path.join(tmp_dir, f"concat_{page_idx}.txt")
    gap_mp3 = os.path.join(tmp_dir, f"gap_{page_idx}.mp3")
    generate_silence(gap_duration, gap_mp3)

    with open(concat_list, "w", encoding="utf-8") as f:
        for i, seg_path in enumerate(segment_paths):
            f.write(f"file '{os.path.abspath(seg_path).replace(chr(92), '/')}'\n")
            if i < len(segment_paths) - 1:
                f.write(f"file '{os.path.abspath(gap_mp3).replace(chr(92), '/')}'\n")

    combined = os.path.join(tmp_dir, f"page_{page_idx}.mp3")

    result = subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-c:a", "libmp3lame", "-b:a", "192k", combined],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        log(f"ffmpeg concat error: {result.stderr[-500:]}")
        raise subprocess.CalledProcessError(result.returncode, result.args)

    # Calculate segment start times from actual durations
    segment_timings = []
    current_time = 0.0
    for seg_path in segment_paths:
        dur = get_duration(seg_path)
        segment_timings.append({"start": round(current_time, 3), "duration": round(dur, 3)})
        current_time += dur + gap_duration

    return combined, segment_timings


# ── Base64 encode ───────────────────────────────────────────────────

def audio_to_base64(path):
    """Read audio file and return base64 data URI string."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:audio/mp3;base64,{data}"


# ── Process all pages ───────────────────────────────────────────────

def process_pages(pages, voice, tmp_dir, rate="+0%", pitch="+0Hz", tts_engine="edge"):
    """Generate audio + timeline for all pages."""
    timeline = {"pages": []}

    # Step 1: Generate all TTS segments
    seg_paths = asyncio.run(generate_all_segments(pages, voice, tmp_dir, rate=rate, pitch=pitch, tts_engine=tts_engine))

    # Step 2: Concatenate per page and build timeline
    for pi, page in enumerate(pages):
        log(f"Processing page {pi}/{len(pages)-1}: {page.get('title', '')[:30]}")
        narration = page.get("narration", [])
        page_seg_paths = seg_paths[pi]

        if not narration:
            timeline["pages"].append({
                "audio_base64": "",
                "duration": 0,
                "segments": []
            })
            continue

        # Fail fast when a TTS segment produced no audio; ffmpeg concat would
        # otherwise crash later with a confusing "file not found" error.
        missing = [os.path.basename(p) for p in page_seg_paths if not os.path.isfile(p)]
        if missing:
            raise RuntimeError(
                "TTS generation produced no audio for segment(s): " + ", ".join(missing)
            )

        # Concatenate audio
        combined_path, seg_timings = concat_page_audio(
            page_seg_paths, SEGMENT_GAP, pi, tmp_dir
        )

        # Get total duration
        total_dur = get_duration(combined_path)

        # Build segment timeline
        segments = []
        for ni, seg in enumerate(narration):
            timing = seg_timings[ni]
            segments.append({
                "start": timing["start"],
                "end": round(timing["start"] + timing["duration"], 3),
                "elements": seg.get("elements", [])
            })

        # Base64 encode
        audio_b64 = audio_to_base64(combined_path)

        timeline["pages"].append({
            "audio_base64": audio_b64,
            "duration": round(total_dur, 3),
            "segments": segments
        })

    return timeline


# ── Inject into HTML ────────────────────────────────────────────────

def inject_into_html(html_path, timeline, output_path):
    """Replace __AUDIO_N__ and __TIMELINE__ placeholders in HTML."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Replace audio placeholders
    for i, page in enumerate(timeline["pages"]):
        placeholder = f"__AUDIO_{i}__"
        if placeholder in html:
            html = html.replace(placeholder, page["audio_base64"])

    # Replace timeline placeholder
    timeline_json = json.dumps(timeline, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("__TIMELINE__", timeline_json)

    # Replace page count placeholder
    html = html.replace("__PAGE_COUNT__", str(len(timeline["pages"])))

    # Check for unreplaced placeholders
    remaining = re.findall(r'__(AUDIO_\d+|TIMELINE|PAGE_COUNT)__', html)
    if remaining:
        raise RuntimeError(
            "Unreplaced placeholders found in draft.html: " + ", ".join(remaining[:5])
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    log(f"Final HTML written to: {output_path}")


# ── Main ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py <output_dir>")
        print("  output_dir must contain: manifest.json + draft.html")
        sys.exit(1)

    output_dir = sys.argv[1]
    manifest_path = os.path.join(output_dir, "manifest.json")
    html_path = os.path.join(output_dir, "draft.html")

    if not os.path.exists(manifest_path):
        log(f"ERROR: {manifest_path} not found")
        sys.exit(1)
    if not os.path.exists(html_path):
        log(f"ERROR: {html_path} not found")
        sys.exit(1)

    # Load manifest
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    pages = manifest.get("pages", [])
    voice = manifest.get("voice", DEFAULT_VOICE)
    title = manifest.get("title", "Presentation")
    rate = manifest.get("rate", "+0%")
    pitch = manifest.get("pitch", "+0Hz")
    tts_engine = manifest.get("tts_engine", "edge")

    if tts_engine not in SUPPORTED_TTS_ENGINES:
        log(f"ERROR: Unknown tts_engine '{tts_engine}'. "
            f"Supported engines: {', '.join(SUPPORTED_TTS_ENGINES)}")
        sys.exit(1)

    # Validate voice against engine
    if tts_engine == "moss":
        if voice not in MOSS_VOICES:
            log(f"WARNING: MOSS voice '{voice}' not in known list, using {MOSS_DEFAULT_VOICE}")
            voice = MOSS_DEFAULT_VOICE
    elif tts_engine == "cosyvoice":
        if voice not in COSYVOICE_VOICES:
            log(f"WARNING: CosyVoice '{voice}' not in known list, using {COSYVOICE_DEFAULT_VOICE}")
            voice = COSYVOICE_DEFAULT_VOICE
    elif tts_engine == "dashscope":
        if voice not in DASHSCOPE_VOICES:
            log(f"WARNING: DashScope voice '{voice}' not in known list, using {DASHSCOPE_DEFAULT_VOICE}")
            voice = DASHSCOPE_DEFAULT_VOICE
    else:
        if voice not in VALID_VOICES:
            log(f"WARNING: voice '{voice}' not in known list, using {DEFAULT_VOICE}")
            voice = DEFAULT_VOICE

    # DashScope API key setup
    dashscope_model = manifest.get("dashscope_model", DASHSCOPE_DEFAULT_MODEL)
    if tts_engine == "dashscope":
        api_key = manifest.get("api_key") or os.environ.get("DASHSCOPE_API_KEY", "")
        # Windows fallback: read from registry (setx stores it there)
        if not api_key and sys.platform == "win32":
            try:
                import winreg
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
                api_key, _ = winreg.QueryValueEx(reg_key, "DASHSCOPE_API_KEY")
                winreg.CloseKey(reg_key)
            except Exception:
                pass
        if not api_key:
            log("ERROR: DashScope API key required. Set DASHSCOPE_API_KEY env var or add 'api_key' to manifest.json")
            sys.exit(1)
        os.environ["DASHSCOPE_API_KEY"] = api_key
        log(f"DashScope model: {dashscope_model}")

    # Validate manifest structure
    if not pages:
        log("ERROR: manifest.json has no pages")
        sys.exit(1)
    for pi, page in enumerate(pages):
        if "type" not in page:
            log(f"ERROR: page {pi} missing 'type' field")
            sys.exit(1)
        for ni, seg in enumerate(page.get("narration", [])):
            if "text" not in seg:
                log(f"ERROR: page {pi} narration[{ni}] missing 'text'")
                sys.exit(1)
            if "elements" not in seg:
                log(f"WARNING: page {pi} narration[{ni}] missing 'elements'")

    log(f"=== text-to-ppt-card-video build ===")
    log(f"Title: {title}")
    log(f"Pages: {len(pages)}")
    log(f"TTS engine: {tts_engine}")
    log(f"Voice: {voice}")
    log(f"Rate: {rate}, Pitch: {pitch}")
    log(f"Segment gap: {SEGMENT_GAP}s")

    # Create temp directory for audio files
    tmp_dir = os.path.join(output_dir, ".build_temp")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        # Process all pages
        timeline = process_pages(pages, voice, tmp_dir, rate=rate, pitch=pitch, tts_engine=tts_engine)

        # Print summary
        log("---")
        for i, p in enumerate(timeline["pages"]):
            segs = len(p["segments"])
            dur = p["duration"]
            log(f"  Page {i}: {segs} segments, {dur:.1f}s audio")
        total_audio = sum(p["duration"] for p in timeline["pages"])
        log(f"  Total audio: {total_audio:.1f}s")

        # Inject into HTML
        final_path = os.path.join(output_dir, "final.html")
        inject_into_html(html_path, timeline, final_path)

        # Write timeline JSON for reference
        timeline_ref = {
            "pages": [
                {"duration": p["duration"], "segments": p["segments"]}
                for p in timeline["pages"]
            ]
        }
        with open(os.path.join(output_dir, "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(timeline_ref, f, ensure_ascii=False, indent=2)

        log(f"=== Build complete ===")
        log(f"Output: {final_path}")

    finally:
        # Clean up temp directory
        shutil.rmtree(tmp_dir, ignore_errors=True)
        log("Temp files cleaned up.")


if __name__ == "__main__":
    main()
