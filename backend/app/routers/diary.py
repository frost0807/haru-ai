from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.diary import (
    ConversationItem,
    DiaryDeleteResponse,
    DiaryDetailResponse,
    DiaryListResponse,
    EmotionDetail,
)
from app.services import diary_service, rag_service

router = APIRouter(prefix="/api/v1/diary", tags=["diary"])


@router.get("", response_model=DiaryListResponse)
async def get_diaries(
    user_id: str = Query(...),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    emotion: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """일기 목록을 조회한다."""
    return diary_service.get_diary_list(
        db=db,
        user_id=user_id,
        start_date=date.fromisoformat(start_date) if start_date else None,
        end_date=date.fromisoformat(end_date) if end_date else None,
        emotion=emotion,
        page=page,
        size=size,
    )


@router.get("/{diary_id}", response_model=DiaryDetailResponse)
async def get_diary(diary_id: int, db: Session = Depends(get_db)):
    """일기 상세를 조회한다. 대화 내역 포함."""
    diary = diary_service.get_diary_detail(db, diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail=f"diary_id={diary_id} not found")

    return DiaryDetailResponse(
        diary_id=diary.id,
        diary_date=str(diary.diary_date),
        content=diary.content,
        emotion=EmotionDetail(
            primary_emotion=diary.primary_emotion,
            secondary_emotion=diary.secondary_emotion,
            intensity=diary.emotion_intensity,
            keywords=diary.emotion_keywords,
            summary=diary.emotion_summary,
        ),
        conversation=[
            ConversationItem(role=c.role, message=c.message)
            for c in sorted(diary.conversations, key=lambda x: x.seq_order)
        ],
        created_at=diary.created_at,
    )


@router.delete("/{diary_id}", response_model=DiaryDeleteResponse)
async def delete_diary(diary_id: int, db: Session = Depends(get_db)):
    """일기를 삭제한다."""
    diary = diary_service.get_diary_detail(db, diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail=f"diary_id={diary_id} not found")

    rag_service.delete_diary(diary)
    diary_service.delete_diary(db, diary_id)

    return DiaryDeleteResponse(message="삭제 완료", diary_id=diary_id)