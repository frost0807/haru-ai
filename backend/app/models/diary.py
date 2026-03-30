from datetime import date, datetime

from sqlalchemy import String, Text, Integer, Date, DateTime, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Diary(Base):
    __tablename__ = "diaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    diary_date: Mapped[date] = mapped_column(Date, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 감정 분석
    primary_emotion: Mapped[str | None] = mapped_column(String(20))
    secondary_emotion: Mapped[str | None] = mapped_column(String(20))
    emotion_intensity: Mapped[int | None] = mapped_column(Integer)
    emotion_keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    emotion_summary: Mapped[str | None] = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 관계
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="diary", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Diary {self.diary_date} [{self.primary_emotion}]>"
