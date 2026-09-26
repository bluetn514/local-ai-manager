<div align="center">

# Local AI Manager

### 给 Windows 用户的本地 AI 模型管理面板

用一个清爽的界面管理 **Ollama、本地模型、GPU / CPU / 内存**，并随时测试模型的实际表现。

**完全在本机运行 · 无需账号 · 不依赖云端服务**

[![GitHub stars](https://img.shields.io/github/stars/bluetn514/local-ai-manager?style=social)](https://github.com/bluetn514/local-ai-manager/stargazers)
![Windows](https://img.shields.io/badge/Windows-10%20%2F%2011-0078D4?logo=windows)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local-222222)

[快速开始](#快速开始) · [功能](#现在能做什么) · [项目结构](#项目结构) · [参与项目](#参与项目)

</div>

> **当前阶段：MVP。** 这是一个本地网页界面，由 FastAPI 和 Vite 在你的电脑上运行；目前不是打包好的 `.exe` 安装程序。

## 为什么做这个项目？

使用 Ollama 时，模型文件、运行状态和硬件占用往往分散在命令行与系统工具中。Local AI Manager 把这些信息放在同一个界面：查看机器还剩多少资源，找到已安装模型，加载或卸载模型，再用 Playground 直接测试回答速度。

**Local AI Manager is a local-first Ollama model manager and hardware dashboard for Windows.**

## 界面预览

页面包含 **Dashboard、Models、Playground、Logs、Settings**。项目截图预留在 [`docs/screenshots/`](docs/screenshots/)；目前还没有提交截图。欢迎提供真实使用截图或界面改进建议。

## 现在能做什么

| 页面 | 功能 |
| --- | --- |
| Dashboard | 实时查看操作系统、CPU 型号与使用率、内存、NVIDIA GPU 使用率与温度、显存和 Ollama 状态；显示当前已加载模型。没有 NVIDIA GPU 时正常降级。 |
| Models | 自动读取 Ollama 本地模型，显示名称、Tag、大小、修改时间、加载状态及可获取的量化信息。支持加载、卸载、测试、二次确认删除。 |
| Pull Model | 输入模型名，通过 Ollama 流式 API 显示下载状态、进度、已下载量、总量和速度。 |
| Playground | 选择已安装模型，流式查看单次提问的回答；显示输入 / 输出 Token、首 Token 时间、总生成时间和 Tokens/s。 |
| Logs | 查看 INFO、WARNING、ERROR 级别的本地应用日志，支持筛选、自动滚动和清空。 |

性能数据优先采用 Ollama 返回的官方统计字段；不可获取时显示 `—`，不会编造数值。

## 快速开始

### 1. 准备环境

- Windows 10 或 Windows 11
- Python 3.12+
- Node.js 20+ 与 npm
- [Ollama](https://ollama.com/)（模型相关功能需要）
- 可选：NVIDIA 显卡、驱动及 `nvidia-smi`，用于读取 GPU / 显存数据

首次安装 Python、Node 依赖需要联网。请确保 `python`、`node`、`npm` 可以在终端中运行。没有 NVIDIA 显卡仍可打开和使用其他功能。

### 2. 下载并启动

```powershell
git clone https://github.com/bluetn514/local-ai-manager.git
cd local-ai-manager
```

双击 **`start.bat`**。脚本会检查环境、按需安装依赖、启动后端和前端，并打开浏览器：

- 界面：<http://127.0.0.1:5173>
- API 文档：<http://127.0.0.1:8000/docs>

也可以从 GitHub 仓库的 **Code → Download ZIP** 下载，不必使用 Git 命令。首次进入后，可在 Models 页输入适合自己硬件的 Ollama 模型名并点击 **Pull Model**。

### 手动开发启动

在项目根目录打开两个终端。

```powershell
# 终端 1：后端
python -m pip install --target backend\.deps -r backend\requirements.txt
$env:PYTHONPATH = "$PWD;$PWD\backend\.deps"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
# 终端 2：前端
cd frontend
npm install
npm run dev
```

## 项目结构

```text
local-ai-manager/
├─ backend/
│  ├─ api/          FastAPI 接口：系统、Ollama、模型、聊天、日志
│  ├─ services/     Ollama、系统资源和 GPU 服务层
│  ├─ core/         配置与日志
│  ├─ database/     SQLite 数据库
│  └─ main.py       应用入口
├─ frontend/
│  └─ src/          React + TypeScript 界面
├─ data/            本地运行数据（自动创建，不提交到 Git）
├─ start.bat        Windows 一键启动脚本
└─ README.md
```

**技术栈：** Python、FastAPI、httpx、psutil、SQLite、React、TypeScript、Vite、Tailwind CSS。

## 当前边界

- 第一阶段只做本地模型管理和测试，没有云端账号、RAG 或复杂 Agent 功能。
- **停止 Ollama** 只管理由本工具启动的服务，避免结束其他程序启动的进程。
- Playground 目前针对单次提问，不保存多轮会话。
- 应用日志与本工具启动的 Ollama 进程日志分别保存；模型和硬件信息仍以本机 Ollama 与系统工具的实际返回为准。

## 下一步

1. 模型搜索与下载目录，让新用户更容易找到适合自己硬件的模型。
2. 每个模型的上下文长度、驻留时间等运行参数设置。
3. 可保存、导出的本地模型性能对比记录。

## 参与项目

欢迎通过 [Issues](https://github.com/bluetn514/local-ai-manager/issues) 反馈问题或建议，也欢迎提交 Pull Request。请附上 Windows 版本、Ollama 版本、复现步骤和相关错误信息，便于定位问题；提交日志前请检查其中是否包含个人信息。

如果这个项目对你有帮助，欢迎点一个 **Star** ⭐。它能让更多需要本地 AI 工具的 Windows 用户发现这个项目。
