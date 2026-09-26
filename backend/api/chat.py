import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.services import ollama_service as service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    model: str
    message: str

@router.post("")
async def chat(body: ChatRequest) -> StreamingResponse:
    service.validate_name(body.model)
    if not body.message.strip() or len(body.message) > 20000:
        raise ValueError("Message must contain 1–20000 characters")
    async def events():
        async for event in service.chat(body.model, body.message):
            yield json.dumps(event) + "\n"
    return StreamingResponse(events(), media_type="application/x-ndjson")
