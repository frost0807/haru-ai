import json
import logging
import time

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.models import user_preference, diary_embedding  # noqa: F401 — 테이블 생성 등록
from app.routers import chat, diary, user, reflect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("haruai.http")

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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # /health는 노이즈가 많아서 제외
    if request.url.path == "/health":
        return await call_next(request)

    # 요청 바디 읽기
    body_bytes = await request.body()
    try:
        body = json.loads(body_bytes) if body_bytes else None
    except Exception:
        body = body_bytes.decode(errors="replace") if body_bytes else None

    logger.info("→ %s %s | body: %s", request.method, request.url.path, json.dumps(body, ensure_ascii=False) if body else "-")

    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000

    # 응답 바디 읽기
    resp_body_bytes = b""
    async for chunk in response.body_iterator:
        resp_body_bytes += chunk
    try:
        resp_body = json.loads(resp_body_bytes)
    except Exception:
        resp_body = resp_body_bytes.decode(errors="replace")

    logger.info("← %s %s | status: %d | %.0fms | body: %s",
        request.method, request.url.path, response.status_code, elapsed,
        json.dumps(resp_body, ensure_ascii=False) if isinstance(resp_body, dict) else str(resp_body)[:200]
    )

    return Response(
        content=resp_body_bytes,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
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
app.include_router(reflect.router)


@app.get("/")
async def root():
    return {"message": "하루AI API 서버", "version": "0.1.0"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """DB 연결 확인 — Supabase 잠김 방지 ping용"""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}