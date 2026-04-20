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
- ✅ **跨平台** - Windows、Mac、Linux 都能用

## 快速开始

### 方式一：直接运行 Python（推荐）

```bash
# 1. 安装依赖
pip install requests

# 2. 运行
python benchmark.py

# 3. 浏览器自动打开 http://localhost:18288
```

### 方式二：打包成可执行文件

**Windows:**
```powershell
# 右键点击 package.ps1 → 使用 PowerShell 运行
```

**Mac/Linux:**
```bash
chmod +x package.sh
./package.sh
```

打包完成后在 `dist/` 目录找到可执行文件。

## 使用说明

1. **填写 API 信息**
   - Base URL: 你的 API 端点（如 `https://api.openai.com/v1`）
   - API Key: 你的 API 密钥
   - 模型 ID: 如 `gpt-4o`、`claude-sonnet-4-20250514`

2. **协议选择（可选）**
   - 留空：自动识别
   - OpenAI：强制使用 OpenAI 协议
   - Anthropic：强制使用 Anthropic 协议

3. **粘贴示例代码（可选）**
   - 支持 curl、Python、JavaScript 格式
   - 自动提取 URL、协议和模型

4. **点击开始测试**
   - 等待约 2-5 分钟完成 10 项测试
   - 查看总分和雷达图
   - 导出 Markdown 报告

## 测试项目

| 维度 | 测试项 |
|------|--------|
| 💻 代码能力 | 代码修改、代码二次修改、编程能力专项 |
| 🧠 推理分析 | 复杂推理（海盗分金币）、事实与幻觉控制 |
| 📝 语言表达 | 长文结构化输出、中文真实沟通 |
| ✏️ 上下文处理 | 二次改写/上下文衔接、8轮多轮对话 |
| 🎯 综合执行 | 多约束执行 |

## 评分标准

- **50 分**: 🏆 顶级水平
- **40-49 分**: 🌟 优秀
- **30-39 分**: 👍 中等
- **<30 分**: ⚠️ 偏弱

## 常见问题

**Q: 为什么显示 404 错误？**
A: 可能是协议不匹配。尝试在"协议类型"中选择 Anthropic，或让程序自动检测。

**Q: 支持哪些模型？**
A: 所有兼容 OpenAI 或 Anthropic 协议的模型都支持，包括 GPT-4、Claude、Gemini、MiniMax 等。

**Q: 测试需要多长时间？**
A: 通常 2-5 分钟，取决于模型响应速度。

## 技术说明

- 前端：纯 HTML + CSS + JavaScript（无框架依赖）
- 后端：Python HTTP 服务器（标准库）
- 通信：本地 HTTP API，无 CORS 限制
- 安全：API Key 仅本地使用，不上传任何服务器

## License

MIT License
