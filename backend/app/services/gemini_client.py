from google import genai

from app.config import settings

# Gemini 2.5 Flash (안정 버전)
CHAT_MODEL = "gemini-2.5-flash"

_client: genai.Client | None = None


def get_gemini_client() -> genai.Client:
    """Gemini 클라이언트 싱글턴 반환"""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client
