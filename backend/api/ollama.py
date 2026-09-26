from fastapi import APIRouter
from backend.services import ollama_service as service

router = APIRouter(prefix="/ollama", tags=["ollama"])

@router.get("/status")
async def status() -> dict:
    return {"ok": True, "data": await service.status()}

@router.post("/start")
def start() -> dict:
    return {"ok": True, "data": service.start()}

@router.post("/stop")
def stop() -> dict:
    return {"ok": True, "data": service.stop()}
