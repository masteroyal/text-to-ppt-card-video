# Text-to-PPT-Card-Video

[English](README.en.md) | [简体中文](README.md)

Text-to-PPT-Card-Video turns a `manifest.json` into PPT-card style presentations with narration and animation. The default output is a single-file HTML with styles, scripts, and audio embedded, so it can be played directly in a browser. MP4 export is optional and uses Puppeteer plus FFmpeg.

Pages can include TTS narration, and elements appear one by one along the audio timeline. `SKILL.md` at the repository root is for tools that support custom skills; command-line users can follow Quick Start below.

## Features

- 12 lieflat-style themes covering consulting reports, magazines, geek, terminal, and other scenarios
- 4 TTS engines: Edge TTS, MOSS-TTS-Nano, CosyVoice, DashScope
- Narration and element animations aligned to the audio timeline
- Single-file HTML output with no external assets
- Optional MP4 export with custom resolution

## Workflow

`manifest.json` defines page content, narration, and element bindings. `gen_draft.py` turns it into an HTML template with placeholders:

```text
manifest.json
      |
      v
gen_draft.py -> draft.html
      |
      v
build.py -> final.html (audio and timeline embedded)
      |
      v
split_pages.py -> page_N.html
      |
      v
record_video.js -> output.mp4
```

## Quick Start

### Requirements

- Python 3.10+
- Node.js 22.12+
- FFmpeg (must be available on PATH)
- Chrome/Chromium (Puppeteer downloads it automatically on the first `npm install`)

### Install

```bash
git clone --recursive https://github.com/masteroyal/text-to-ppt-card-video.git
cd text-to-ppt-card-video

cd scripts && npm install && cd ..
pip install -r scripts/requirements.txt
```

Local TTS is optional. MOSS-TTS-Nano and CosyVoice require additional model downloads; Edge TTS works with a network connection:

```bash
pip install -r scripts/requirements-optional.txt
```

### Use

Prepare `manifest.json` in the output directory, then run the pipeline in order:

```bash
python scripts/gen_draft.py ./output
python scripts/build.py ./output
python scripts/split_pages.py ./output
node scripts/record_video.js ./output/pages ./output/video.mp4
```

The first two steps only generate HTML. After `build.py`, `final.html` is the complete artifact; the last two steps export video.

Configure the TTS engine in `manifest.json`:

```json
{
  "tts_engine": "edge",
  "voice": "YunxiNeural"
}
```

Supported values are `edge` (default), `moss`, `cosyvoice`, and `dashscope`. DashScope requires the `dashscope` package and a `DASHSCOPE_API_KEY` environment variable, or an `api_key` field directly in `manifest.json`.

The default video resolution is 1080x1920. You can pass a different size that matches the card aspect ratio:

```bash
node scripts/record_video.js ./output/pages ./output/video.mp4 1080 1440
```

If the output aspect ratio differs from the card, the video is scaled to fit with black bars instead of stretching the card.

## Input format

See [examples/sample_manifest.json](examples/sample_manifest.json) for a complete `manifest.json` example. Field descriptions and narration syntax are in [SKILL.md](SKILL.md).

## Themes

Styles and descriptions for the 12 themes are in [themes.md](themes.md).

## Directory structure

```text
text-to-ppt-card-video/
├── SKILL.md
├── themes.md
├── LICENSE
├── NOTICE
├── CHANGELOG.md
├── README.en.md
├── scripts/
│   ├── build.py
│   ├── gen_draft.py
│   ├── split_pages.py
│   ├── record_video.js
│   ├── setup_local_tts.py
│   ├── themes.py
│   ├── tts_common.py
│   ├── moss_tts_engine.py
│   ├── cosyvoice_engine.py
│   ├── check.py
│   ├── requirements.txt
│   ├── requirements-optional.txt
│   ├── package.json
│   ├── cosyvoice/       # submodule: FunAudioLLM/CosyVoice
│   └── moss-tts-nano/   # submodule: OpenMOSS/MOSS-TTS-Nano
├── examples/
└── .github/workflows/
```

## Acknowledgments

- HTML design templates from [lieflat-html-design](https://github.com/larashero3-dotcom/lieflat-html-design) (MIT)
- TTS engines: [CosyVoice](https://github.com/FunAudioLLM/CosyVoice), [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano), [Edge TTS](https://github.com/rany2/edge-tts)
- Video recording: [Puppeteer](https://github.com/puppeteer/puppeteer)

Third-party notices are listed in [NOTICE](NOTICE).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
