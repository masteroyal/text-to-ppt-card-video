# 更新日志

## 3.4.2 - 2026-08-06

- 修复无旁白页在 HTML 自动播放时被直接跳过的问题，构建时统一按 2 秒静态页处理
- 无旁白页改用真实时间计时，不再依赖始终为 0 的音频进度
- manifest 校验增加 ID 格式、全局唯一性和旁白引用检查
- 空 ID 或非 ASCII ID 不再统一退化成 `el`，缺失 ID 自动生成唯一 ID
- DashScope 移出基础依赖，只在需要该引擎时安装
- CI 不再递归拉取 CosyVoice 和 MOSS 子模块
- 补充无旁白页播放和 ID 校验相关单元测试

## 3.4.1 - 2026-07-08

- 抽取共享 TTS 配置模块，统一音色表和可执行文件查找
- CosyVoice Python 改为按环境变量、常见安装路径和 conda 依次查找
- MOSS 模型镜像改为通过 `MOSS_HF_MIRROR` 显式启用
- manifest.json 增加结构校验，错误信息包含具体字段路径
- 视频录制不再关闭浏览器跨域安全限制
- 补充本地 TTS 可选依赖和统一检查脚本

## 3.4.0 - 2026-04-18

- 修复视频导出时画幅不一致导致卡片拉伸的问题，改为等比缩放并补黑边
- 录制中途失败时确保 Puppeteer 浏览器被关闭
- CosyVoice 批量合成失败时立即报错，不再继续生成缺音频的视频
- 构建前校验 `tts_engine`，不支持的引擎直接退出
- 最低 Node.js 版本提高到 22.12，与 Puppeteer 25 保持一致
- 重写 README 和 skill 文档，修正表述不一致的地方
- README 增加英文版，并在中英文之间提供切换入口

## 3.3.0 - 2026-02-02

- 项目更名为 text-to-ppt-card-video
- `gen_draft.py` 接入文档中的 12 套主题
- 新增 `setup_local_tts.py`，用于检查并下载本地 TTS 模型
- 对 manifest 内容做 HTML 转义，并规范化元素 ID
- TTS 失败或占位符未替换时快速失败
- 无旁白页面也能录制，并自动补静音音频
- 新增 requirements、示例、单元测试和 CI
- 修正 NOTICE 中的 MOSS-TTS-Nano 归属说明

## 3.2.0 - 2025-12-16

- 支持 manifest.json 定义页面、旁白和元素绑定
- Edge TTS 生成中文旁白并内嵌到单文件 HTML
- 元素按旁白时间轴逐段出现
- 通过 Puppeteer 和 FFmpeg 导出 MP4
- 支持 3:4、4:3、16:9 等画幅比例
