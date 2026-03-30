from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini
    GEMINI_API_KEY: str = ""

    # PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/haru_ai"

    # CORS — 쉼표로 구분된 허용 도메인 목록
    # 예: "http://localhost:5173,https://haruai.vercel.app"
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    model_config = {"env_file": ".env"}


settings = Settings()