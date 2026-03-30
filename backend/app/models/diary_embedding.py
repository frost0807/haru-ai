from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.database import Base

# gemini-embedding-2-preview 출력 차원
EMBEDDING_DIM = 3072


class DiaryEmbedding(Base):
    __tablename__ = "diary_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    diary_id: Mapped[int] = mapped_column(
        ForeignKey("diaries.id", ondelete="CASCADE"), unique=True
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    diary_date: Mapped[str] = mapped_column(String(20), nullable=False)
    embed_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(EMBEDDING_DIM), nullable=False)

    # 검색 결과에서 사용할 메타데이터
    primary_emotion: Mapped[str | None] = mapped_column(String(20))
    secondary_emotion: Mapped[str | None] = mapped_column(String(20))
    emotion_intensity: Mapped[int | None] = mapped_column(Integer)
    keywords: Mapped[str | None] = mapped_column(String(500))

    def __repr__(self):
        return f"<DiaryEmbedding diary_id={self.diary_id}>"