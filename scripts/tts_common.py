#!/usr/bin/env python3
"""Shared TTS settings and executable lookup used by the build scripts."""

import os
import shutil

VALID_VOICES = {
    "XiaoxiaoNeural": "zh-CN female, warm",
    "XiaoyiNeural": "zh-CN female, lively",
    "YunjianNeural": "zh-CN male, grand",
    "YunxiNeural": "zh-CN male, professional",
    "YunxiaNeural": "zh-CN male, young",
    "YunyangNeural": "zh-CN male, news anchor",
    "liaoning-XiaobeiNeural": "zh-CN female, northeastern",
    "shaanxi-XiaoniNeural": "zh-CN female, central plains",
}
DEFAULT_VOICE = "YunxiNeural"

MOSS_VOICES = {
    "Junhao":  "zh male, professional",
    "Zhiming": "zh male, warm",
    "Weiguo":  "zh male, steady",
    "Xiaoyu":  "zh female, gentle",
    "Yuewen":  "zh female, clear",
    "Lingyu":  "zh female, lively",
}
MOSS_DEFAULT_VOICE = "Junhao"

COSYVOICE_VOICES = {
    "中文女":  "zh female, standard",
    "中文男":  "zh male, standard",
    "英文女":  "en female, standard",
    "英文男":  "en male, standard",
}
COSYVOICE_DEFAULT_VOICE = "中文女"

DASHSCOPE_VOICES = {
    "longanhuan":         "zh female, energetic lively 20-30",
    "longanhuan_v3":      "zh female, energetic lively v3 (dialects)",
    "longanyang":         "zh male, sunny warm 20-30",
    "longjiaxin_v3":      "zh female, elegant cantonese",
    "longjiayi_v3":       "zh female, intellectual cantonese",
    "longanmin_v3":       "zh female, cute loli minnan",
    "longanyue_v3":       "zh male, lively cantonese",
    "longlaotie_v3":      "zh male, straightforward northeast",
    "longshange_v3":      "zh male, shaanxi dialect",
    "longhuhu_v3":        "zh female, child 6-10 lively",
    "longxian_v3":        "zh female, child 12 bold cute",
    "longling_v3":        "zh female, child 10 naive",
    "longpaopao_v3":      "zh neutral, child bubble voice",
    "longshanshan_v3":    "zh neutral, child dramatic",
    "longjielidou_v3":    "zh male, child 10 playful",
    "longniuniu_v3":      "zh male, child sunny boy",
}
DASHSCOPE_DEFAULT_VOICE = "longanhuan"
DASHSCOPE_DEFAULT_MODEL = "cosyvoice-v3-flash"

SUPPORTED_TTS_ENGINES = ("edge", "moss", "cosyvoice", "dashscope")


def find_bin(name):
    """Return an executable path from PATH or the WinGet FFmpeg install."""
    found = shutil.which(name)
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA", "")
    if not local:
        return None
    import glob
    for ext in (".exe", ".EXE"):
        pattern = os.path.join(
            local, "Microsoft", "WinGet", "Packages", "*FFmpeg*", "bin", name + ext
        )
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None


def find_cosyvoice_python():
    """Return the Python command for the cosyvoice env, or None when unknown."""
    configured = os.environ.get("COSYVOICE_PYTHON")
    if configured:
        return configured

    user_home = os.environ.get("USERPROFILE", "")
    program_data = os.environ.get("ProgramData", "")
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(user_home, "miniconda3", "envs", "cosyvoice", "python.exe"),
        os.path.join(user_home, "anaconda3", "envs", "cosyvoice", "python.exe"),
        os.path.join(user_home, "miniforge3", "envs", "cosyvoice", "python.exe"),
        os.path.join(program_data, "miniconda3", "envs", "cosyvoice", "python.exe"),
        os.path.join(program_data, "anaconda3", "envs", "cosyvoice", "python.exe"),
        os.path.join(home, "miniconda3", "envs", "cosyvoice", "bin", "python"),
        os.path.join(home, "anaconda3", "envs", "cosyvoice", "bin", "python"),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate

    conda = shutil.which("conda")
    if conda:
        return [conda, "run", "-n", "cosyvoice", "python"]
    return None
