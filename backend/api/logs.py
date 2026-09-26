from fastapi import APIRouter
from backend.core import logger
from backend.core.config import DATA_DIR

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("")
def logs(level: str | None = None) -> dict:
    if level is not None and level not in {"INFO", "WARNING", "ERROR"}:
        raise ValueError("Invalid log level")
    return {"ok": True, "data": logger.recent(level)}

@router.delete("")
def clear() -> dict:
    logger.clear()
    return {"ok": True, "data": {"message": "Logs cleared"}}

@router.get("/ollama")
def ollama_logs() -> dict:
    path = DATA_DIR / "ollama.log"
    content = path.read_text(encoding="utf-8", errors="replace")[-30000:] if path.exists() else "No Ollama log captured by this app yet."
    return {"ok": True, "data": {"content": content}}
