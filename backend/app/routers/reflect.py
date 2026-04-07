from fastapi import APIRouter, HTTPException
from google.genai.errors import ClientError, ServerError
from pydantic import BaseModel

from app.services import reflect_service
from app.routers.chat import _handle_gemini_error

router = APIRouter(prefix="/api/v1/reflect", tags=["reflect"])


class ReflectRequest(BaseModel):
    user_id: str
    question: str


class ReflectSourceItem(BaseModel):
    diary_id: int
    diary_date: str
    preview: str


class ReflectResponse(BaseModel):
    answer: str
    sources: list[ReflectSourceItem]


@router.post("/ask", response_model=ReflectResponse)
async def ask_reflect(request: ReflectRequest):
    """과거 일기 기반 자연어 질의응답"""
    try:
        return reflect_service.ask(request.user_id, request.question)
    except (ServerError, ClientError) as e:
        _handle_gemini_error(e)