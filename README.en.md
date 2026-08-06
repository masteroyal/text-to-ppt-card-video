# Text-to-PPT-Card-Video

[English](README.en.md) | [简体中文](README.md)

Generate narrated PPT-card decks from a single `manifest.json`. The default output is a self-contained `final.html`; page splitting and MP4 export are available when you need a video.

## Features

- 12 themes selected with the `theme` field
- 4 TTS engines: Edge TTS, MOSS-TTS-Nano, CosyVoice, DashScope
- Narration segments drive element animations on an audio timeline
- Self-contained HTML output
- Optional MP4 export

## Requirements

- Python 3.10+
- Node.js 22.12+
- FFmpeg on PATH
- Puppeteer downloads Chrome during `npm install`

## Installation

```bash
git clone https://github.com/masteroyal/text-to-ppt-card-video.git
cd text-to-ppt-card-video
cd scripts && npm install && cd ..
pip install -r scripts/requirements.txt
```

The default Edge TTS flow needs no submodules. For CosyVoice or MOSS-TTS-Nano, run:

```bash
git submodule update --init --recursive
pip install -r scripts/requirements-optional.txt
```

## Usage

Put a `manifest.json` in your output directory:

```bash
python scripts/gen_draft.py ./output
python scripts/build.py ./output
```

Open `./output/final.html` to play the deck. To export an MP4:

```bash
python scripts/split_pages.py ./output
node scripts/record_video.js ./output/pages ./output/video.mp4
```

The default resolution is 1080x1920. For a 3:4 card, pass `1080 1440` to avoid stretching.

## Documentation

- [Manifest and usage guide](docs/usage.md)
- [Sample manifest](examples/sample_manifest.json)
- [Theme CSS reference](themes.md)
- [Changelog](CHANGELOG.md)

## Testing

```bash
python scripts/check.py
```

## Acknowledgements

- Theme CSS and card layouts are adapted from [lieflat-html-design](https://github.com/larashero3-dotcom/lieflat-html-design) (MIT)
- TTS engines: [CosyVoice](https://github.com/FunAudioLLM/CosyVoice), [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano), [Edge TTS](https://github.com/rany2/edge-tts)
- Video recording: [Puppeteer](https://github.com/puppeteer/puppeteer)

See [NOTICE](NOTICE) for third-party notices and [LICENSE](LICENSE) for the project license.
