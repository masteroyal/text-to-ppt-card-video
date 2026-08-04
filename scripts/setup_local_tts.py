#!/usr/bin/env python3
"""
setup_local_tts.py - Check and prepare local TTS engines.

Usage:
    python setup_local_tts.py --check
    python setup_local_tts.py --engine moss
    python setup_local_tts.py --engine cosyvoice
    python setup_local_tts.py --engine all

MOSS-TTS-Nano downloads its ONNX models on first inference automatically.
This script pre-downloads them with huggingface_hub when they are missing.
CosyVoice-300M-SFT is downloaded with the modelscope SDK.
"""

import argparse
import os
import sys

from tts_common import find_bin, find_cosyvoice_python

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))

MOSS_DIR = os.path.join(SKILL_DIR, "moss-tts-nano")
MOSS_INFER = os.path.join(MOSS_DIR, "infer_onnx.py")
MOSS_MODELS_DIR = os.path.join(MOSS_DIR, "models")
MOSS_MODEL_DIRS = [
    "MOSS-TTS-Nano-100M-ONNX",
    "MOSS-Audio-Tokenizer-Nano-ONNX",
]
MOSS_REPOS = [
    "OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX",
    "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX",
]

COSYVOICE_DIR = os.path.join(SKILL_DIR, "cosyvoice")
COSYVOICE_MODEL_DIR = os.path.join(COSYVOICE_DIR, "pretrained_models", "CosyVoice-300M-SFT")
COSYVOICE_MODEL_FILES = [
    "flow.pt",
    "llm.pt",
    "hift.pt",
    "campplus.onnx",
    "speech_tokenizer_v1.onnx",
]
COSYVOICE_REPO = "iic/CosyVoice-300M-SFT"


def check_moss():
    issues = []
    if not os.path.isfile(MOSS_INFER):
        issues.append(
            f"MOSS submodule missing: {MOSS_DIR} "
            "(run `git submodule update --init --recursive` first)"
        )
    else:
        for name in MOSS_MODEL_DIRS:
            if not os.path.isdir(os.path.join(MOSS_MODELS_DIR, name)):
                issues.append(f"MOSS model missing: {os.path.join(MOSS_MODELS_DIR, name)}")
    return issues


def check_cosyvoice():
    issues = []
    if not os.path.isdir(os.path.join(COSYVOICE_DIR, "cosyvoice")):
        issues.append(
            f"CosyVoice submodule missing: {COSYVOICE_DIR} "
            "(run `git submodule update --init --recursive` first)"
        )
    if not os.path.isdir(COSYVOICE_MODEL_DIR):
        issues.append(f"CosyVoice model dir missing: {COSYVOICE_MODEL_DIR}")
    else:
        missing = [
            name
            for name in COSYVOICE_MODEL_FILES
            if not os.path.isfile(os.path.join(COSYVOICE_MODEL_DIR, name))
        ]
        if missing:
            issues.append("CosyVoice model files missing: " + ", ".join(missing))
    if not find_cosyvoice_python():
        issues.append(
            "CosyVoice conda python not found; "
            "set COSYVOICE_PYTHON or create the `cosyvoice` conda env"
        )
    return issues


def run_check():
    print("[setup] Python:", sys.version.split()[0])
    print("[setup] FFmpeg:", find_bin("ffmpeg") or "NOT FOUND")
    ok = True
    for engine, checker in (("moss", check_moss), ("cosyvoice", check_cosyvoice)):
        print(f"\n[{engine}]")
        issues = checker()
        if not issues:
            print("  READY")
        else:
            ok = False
            for msg in issues:
                print("  MISSING: " + msg)
    print("\nResult:", "READY" if ok else "NEEDS SETUP (see messages above)")
    return 0 if ok else 1


def download_moss():
    if not os.path.isfile(MOSS_INFER):
        print("ERROR: MOSS submodule missing. Run `git submodule update --init --recursive` first.")
        return 1
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("MOSS models are missing. Install huggingface_hub, then run this command again:")
        print("  pip install -U huggingface_hub")
        print("  python setup_local_tts.py --engine moss")
        return 1
    os.makedirs(MOSS_MODELS_DIR, exist_ok=True)
    for repo in MOSS_REPOS:
        print("Downloading", repo, "...")
        snapshot_download(repo, local_dir=os.path.join(MOSS_MODELS_DIR, repo.split("/")[-1]))
    return 0


def download_cosyvoice():
    if not os.path.isdir(COSYVOICE_DIR):
        print("ERROR: CosyVoice submodule missing. Run `git submodule update --init --recursive` first.")
        return 1
    try:
        from modelscope import snapshot_download
    except ImportError:
        print("CosyVoice model is missing. Install modelscope, then run this command again:")
        print("  pip install -U modelscope")
        print("  python setup_local_tts.py --engine cosyvoice")
        return 1
    os.makedirs(os.path.dirname(COSYVOICE_MODEL_DIR), exist_ok=True)
    print("Downloading", COSYVOICE_REPO, "->", COSYVOICE_MODEL_DIR)
    snapshot_download(COSYVOICE_REPO, local_dir=COSYVOICE_MODEL_DIR)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Check/prepare local TTS engines for text-to-ppt-card-video.")
    parser.add_argument("--check", action="store_true", help="Report environment and model status")
    parser.add_argument(
        "--engine",
        choices=["moss", "cosyvoice", "all"],
        help="Prepare a specific local engine (default: all)",
    )
    args = parser.parse_args()

    if args.check:
        return run_check()

    engines = ["moss", "cosyvoice"] if args.engine in (None, "all") else [args.engine]
    rc = 0
    for engine in engines:
        checker = check_moss if engine == "moss" else check_cosyvoice
        issues = checker()
        if not issues:
            print(f"[{engine}] READY")
            continue
        print(f"[{engine}] missing components; preparing...")
        rc |= download_moss() if engine == "moss" else download_cosyvoice()
        after = checker()
        if after:
            rc = 1
            print(f"[{engine}] STILL MISSING: " + "; ".join(after))
        else:
            print(f"[{engine}] READY")
    return rc


if __name__ == "__main__":
    sys.exit(main())
