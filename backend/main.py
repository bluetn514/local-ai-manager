from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.api import system, ollama, models, chat, logs
from backend.core.logger import record
from backend.database.database import initialize

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    record("INFO", "Backend started")
    yield

app = FastAPI(title="Local AI Manager", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    status = 400 if isinstance(exc, ValueError) else 503 if isinstance(exc, RuntimeError) else 500
    try:
        record("WARNING" if status == 400 else "ERROR", f"{request.url.path}: {exc}")
    except Exception:
        pass
    return JSONResponse(status_code=status, content={"ok": False, "error": str(exc) if status != 500 else "Internal server error"})

for router in (system.router, ollama.router, models.router, chat.router, logs.router):
    app.include_router(router, prefix="/api")

@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "data": {"status": "healthy"}}
