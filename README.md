# Local AI Manager

A local desktop browser dashboard for managing Ollama models and monitoring Windows AI hardware. Stage one MVP runs entirely on your machine. No account or cloud service is needed.

## Screenshots

Add screenshots to `docs/screenshots/` (for example `docs/screenshots/dashboard.png`).

## Features

- Live CPU, RAM, NVIDIA GPU and VRAM monitoring, with graceful fallback without NVIDIA hardware.
- Ollama installation, version and connection status; start and stop services launched by this app; view captured Ollama process logs.
- Installed and loaded models with size, modification date and quantization where available.
- Load, unload and confirm deletion of models; pull models with streaming progress, bytes and speed.
- Streaming chat playground with Ollama token counts and timing metrics.
- SQLite backed INFO, WARNING and ERROR application log viewer with auto scroll, filtering and clearing.

## Requirements

Windows 10/11, Python 3.12+, Node.js 20+, npm, and [Ollama](https://ollama.com/) for model features. NVIDIA drivers and `nvidia-smi` enable GPU metrics; they are optional.

## Install and launch

Double-click `start.bat`. It checks the tools, installs Python and Node dependencies on the first run, starts both local servers and opens the browser. Internet access is needed for the first dependency install. Ollama can already be running, or start it from the Dashboard. The app binds to loopback only.

Manual development launch, in separate terminals from the project root:

```powershell
python -m pip install --target backend\.deps -r backend\requirements.txt
$env:PYTHONPATH = "$PWD;$PWD\backend\.deps"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. API docs: http://127.0.0.1:8000/docs.

## Project structure

```text
backend/
  api/            FastAPI route handlers
  services/       Ollama, system and GPU operations
  core/           Configuration and logging
  database/       SQLite connection and schema
  main.py         Application setup
frontend/
  src/            React TypeScript UI and API client
data/             Runtime SQLite database and Ollama process log
start.bat         Windows launcher
```

## Stack

FastAPI, Python, SQLite, psutil, httpx; React, TypeScript, Vite, Tailwind CSS.

## Notes

Stop only manages an Ollama service started by this application, so another application's Ollama process is not terminated. Metrics rely on Ollama's official response fields; unavailable values appear as a dash. Application logs and Ollama process logs are separate.

## Roadmap

1. Model search and download catalog.
2. Per model runtime settings such as context length and keep alive.
3. Exportable benchmark history for local models.
