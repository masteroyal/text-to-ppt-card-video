# Text-to-PPT-Card-Video

[English](README.en.md) | [简体中文](README.md)

一份 `manifest.json` 生成带旁白的 PPT 卡片演示。默认产物是单文件 `final.html`，样式、脚本和音频都内嵌在文件里；需要视频时，可以再拆页并导出 MP4。

## 功能

- 12 套主题，按 `theme` 字段切换
- 4 种 TTS 引擎：Edge TTS、MOSS-TTS-Nano、CosyVoice、DashScope
- 旁白分段与页面元素动画按音频时间轴对齐
- 单文件 HTML 输出，可离线播放
- 可选导出 MP4

## 环境要求

- Python 3.10+
- Node.js 22.12+
- FFmpeg（在 PATH 中可用）
- Puppeteer 会在第一次 `npm install` 时下载 Chrome

## 安装

```bash
git clone https://github.com/masteroyal/text-to-ppt-card-video.git
cd text-to-ppt-card-video
cd scripts && npm install && cd ..
pip install -r scripts/requirements.txt
```

默认使用 Edge TTS，不需要子模块。使用 CosyVoice 或 MOSS-TTS-Nano 时，再执行：

```bash
git submodule update --init --recursive
pip install -r scripts/requirements-optional.txt
```

## 使用

在输出目录放好 `manifest.json`：

```bash
python scripts/gen_draft.py ./output
python scripts/build.py ./output
```

打开 `./output/final.html` 即可播放。生成 MP4 时：

```bash
python scripts/split_pages.py ./output
node scripts/record_video.js ./output/pages ./output/video.mp4
```

默认分辨率是 1080×1920。卡片是 3:4 时建议传 `1080 1440`，避免画面拉伸。

## 文档

- [manifest 与使用说明](docs/usage.md)
- [示例 manifest](examples/sample_manifest.json)
- [主题 CSS 参考](themes.md)
- [更新日志](CHANGELOG.md)

## 测试

```bash
python scripts/check.py
```

## 致谢

- 主题 CSS 和卡片布局参考 [lieflat-html-design](https://github.com/larashero3-dotcom/lieflat-html-design)（MIT）
- TTS 引擎：[CosyVoice](https://github.com/FunAudioLLM/CosyVoice)、[MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano)、[Edge TTS](https://github.com/rany2/edge-tts)
- 视频录制：[Puppeteer](https://github.com/puppeteer/puppeteer)

第三方组件声明见 [NOTICE](NOTICE)，许可证见 [LICENSE](LICENSE)。
