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

### v1.1.8 — 2026-04-30

#### 本次新增
- **退出服务按钮** — 网页底部新增「退出服务」按钮，点击确认后安全关闭后台服务，解决关闭浏览器后进程残留问题
- **去除 --windowed 打包参数** — Windows/macOS 版本不再隐藏控制台，可按 Ctrl+C 手动退出

### v1.1.7 — 2026-04-30

#### 本次新增
- **停止测试按钮** — 测试过程中可随时中断，不必等待全部 10 项完成
- **中断后表单自动保留** — 停止后 URL、API Key、模型 ID、Temperature 等输入内容全部保留，方便重新测试
- **即时反馈** — 点击停止后按钮立即变为"停止中..."并置灰，避免重复点击

### v1.1.6

#### 本次新增
- **停止测试功能** — 通过 `threading.Event` 实现实时中断，停止后表单数据完整保留

### v1.1.5 — 2026-04-29

#### 本次修复
- **Kimi K2.5 temperature 兼容性** — 为 Kimi K2.5 测试临时添加 `temperature=1` 容错参数，后回退
- **优化协议检测逻辑** — 改进 OpenAI/Anthropic 协议自动识别的准确性

### v1.1.2 — 2026-04-29

#### 本次新增
- **Temperature 输入框** — 新增温度参数配置，带中文标签"Temperature（温度/随机性，选填，默认0.2）"

### v1.1.0 — 2026-04-17

#### 初始发布
- 10 项综合能力测试
- 5 维度雷达图可视化
- OpenAI/Anthropic 双协议支持
- 本地运行，无 CORS 限制
