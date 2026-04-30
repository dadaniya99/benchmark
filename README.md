# AI 大模型 50 分制基准测试工具

一个简单易用的本地大模型评测工具，10 项测试、50 分满分，跑完出总分和雷达图。

## 下载

| 平台 | 下载 |
|------|------|
| Windows | [benchmark-windows.exe](https://github.com/dadaniya99/benchmark/releases/latest/download/benchmark-windows.exe) |
| macOS | [benchmark-macos](https://github.com/dadaniya99/benchmark/releases/latest/download/benchmark-macos) |
| Linux | [benchmark-linux](https://github.com/dadaniya99/benchmark/releases/latest/download/benchmark-linux) |

## 功能特点

- ✅ **10 项综合能力测试** - 代码、推理、语言、上下文处理
- ✅ **5 维度雷达图可视化** - 一眼看出模型强项和弱项
- ✅ **自动协议检测** - 支持 OpenAI 和 Anthropic 协议自动识别
- ✅ **本地运行** - API Key 不经过第三方，安全私密
- ✅ **停止测试按钮** - 测试中可随时中断，表单自动保留

## 使用

1. 下载对应平台的可执行文件
2. 双击运行（Windows/macOS）或 `./benchmark-linux`（Linux）
3. 浏览器自动打开界面
4. 输入 API Key 和配置，开始测试

## 从源码运行

```bash
python benchmark.py
```

## Changelog

### v1.1.7
- 新增停止测试按钮，支持中断后恢复表单
- 停止按钮即时反馈："停止中..."

### v1.1.6
- 停止测试功能（threading.Event 实时中断 + 表单保留）

### v1.1.5
- 修复 Kimi K2.5 temperature 兼容性
- 优化协议检测逻辑

### v1.1.2
- 添加 Temperature 输入框（中文标签）

### v1.1.0
- 初始发布版本
