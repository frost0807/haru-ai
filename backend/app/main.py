from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.models import user_preference, diary_embedding  # noqa: F401 — 테이블 생성 등록
from app.routers import chat, diary, user

# pgvector 확장 활성화 후 테이블 생성
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="하루AI (HaruAI)",
    description="AI 대화형 일기 서비스",
    version="0.1.0",
)

# CORS — 환경변수에서 허용 도메인 목록 읽기
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router)
app.include_router(diary.router)
app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "하루AI API 서버", "version": "0.1.0"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """DB 연결 확인 — Supabase 잠김 방지 ping용"""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}