from pydantic import BaseModel


class ChatStartRequest(BaseModel):
    user_id: str
    diary_date: str | None = None  # YYYY-MM-DD, 기본값 오늘
    character_id: str = "haru"  # 선택한 캐릭터 ID


class ChatStartResponse(BaseModel):
    session_id: str
    message: str
    status: str  # "in_progress"


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str


class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    status: str  # "in_progress" | "ready_to_finish"


class ChatFinishRequest(BaseModel):
    session_id: str


class EmotionResponse(BaseModel):
    primary_emotion: str
    secondary_emotion: str | None = None
    intensity: int
    keywords: list[str]
    summary: str


class ChatFinishResponse(BaseModel):
    diary_id: int
    diary_date: str
    content: str
    emotion: EmotionResponse
