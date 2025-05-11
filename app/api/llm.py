from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import httpx
from pydantic import BaseModel
from typing import List, Literal, Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

router = APIRouter(prefix="/api/llm", tags=["llm"])

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class LLMRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

try:
    from app.api.auth import get_current_user  # JWT authentication
except ImportError:  # fallback if auth module not available
    async def get_current_user():
        return None

@router.post("")
async def llm_proxy(request: Request, body: LLMRequest, user=Depends(get_current_user)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured on server")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = body.dict()
    async with httpx.AsyncClient() as client:
        resp = await client.post(OPENAI_API_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return JSONResponse(content=resp.json())
