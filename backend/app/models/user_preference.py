from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserCharacter(Base):
    __tablename__ = "user_characters"

    user_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    character_id: Mapped[str] = mapped_column(String(20), nullable=False, default="haru")

    def __repr__(self):
        return f"<UserCharacter {self.user_id} → {self.character_id}>"