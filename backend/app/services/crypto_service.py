from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return _fernet


def encrypt(text: str) -> str:
    """평문 → 암호문"""
    return _get_fernet().encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    """암호문 → 평문. 기존 평문 데이터(마이그레이션 전)는 그대로 반환"""
    try:
        return _get_fernet().decrypt(text.encode()).decode()
    except (InvalidToken, ValueError):
        return text