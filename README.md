# Benchmark Tool - 大模型跑分工具

支持 OpenAI 和 Anthropic 协议的大模型基准测试工具。

## 功能

- 自动检测 API 协议（OpenAI / Anthropic）
- 10 项综合能力测试
- 雷达图可视化
- 结果导出 Markdown

## 下载

| 平台 | 下载 |
|------|------|
| Windows | [benchmark-windows.exe](https://github.com/dadaniya99/benchmark/releases/latest) |
| macOS | [benchmark-macos](https://github.com/dadaniya99/benchmark/releases/latest) |
| Linux | [benchmark-linux](https://github.com/dadaniya99/benchmark/releases/latest) |

## 使用

### Windows
1. 下载 `benchmark-windows.exe`
2. 双击运行
3. 浏览器自动打开界面

### macOS
1. 下载 `benchmark-macos`
2. **右键点击** → 选择"打开" → 点击"打开"（首次运行需要）
3. 浏览器自动打开界面

> **提示**：如果双击没反应，请用右键"打开"的方式运行。这是 macOS 的安全机制，不是程序有问题。

### Linux
1. 下载 `benchmark-linux`
2. 终端运行：`chmod +x benchmark-linux && ./benchmark-linux`
3. 浏览器自动打开界面

### 通用步骤
1. 程序启动后浏览器会自动打开
2. 输入 Base URL、API Key 和模型 ID
3. 点击"开始测试"

## 从源码运行

```bash
pip install -r requirements.txt
python benchmark.py
```

## 技术栈

- Python 3.11
- ThreadingHTTPServer（内置）
- HTML/CSS/JavaScript（前端）
- PyInstaller（打包）
