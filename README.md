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
| Windows | [benchmark-windows.exe](https://github.com/maonanbei/benchmark/releases/latest) |
| macOS | [benchmark-macos](https://github.com/maonanbei/benchmark/releases/latest) |
| Linux | [benchmark-linux](https://github.com/maonanbei/benchmark/releases/latest) |

## 使用

1. 下载对应平台的可执行文件
2. 双击运行（Windows/macOS）或 `./benchmark-linux`（Linux）
3. 浏览器自动打开界面
4. 输入 API Key 和配置，开始测试

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
