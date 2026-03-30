from datetime import date, timedelta

from google.genai import types
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.diary import Diary
from app.services.gemini_client import get_gemini_client, CHAT_MODEL

_SYSTEM_PROMPT = """아래 대화 내용을 바탕으로 오늘의 일기를 작성해줘.

규칙:
1. 1인칭 시점, 일기체
2. 대화에서 나온 사실만 포함 (절대 지어내지 마)
3. 시간 순서대로 정리
4. 감정 표현은 사용자의 원래 표현 유지
5. 50~300자 내외
6. 날짜는 포함하지 마 (별도 저장됨)"""


def generate_diary(conversation_history: list[dict]) -> str:
    """대화 내역으로 일기 본문 생성"""
    # 대화 내역을 텍스트로 변환
    conv_text = "\n".join(
        f"{'AI' if item['role'] == 'model' else '나'}: {item['content']}"
        for item in conversation_history
    )

    client = get_gemini_client()
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=conv_text,
        config=types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
    )
    return response.text.strip()


def save_diary(
    db: Session,
    user_id: str,
    diary_date: date,
    content: str,
    emotion: dict,
    conversation_history: list[dict],
) -> Diary:
    """일기 + 대화 내역을 PostgreSQL에 저장"""
    diary = Diary(
        user_id=user_id,
        diary_date=diary_date,
        content=content,
        primary_emotion=emotion.get("primary_emotion"),
        secondary_emotion=emotion.get("secondary_emotion"),
        emotion_intensity=emotion.get("intensity"),
        emotion_keywords=emotion.get("keywords"),
        emotion_summary=emotion.get("summary"),
    )
    db.add(diary)
    db.flush()  # diary.id 확보 (커밋 전)

    for seq, item in enumerate(conversation_history):
        conv = Conversation(
            diary_id=diary.id,
            role="assistant" if item["role"] == "model" else "user",
            message=item["content"],
            seq_order=seq,
        )
        db.add(conv)

    db.commit()
    db.refresh(diary)
    return diary


def get_diary_by_date(db: Session, user_id: str, diary_date: date) -> Diary | None:
    """특정 날짜 일기 조회 (중복 확인용)"""
    return (
        db.query(Diary)
        .filter(Diary.user_id == user_id, Diary.diary_date == diary_date)
        .first()
    )


def get_recent_diaries(db: Session, user_id: str, days: int = 3) -> list[Diary]:
    """최근 n일 일기 조회 (채팅 컨텍스트 주입용)"""
    cutoff = date.today() - timedelta(days=days)
    return (
        db.query(Diary)
        .filter(Diary.user_id == user_id, Diary.diary_date >= cutoff)
        .order_by(Diary.diary_date.desc())
        .limit(days)
        .all()
    )


def get_diary_list(
    db: Session,
    user_id: str,
    start_date: date | None,
    end_date: date | None,
    emotion: str | None,
    page: int,
    size: int,
) -> dict:
    """일기 목록 조회 (필터 + 페이징)"""
    query = db.query(Diary).filter(Diary.user_id == user_id)

    if start_date:
        query = query.filter(Diary.diary_date >= start_date)
    if end_date:
        query = query.filter(Diary.diary_date <= end_date)
    if emotion:
        query = query.filter(Diary.primary_emotion == emotion)

    total = query.count()
    diaries = (
        query.order_by(Diary.diary_date.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = [
        {
            "diary_id": d.id,
            "diary_date": str(d.diary_date),
            "content": d.content,
            "primary_emotion": d.primary_emotion,
            "emotion_intensity": d.emotion_intensity,
            "emotion_summary": d.emotion_summary,
        }
        for d in diaries
    ]

    return {"total": total, "page": page, "size": size, "items": items}


def get_diary_detail(db: Session, diary_id: int) -> Diary | None:
    """일기 상세 조회 (대화 내역 포함)"""
    return db.query(Diary).filter(Diary.id == diary_id).first()


def delete_diary(db: Session, diary_id: int) -> bool:
    """일기 삭제 (conversations 는 CASCADE 로 자동 삭제)"""
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if diary is None:
        return False
    db.delete(diary)
    db.commit()
    return True