from app.database import SessionLocal
from app.models.diary import Diary
from app.models.diary_embedding import DiaryEmbedding
from app.services.gemini_client import get_gemini_client

_EMBEDDING_MODEL = "gemini-embedding-2-preview"


def _embed(text: str) -> list[float]:
    """텍스트를 Gemini 임베딩 벡터로 변환"""
    client = get_gemini_client()
    response = client.models.embed_content(
        model=_EMBEDDING_MODEL,
        contents=text,
    )
    return response.embeddings[0].values


def _build_embed_text(diary: Diary) -> str:
    """임베딩할 텍스트 구성 (본문 + 감정 + 키워드)"""
    text = diary.content
    if diary.primary_emotion:
        text += f"\n감정: {diary.primary_emotion}"
    if diary.emotion_keywords:
        text += f"\n키워드: {', '.join(diary.emotion_keywords)}"
    return text


def store_diary(diary: Diary) -> None:
    """일기를 pgvector에 임베딩하여 저장 (upsert)"""
    embed_text = _build_embed_text(diary)
    embedding = _embed(embed_text)

    db = SessionLocal()
    try:
        existing = (
            db.query(DiaryEmbedding)
            .filter(DiaryEmbedding.diary_id == diary.id)
            .first()
        )
        if existing:
            existing.embed_text = embed_text
            existing.embedding = embedding
        else:
            row = DiaryEmbedding(
                diary_id=diary.id,
                user_id=diary.user_id,
                diary_date=str(diary.diary_date),
                embed_text=embed_text,
                embedding=embedding,
                primary_emotion=diary.primary_emotion,
                secondary_emotion=diary.secondary_emotion,
                emotion_intensity=diary.emotion_intensity,
                keywords=", ".join(diary.emotion_keywords) if diary.emotion_keywords else None,
            )
            db.add(row)
        db.commit()
    finally:
        db.close()


def delete_diary(diary: Diary) -> None:
    """pgvector에서 일기 임베딩 삭제"""
    db = SessionLocal()
    try:
        db.query(DiaryEmbedding).filter(DiaryEmbedding.diary_id == diary.id).delete()
        db.commit()
    finally:
        db.close()


def search(user_id: str, query: str, top_k: int = 5) -> list[dict]:
    """자연어 질문으로 유사 일기 코사인 유사도 검색"""
    query_embedding = _embed(query)

    db = SessionLocal()
    try:
        results = (
            db.query(DiaryEmbedding)
            .filter(DiaryEmbedding.user_id == user_id)
            .order_by(DiaryEmbedding.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )
        return [
            {
                "diary_id": r.diary_id,
                "diary_date": r.diary_date,
                "document": r.embed_text,
                "primary_emotion": r.primary_emotion,
            }
            for r in results
        ]
    finally:
        db.close()