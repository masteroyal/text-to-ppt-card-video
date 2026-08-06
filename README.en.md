# Text-to-PPT-Card-Video

[English](README.en.md) | [简体中文](README.md)

Turn text into narrated PPT-card videos. Write a `manifest.json` describing pages, narration, and element animation, then let the scripts produce a single-file HTML deck. The same manifest can later be exported as an MP4.

## Getting started

Requirements: Python 3.10+, Node.js 22.12+, FFmpeg on PATH. Puppeteer downloads Chrome on the first `npm install`.

```bash
git clone https://github.com/masteroyal/text-to-ppt-card-video.git
cd text-to-ppt-card-video
cd scripts && npm install && cd ..
pip install -r scripts/requirements.txt
```

The default Edge TTS flow needs no submodules. For CosyVoice or MOSS-TTS-Nano, run `git submodule update --init --recursive` and install the model dependencies from `requirements-optional.txt`.

Put a `manifest.json` in your output directory and run:

```bash
python scripts/gen_draft.py ./output
python scripts/build.py ./output
```

`final.html` now contains everything needed to play the deck. The default TTS engine is Edge TTS and works online; MOSS-TTS-Nano and CosyVoice need local models, and DashScope needs an API key. Optional engine dependencies live in `scripts/requirements-optional.txt`.

For video:

```bash
python scripts/split_pages.py ./output
node scripts/record_video.js ./output/pages ./output/video.mp4
```

The default resolution is 1080x1920; pass a size matching the card ratio (for example `1080 1440` for 3:4) to keep the card un-stretched.

## Further reading

- Sample manifest: `examples/sample_manifest.json`
- Field reference and narration guide: `SKILL.md`
- Theme palettes: `themes.md`
- Third-party notices: `NOTICE`
- License: `LICENSE`
