@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo ERROR: Python 3.12+ is required on PATH. & pause & exit /b 1)
where node >nul 2>nul || (echo ERROR: Node.js is required on PATH. & pause & exit /b 1)
where npm >nul 2>nul || (echo ERROR: npm is required on PATH. & pause & exit /b 1)
where ollama >nul 2>nul || echo WARNING: Ollama is not on PATH. The UI will still open.
python -c "import sys; assert sys.version_info >= (3,12), 'Python 3.12+ required'" || (pause & exit /b 1)
if not exist "backend\.deps\fastapi" (
  echo Installing Python dependencies...
  python -m pip install --target backend\.deps -r backend\requirements.txt || (echo ERROR: Python install failed. & pause & exit /b 1)
)
if not exist "frontend\node_modules\vite" (
  echo Installing frontend dependencies...
  pushd frontend
  call npm install || (popd & echo ERROR: npm install failed. & pause & exit /b 1)
  popd
)
set "PYTHONPATH=%CD%;%CD%\backend\.deps"
start "Local AI Manager API" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
start "Local AI Manager UI" /D "%CD%\frontend" cmd /k "npm run dev"
timeout /t 4 >nul
start "" http://127.0.0.1:5173
echo Local AI Manager started. Close the two server windows to stop it.
