from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_preference import UserCharacter
from app.services.characters import get_character

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class CharacterUpdateRequest(BaseModel):
    character_id: str


@router.get("/{user_id}/character")
def get_user_character(user_id: str, db: Session = Depends(get_db)):
    """사용자의 선택된 캐릭터 반환 (미설정 시 404)"""
    row = db.query(UserCharacter).filter(UserCharacter.user_id == user_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="설정된 캐릭터가 없습니다.")
    return get_character(row.character_id)


@router.put("/{user_id}/character")
def update_user_character(
    user_id: str, body: CharacterUpdateRequest, db: Session = Depends(get_db)
):
    """사용자의 캐릭터 선택 저장 (upsert)"""
    row = db.query(UserCharacter).filter(UserCharacter.user_id == user_id).first()
    if row is None:
        row = UserCharacter(user_id=user_id, character_id=body.character_id)
        db.add(row)
    else:
        row.character_id = body.character_id
    db.commit()
    return get_character(row.character_id)