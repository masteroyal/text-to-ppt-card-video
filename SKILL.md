---
name: text-to-ppt-card-video
description: >-
  把文本变成带旁白和动画的 PPT 卡片演示，可输出单文件 HTML，也可导出 MP4。
  支持 12 套 lieflat 主题和 Edge TTS、MOSS-TTS-Nano、CosyVoice、DashScope
  四种 TTS 引擎。用户需要生成演示文稿、卡片视频或带旁白的 HTML 时使用。
version: 1.0.0
---

# text-to-ppt-card-video

这个 skill 根据 `manifest.json` 生成多页 PPT 卡片演示。默认产物是单文件 HTML，样式、脚本和 TTS 旁白全部内嵌；浏览器打开后会按旁白时间轴自动播放，每页元素随语音逐段出现。需要成片时，再用同一份内容导出 MP4。

## 产物说明

| 项目 | 说明 |
|------|------|
| 默认产物 | `final.html`，可复制为 `{project-name}.html` 直接交付 |
| 布局 | 横向滚动，每页占一个视口 |
| 卡片尺寸 | 由 manifest.json 的 `aspect_ratio` 决定，如 3:4 为 600×800 |
| 主题 | 12 套 lieflat 主题 |
| 音频 | TTS 旁白以 base64 内嵌 |
| 动画 | 按音频时间轴触发 |
| 导航 | 自动播放、播放按钮、键盘、圆点 |

输出目录必须可写，项目不会自动把文件写到其他位置。

## 环境要求

- Python 3.10+
- Node.js 22.12+
- FFmpeg，在 PATH 中，或用 `winget install Gyan.FFmpeg` 安装
- 首次使用时安装依赖：

```bash
pip install -r {skill_dir}/scripts/requirements.txt
cd {skill_dir}/scripts && npm install
```

`npm install` 会由 Puppeteer 自动下载 Chromium。Puppeteer 25 要求 Node.js 22.12 以上。

Edge TTS 联网即可使用，不需要额外模型。MOSS-TTS-Nano 和 CosyVoice 是本地引擎，首次使用前需要下载模型；模型较大，需要时再运行 setup 命令下载。

```bash
pip install -r {skill_dir}/scripts/requirements-optional.txt
```

```bash
python {skill_dir}/scripts/setup_local_tts.py --check
python {skill_dir}/scripts/setup_local_tts.py --engine moss
python {skill_dir}/scripts/setup_local_tts.py --engine cosyvoice
```

## 工作流程

1. 编写 `manifest.json`（页面结构、旁白和元素绑定），写入输出目录。
2. 生成草稿 HTML：

```bash
python {skill_dir}/scripts/gen_draft.py {output_dir}
```

这一步根据 manifest 生成 `draft.html`，包含主题样式、卡片布局、播放引擎和音频占位符。

3. 合成旁白并生成最终 HTML：

```bash
python {skill_dir}/scripts/build.py {output_dir}
```

这一步按 manifest 里的 `tts_engine` 生成旁白，计算每段音频的开始时间，把 base64 音频和时间轴写进 `draft.html`，输出 `final.html`。同时会生成 `timeline.json`，只包含页面时长和分段时间，不包含音频。

4. 用户需要视频时，先拆页，再录制：

```bash
python {skill_dir}/scripts/split_pages.py {output_dir}
node {skill_dir}/scripts/record_video.js {output_dir}/pages {output_dir}/{project}.mp4 [width] [height]
```

`split_pages.py` 会把 `final.html` 拆成 `pages/page_N.html`，每页单独初始化播放状态。`record_video.js` 逐页录制后用 FFmpeg 拼接。宽高不传时默认 1080×1920；建议按卡片比例传，例如 3:4 用 1080×1440，16:9 用 1920×1080。宽高比不一致时会等比缩放并用黑边补齐。

## manifest.json 格式

```json
{
  "title": "演示标题",
  "theme": "consulting-report",
  "tts_engine": "edge",
  "voice": "YunxiNeural",
  "aspect_ratio": "3:4",
  "rate": "+0%",
  "pitch": "+0Hz",
  "brand": {
    "name": "品牌名",
    "sub": "副标题"
  },
  "pages": [
    {
      "type": "cover",
      "title": "主标题",
      "subtitle": "副标题",
      "tags": "标签一 / 标签二",
      "firm": "落款",
      "label": "CATEGORY / TOPIC",
      "meta": ["第一行", "第二行"],
      "narration": [
        {
          "text": "欢迎来到本次演示，我们先用两分钟了解核心内容。",
          "elements": ["cover-title", "cover-subtitle"]
        },
        {
          "text": "每一页都会按旁白逐步展开。",
          "elements": ["cover-tags", "cover-footer"]
        }
      ]
    },
    {
      "type": "content",
      "title": "页面标题",
      "subtitle": "页面副标题",
      "series": "系列名",
      "page_num": "1/2",
      "category": "分类",
      "breadcrumb": "路径 / 到 / 这里",
      "sections": [
        {
          "heading": "章节标题",
          "heading_id": "p1-s1-heading",
          "components": [
            {
              "type": "exec",
              "id": "p1-s1-exec",
              "text": "核心结论。"
            },
            {
              "type": "list",
              "id": "p1-s1-list",
              "items": ["要点一", "要点二", "要点三"]
            }
          ]
        }
      ],
      "narration": [
        {
          "text": "先看这一页的核心结论。",
          "elements": ["p1-s1-heading"]
        },
        {
          "text": "这里有三个要点。",
          "elements": ["p1-s1-exec", "p1-s1-list"]
        }
      ]
    }
  ]
}
```

### 根字段

| 字段 | 说明 |
|------|------|
| `title` | 整个演示的标题 |
| `theme` | 主题 ID，12 套主题见下方表格 |
| `tts_engine` | `edge`、`moss`、`cosyvoice` 或 `dashscope`，默认 `edge` |
| `voice` | 对应引擎的音色名称 |
| `api_key` | DashScope 的 API key，可选；也可以设置环境变量 `DASHSCOPE_API_KEY` |
| `dashscope_model` | DashScope 模型，默认 `cosyvoice-v3-flash` |
| `aspect_ratio` | `3:4`、`4:3`、`1:1`、`9:16` 或 `16:9`，默认 `3:4` |
| `rate` | 语速，如 `+0%`、`+20%`、`-15%` |
| `pitch` | 音调，如 `+0Hz`、`+50Hz`、`-30Hz` |
| `brand.name` / `brand.sub` | 每页顶部显示的标识文字 |

### 页面字段

封面页（`type: "cover"`）：

| 字段 | 说明 |
|------|------|
| `title` | 主标题 |
| `subtitle` | 副标题 |
| `tags` | 标签 |
| `firm` | 底部落款 |
| `label` | 顶部类别文字 |
| `meta` | 顶部两行说明 |
| `narration` | 旁白分段 |

内容页（`type: "content"`）：

| 字段 | 说明 |
|------|------|
| `title` / `subtitle` | 页头标题 |
| `series` / `page_num` | 系列名和页码 |
| `category` / `breadcrumb` | 分类和路径 |
| `sections` | 章节数组，每项包含 `heading`、`heading_id` 和 `components` |
| `narration` | 旁白分段 |

组件类型：

| 类型 | 结构 |
|------|------|
| `exec` | `{"type":"exec","id":"...","text":"..."}` |
| `paragraph` | `{"type":"paragraph","id":"...","text":"..."}` |
| `blockquote` | `{"type":"blockquote","id":"...","text":"..."}` |
| `metrics` | `{"type":"metrics","id":"...","items":[{"label":"...","value":"...","desc":"..."}]}` |
| `table` | `{"type":"table","id":"...","rows":[{"label":"...","value":"...","status":"...","status_class":"status-red"}]}` |
| `list` | `{"type":"list","id":"...","items":["..."]}` |
| `grid` | `{"type":"grid","id":"...","items":["..."]}`，也支持带 `label`、`text`、`dark` 的对象 |

表格行的 `status_class` 可设为 `status` 或 `status-red`，默认是 `status`。

### 旁白分段

每段旁白是一个对象：

```json
{
  "text": "要朗读的文本",
  "elements": ["要同时出现的元素 ID"]
}
```

`elements` 里的 ID 必须真实存在于对应页面中。ID 在整份 HTML 里必须唯一，不能在不同页面重复使用 `s1-heading` 这类名字。ID 只使用字母、数字、连字符和下划线；中文、空值或重复 ID 会在生成草稿时直接报错，旁白里引用不存在的 ID 也会被校验拦截。

## 内容与旁白写法

- 每段旁白控制在 1-2 句话，中文 40 字左右，大约对应 10 秒音频。
- 先讲结论，再补充理由或例子。
- 旁白提到什么，就把对应的元素绑定到这一段。例如说到“三个要点”，就让列表出现。
- 段与段之间会自动留 0.6 秒静音，不要额外写过渡词。
- 用口语写旁白，不要照搬书面文章。

常见页面的分段数量：

| 页面 | 建议 |
|------|------|
| 封面 | 2-3 段，总时长 10-15 秒 |
| 内容页 | 4-8 段，总时长 25-45 秒 |
| 总结页 | 2-3 段，总时长 10-15 秒 |

绑定建议：

| 旁白内容 | 绑定的元素 |
|------|------|
| 章节引入 | 章节标题 |
| 核心观点 | `exec` 结论框 |
| 详细说明 | `paragraph` 段落 |
| “有几个要点” | `metrics` 或 `list` |
| 举例 | `table` 或数据组件 |
| 总结 | 强调段落 |
| 来源 | 底部 `source` |

## 音色与 TTS 引擎

Edge TTS 默认音色是 `YunxiNeural`，8 个中文音色：

| 音色 | 性别 | 风格 | 适合场景 |
|------|------|------|----------|
| `YunxiNeural` | 男 | 专业稳重 | 企业方案、方法论、技术 |
| `YunyangNeural` | 男 | 新闻播报 | 报告、数据、正式场合 |
| `YunjianNeural` | 男 | 大气 | 战略、愿景、领导力 |
| `YunxiaNeural` | 男 | 年轻 | 教育、培训、入门指南 |
| `XiaoxiaoNeural` | 女 | 温暖亲切 | 品牌、生活、故事 |
| `XiaoyiNeural` | 女 | 活泼 | 测评、对比、轻松话题 |
| `liaoning-XiaobeiNeural` | 女 | 东北口音 | 接地气、幽默 |
| `shaanxi-XiaoniNeural` | 女 | 中原口音 | 接地气、朴实 |

MOSS-TTS-Nano 默认音色是 `Junhao`，支持的中文音色：

| 音色 | 性别 | 风格 |
|------|------|------|
| `Junhao` | 男 | 专业稳重 |
| `Zhiming` | 男 | 温暖磁性 |
| `Weiguo` | 男 | 沉稳大气 |
| `Xiaoyu` | 女 | 温柔亲切 |
| `Yuewen` | 女 | 清晰自然 |
| `Lingyu` | 女 | 活泼明亮 |

CosyVoice 默认音色是 `中文女`，另有 `中文男`、`英文女`、`英文男`。

DashScope 默认音色是 `longanhuan`，其他可用音色见 `scripts/build.py` 里的 `DASHSCOPE_VOICES`。

### 引擎差异

- `edge`：联网生成，速度快，不需要模型。
- `moss`：本地模型，离线可用。首次运行会通过 Hugging Face 下载模型，默认使用官方源；设置 `MOSS_HF_MIRROR=1` 时改用 `hf-mirror.com` 镜像。
- `cosyvoice`：需要 Miniconda 的 `cosyvoice` 环境（Python 3.10）和模型，纯 CPU 生成很慢。
- `dashscope`：调用阿里云百炼 API，需要 `dashscope` 和 API key，`rate` / `pitch` 对它不生效。

## 画幅比例

| 比例 | 尺寸 | 适合场景 |
|------|------|----------|
| `3:4` | 600×800 | 竖版卡片，默认 |
| `4:3` | 800×600 | 横版，适合投影 |
| `1:1` | 700×700 | 方形，适合社交媒体 |
| `9:16` | 540×960 | 手机全屏竖屏 |
| `16:9` | 960×540 | 宽屏投影或视频 |

9:16 页面空间有限，每页最多放 2-3 个章节，每个章节只放一个组件；正文内容总高尽量控制在 500px 以内。内容放不下时，`gen_draft.py` 会把整张卡片等比缩小作为兜底，但正常内容仍应自然放下。

## HTML 结构

`gen_draft.py` 会生成完整的 HTML，不需要手工维护模板。生成的文件包含：

- 横向滚动的 `.deck` 和每页 `.page`；
- 封面 `.card--cover` 或内容 `.card--content`；
- 播放控制、圆点导航和隐藏的 `audio` 元素；
- `TIMELINE` 和 `AUDIO_SRC` 变量，构建时由 `build.py` 填入；
- 一个包裹在 IIFE 里的播放引擎，负责播放音频、按时间轴触发元素、自动翻页。

页面上的可动画元素都通过 ID 控制。封面固定使用：

```text
cover-title
cover-subtitle
cover-label
cover-tags
cover-footer
```

内容页的 ID 由 manifest 指定，建议用 `p{页号}-s{章节号}-{组件类型}`，例如：

```text
p1-s1-heading
p1-s1-exec
p1-s1-list
p2-s1-grid
```

如果只写 `s1-heading`，就必须保证整份演示里没有第二个 `s1-heading`。生成草稿时会校验 ID 唯一性和旁白引用，重复 ID 会导致构建直接报错。

## 主题

12 套主题：

| 主题 ID | 中文名 | 配色 | 适合场景 |
|---------|--------|------|----------|
| `consulting-report` | 咨询报告 | 藏蓝/青 | 企业方案、方法论 |
| `editorial` | 杂志风 | 米白/墨色 | 深度文章、评论 |
| `geek-report` | 极客风格 | 灰/荧光绿 | 技术评测、代码 |
| `rain-notes` | 雨天手记 | 纸张/雨蓝 | 随笔、感悟 |
| `sunrise` | 日光 | 暖纸/金 | 品牌、高端 |
| `terminal` | 终端风 | 暗色/纸色 | 开发者、CLI |
| `clean-review` | 简约测评 | 红/珊瑚 | 产品测评、对比 |
| `dot-matrix` | 点阵编辑 | 中性/信号色 | 数据报告、分析 |
| `pixel-report` | 黑底闪光 | 黑/荧光 | 游戏、赛博朋克 |
| `shiny-tiles` | 镭射网格 | 黑/玻璃银 | 设计、奢侈品 |
| `story-field` | 故事集 | 沙色/石色 | 叙事、案例 |
| `y2k-brand` | 千禧品牌 | 金属/粉/蓝 | 潮流、营销 |

也可以按内容关键词选择主题：企业方案选咨询报告，文章评论选杂志风，技术内容选极客风格，数据报告选点阵编辑，品牌故事选日光或故事集。

完整 CSS 参考见 `themes.md`。

## 生成步骤

1. 编写 `manifest.json`，规划每页结构、旁白和元素绑定。
2. 生成前先确认画幅比例、旁白音色、页数，以及可选的语速和音调，避免反复重跑。
3. 依次运行 `gen_draft.py`、`build.py`，得到 `final.html`。
4. 用当前环境支持的方式打开 HTML，确认播放正常。
5. 需要 MP4 时，再运行 `split_pages.py` 和 `record_video.js`。

## 常见问题

- `build.py` 报找不到 FFmpeg：安装 FFmpeg，或者用 `winget install Gyan.FFmpeg`。
- 页面元素不出现：检查旁白 `elements` 里的 ID 是否存在、是否拼写一致、是否整份 HTML 唯一。
- 某页没有旁白：`build.py` 会把该页时长记为 0，视频录制时自动按 2 秒静态页处理。
- 视频里元素和声音对不上：确认没有重复 ID，也不要手动改生成后的 HTML。
- 本地 TTS 报模型缺失：先运行 `setup_local_tts.py --check` 查看缺什么。
- 输出目录不可写：先换一个可写的输出目录。

## 验证

代码仓库自带了 Python 单元测试和语法检查，改动脚本后可以运行：

```bash
python -m unittest discover -s {skill_dir}/scripts/tests -v
node --check {skill_dir}/scripts/record_video.js
```

生成结果需要人工确认的点：

- 打开 `final.html`，每页旁白都能播放；
- 元素出现时机和旁白对应；
- 自动翻页、按钮、键盘和圆点导航正常；
- 需要视频时，MP4 总时长和音频一致，卡片没有被拉伸。
