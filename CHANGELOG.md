# 更新日志

## 1.0.1 - 2026-08-06

- 恢复 lieflat-html-design 的 MIT 出处声明
- TTS 段生成失败时构建直接报错，不再静默产出残缺音频
- 拆页音频改为按 JSON 数组解析，不再依赖正则匹配
- 空音频页拆页时保留 `[""]` 占位，避免误判为无音频
- 视频录制遇到缺失页面时报错，避免静默截断
- 补充播放按钮的无障碍标签，统一数字字体变量
- 完善 README、package.json 元数据和示例 manifest

## 1.0.0 - 2026-08-06

Text-to-PPT-Card-Video 1.0.0 发布。基于 manifest.json 生成带旁白和动画的 PPT 卡片演示，支持 Edge TTS、MOSS-TTS-Nano、CosyVoice、DashScope 四种语音引擎，可输出单文件 HTML，也能导出 MP4。
