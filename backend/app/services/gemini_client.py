from google import genai

from app.config import settings

# Gemini 3.1 Flash Lite Preview 모델 ID (3.0 Flash 대비 7.5x 저렴, 더 빠름)
CHAT_MODEL = "gemini-3.1-flash-lite-preview"

_client: genai.Client | None = None


def get_gemini_client() -> genai.Client:
    """Gemini 클라이언트 싱글턴 반환"""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client
