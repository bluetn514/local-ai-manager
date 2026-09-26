from fastapi import APIRouter
from backend.services.system_service import snapshot

router = APIRouter(prefix="/system", tags=["system"])

@router.get("")
def system() -> dict:
    return {"ok": True, "data": snapshot()}
