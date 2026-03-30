from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from google.genai.errors import ClientError, ServerError
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.characters import get_all_characters
from app.schemas.chat import (
    ChatFinishRequest,
    ChatFinishResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatStartRequest,
    ChatStartResponse,
)
from app.services import chat_service

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.get("/characters")
def list_characters():
    """사용 가능한 캐릭터 목록 반환"""
    return get_all_characters()


def _handle_gemini_error(e: ServerError | ClientError):
    """Gemini API 에러 → HTTP 에러 변환"""
    if e.status_code == 503:
        raise HTTPException(status_code=503, detail="AI 서버가 잠시 과부하 상태입니다. 잠시 후 다시 시도해주세요.")
    if e.status_code == 429:
        raise HTTPException(status_code=429, detail="API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
    raise HTTPException(status_code=500, detail="AI 응답 중 오류가 발생했습니다.")


@router.post("/start", response_model=ChatStartResponse)
async def start_chat(request: ChatStartRequest, db: Session = Depends(get_db)):
    """일기 작성 세션을 시작한다."""
    diary_date = (
        date.fromisoformat(request.diary_date) if request.diary_date else date.today()
    )
    try:
        return chat_service.start_session(request.user_id, diary_date, db, request.character_id)
    except ValueError as e:
        # DIARY_EXISTS:{diary_id} 형태로 기존 일기 ID 전달
        msg = str(e)
        if msg.startswith("DIARY_EXISTS:"):
            diary_id = msg.split(":")[1]
            raise HTTPException(status_code=409, detail={"code": "DIARY_EXISTS", "diary_id": int(diary_id)})
        raise HTTPException(status_code=400, detail=str(e))
    except (ServerError, ClientError) as e:
        _handle_gemini_error(e)


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """대화를 이어간다."""
    try:
        return chat_service.send_message(request.session_id, request.message)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ServerError, ClientError) as e:
        _handle_gemini_error(e)


@router.post("/finish", response_model=ChatFinishResponse)
async def finish_chat(request: ChatFinishRequest, db: Session = Depends(get_db)):
    """대화를 종료하고 일기를 생성한다."""
    try:
        return chat_service.finish_session(request.session_id, db)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ServerError, ClientError) as e:
        _handle_gemini_error(e)
