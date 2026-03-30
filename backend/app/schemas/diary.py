from datetime import datetime

from pydantic import BaseModel


class ConversationItem(BaseModel):
    role: str
    message: str

    model_config = {"from_attributes": True}


class DiaryListItem(BaseModel):
    diary_id: int
    diary_date: str
    content: str
    primary_emotion: str | None
    emotion_intensity: int | None
    emotion_summary: str | None

    model_config = {"from_attributes": True}


class DiaryListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[DiaryListItem]


class EmotionDetail(BaseModel):
    primary_emotion: str | None
    secondary_emotion: str | None
    intensity: int | None
    keywords: list[str] | None
    summary: str | None


class DiaryDetailResponse(BaseModel):
    diary_id: int
    diary_date: str
    content: str
    emotion: EmotionDetail
    conversation: list[ConversationItem]
    created_at: datetime

    model_config = {"from_attributes": True}


class DiaryDeleteResponse(BaseModel):
    message: str
    diary_id: int
