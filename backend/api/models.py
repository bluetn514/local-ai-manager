import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.services import ollama_service as service

router = APIRouter(prefix="/models", tags=["models"])

class ModelName(BaseModel):
    name: str

class DeleteModel(ModelName):
    confirm: bool

@router.get("")
async def models() -> dict:
    return {"ok": True, "data": await service.models()}

@router.post("/load")
async def load(body: ModelName) -> dict:
    return {"ok": True, "data": await service.load(body.name)}

@router.post("/unload")
async def unload(body: ModelName) -> dict:
    return {"ok": True, "data": await service.unload(body.name)}

@router.post("/delete")
async def delete(body: DeleteModel) -> dict:
    if not body.confirm:
        raise ValueError("Deletion requires confirmation")
    return {"ok": True, "data": await service.delete(body.name)}

@router.post("/pull")
async def pull(body: ModelName) -> StreamingResponse:
    service.validate_name(body.name)
    async def events():
        async for event in service.pull(body.name):
            yield json.dumps(event) + "\n"
    return StreamingResponse(events(), media_type="application/x-ndjson")
