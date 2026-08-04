# Text-to-PPT-Card-Video

[English](README.en.md) | [简体中文](README.md)

这个项目根据 `manifest.json` 生成带旁白和动画的 PPT 卡片演示。默认产物是单文件 HTML，样式、脚本和音频全部内嵌，浏览器打开即可播放；需要视频时再通过 Puppeteer 和 FFmpeg 导出 MP4。

页面可配置 TTS 旁白，元素按音频时间轴逐个出现。仓库根目录的 `SKILL.md` 面向支持自定义 skill 的工具；普通命令行使用按下方“快速开始”运行即可。

## 功能

- 12 套 lieflat 风格主题，覆盖咨询报告、杂志、极客、终端等场景
- 4 种 TTS 引擎：Edge TTS、MOSS-TTS-Nano、CosyVoice、DashScope
- 旁白与元素动画按音频时间轴对齐
- 单文件 HTML 输出，不需要外置资源
- 可选 MP4 导出，支持自定义分辨率

## 工作流程

manifest.json 定义页面内容、旁白和元素绑定，gen_draft.py 根据它生成带占位符的 HTML 模板：

```text
manifest.json
      |
      v
gen_draft.py -> draft.html
      |
      v
build.py -> final.html（内嵌音频和时间轴）
      |
      v
split_pages.py -> page_N.html
      |
      v
record_video.js -> output.mp4
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 22.12+
- FFmpeg（需要在 PATH 中）
- Chrome/Chromium（首次执行 `npm install` 时由 Puppeteer 自动下载）

### 安装

```bash
git clone --recursive https://github.com/masteroyal/text-to-ppt-card-video.git
cd text-to-ppt-card-video

cd scripts && npm install && cd ..
pip install -r scripts/requirements.txt
```

本地 TTS 是可选功能。MOSS-TTS-Nano 和 CosyVoice 需要额外下载模型，Edge TTS 联网即可使用：

```bash
pip install -r scripts/requirements-optional.txt
```

### 使用

先在输出目录准备好 `manifest.json`，然后按顺序执行：

```bash
python scripts/gen_draft.py ./output
python scripts/build.py ./output
python scripts/split_pages.py ./output
node scripts/record_video.js ./output/pages ./output/video.mp4
```

前两步只用来生成 HTML。跑完 `build.py` 后，`final.html` 就是完整产物；后两步是视频导出。

TTS 引擎在 manifest.json 里配置：

```json
{
  "tts_engine": "edge",
  "voice": "YunxiNeural"
}
```

可选值：`edge`（默认）、`moss`、`cosyvoice`、`dashscope`。DashScope 需要安装 `dashscope` 并设置 `DASHSCOPE_API_KEY`，也可以在 manifest.json 里直接写 `api_key` 字段。

视频分辨率默认是 1080×1920，也可以按卡片比例传参：

```bash
node scripts/record_video.js ./output/pages ./output/video.mp4 1080 1440
```

如果输出宽高比和卡片不一致，视频会等比缩放并用黑边补齐，不会拉伸卡片。

## 输入格式

manifest.json 的完整示例见 [examples/sample_manifest.json](examples/sample_manifest.json)。字段说明和旁白写法在 [SKILL.md](SKILL.md) 里。

## 主题

12 套主题的样式和说明见 [themes.md](themes.md)。

## 目录结构

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

## 致谢

- HTML 设计模板来自 [lieflat-html-design](https://github.com/larashero3-dotcom/lieflat-html-design)（MIT）
- TTS 引擎：[CosyVoice](https://github.com/FunAudioLLM/CosyVoice)、[MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano)、[Edge TTS](https://github.com/rany2/edge-tts)
- 视频录制：[Puppeteer](https://github.com/puppeteer/puppeteer)

第三方组件的完整声明见 [NOTICE](NOTICE)。

## 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
