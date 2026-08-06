# Text-to-PPT-Card-Video

[English](README.en.md) | [简体中文](README.md)

这个项目把一段文本变成带旁白的 PPT 卡片视频。你只需要写一份 `manifest.json`，说明每页的内容、旁白和动画顺序，剩下的合成工作由脚本完成。默认产物是单文件 `final.html`，样式、脚本和音频都嵌在文件里，浏览器打开就能播。

## 怎么用

先装环境：Python 3.10+、Node.js 22.12+，以及能在 PATH 里找到的 FFmpeg。Puppeteer 会在第一次 `npm install` 时自动下载 Chrome。

```bash
git clone https://github.com/masteroyal/text-to-ppt-card-video.git
cd text-to-ppt-card-video
cd scripts && npm install && cd ..
pip install -r scripts/requirements.txt
```

默认用 Edge TTS，不需要子模块。要用 CosyVoice 或 MOSS-TTS-Nano 时，再执行 `git submodule update --init --recursive` 并按 `requirements-optional.txt` 安装模型依赖。

在输出目录写好 `manifest.json`，然后跑：

```bash
python scripts/gen_draft.py ./output
python scripts/build.py ./output
```

这两步生成 `final.html`。`build.py` 会按 manifest 里的 `tts_engine` 合成旁白，并把音频和时间轴写进 HTML。默认引擎是 Edge TTS，联网即可使用。

要视频成片时，再执行：

```bash
python scripts/split_pages.py ./output
node scripts/record_video.js ./output/pages ./output/video.mp4
```

默认分辨率是 1080×1920。如果卡片是 3:4，建议传 `1080 1440`，画面不会被拉伸。

## 更多信息

- manifest 完整示例：[examples/sample_manifest.json](examples/sample_manifest.json)
- 字段说明、旁白写法和生成步骤：[SKILL.md](SKILL.md)
- 12 套主题的配色与适用场景：[themes.md](themes.md)
- 第三方组件声明：[NOTICE](NOTICE)
- 许可证：[LICENSE](LICENSE)
