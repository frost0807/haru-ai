from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    diary_id: Mapped[int] = mapped_column(ForeignKey("diaries.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'assistant' or 'user'
    message: Mapped[str] = mapped_column(Text, nullable=False)
    seq_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 관계
    diary: Mapped["Diary"] = relationship(back_populates="conversations")

    def __repr__(self):
        return f"<Conversation [{self.role}] {self.message[:30]}>"
