# 하루AI (HaruAI)

> AI 캐릭터와 대화하며 쓰는 일기 서비스

말하듯 대화하면 AI가 일기를 완성해줍니다.
쌓인 일기는 감정 분석과 시맨틱 검색으로 다시 꺼내볼 수 있습니다.

**배포 주소**: https://haru-ai.vercel.app

---

## 주요 기능

- **대화형 일기 작성** — AI 캐릭터가 질문하며 대화를 이끌고, 대화 내용으로 일기를 자동 생성
- **캐릭터 선택** — 하루(공감형), 솔(정리형), 밝음(활기찬) 중 오늘 기분에 맞는 친구 선택
- **감정 분석** — 15가지 감정 중 대표 감정 태깅 및 한 줄 감정 요약
- **RAG 검색** — 과거 일기를 임베딩해 맥락 기반 대화 ("어제 그 일은 어떻게 됐어?")
- **Google 로그인** — Supabase Auth 기반 OAuth 인증
- **PWA 지원** — 모바일 홈 화면 설치 가능

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | FastAPI, Python |
| LLM | Gemini 3.1 Flash Lite Preview |
| Embedding | Gemini Embedding 2 Preview |
| Vector DB | pgvector (PostgreSQL 확장) |
| RDB | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| Frontend | React 19, Vite 8, Tailwind CSS |
| Auth | Supabase Auth (Google OAuth) |
| 배포 | Railway (Backend), Vercel (Frontend) |

---

## 프로젝트 구조

```
haru-ai/
├── backend/
│   └── app/
│       ├── main.py               # FastAPI 앱 진입점
│       ├── config.py             # 환경 설정
│       ├── database.py           # DB 연결 (SQLAlchemy)
│       ├── models/               # DB 모델
│       ├── schemas/              # Pydantic 스키마
│       ├── services/
│       │   ├── chat_service.py       # 대화 세션 관리
│       │   ├── diary_service.py      # 일기 CRUD + 생성
│       │   ├── emotion_service.py    # 감정 분석
│       │   ├── rag_service.py        # 임베딩 + 검색
│       │   ├── characters.py         # 캐릭터 정의
│       │   └── gemini_client.py      # Gemini API 클라이언트
│       └── routers/
│           ├── chat.py           # /api/v1/chat/*
│           ├── diary.py          # /api/v1/diary/*
│           └── user.py           # /api/v1/users/*
├── frontend/
│   └── src/
│       ├── api/client.js         # Axios API 호출
│       ├── lib/supabase.js       # Supabase 클라이언트
│       ├── contexts/
│       │   └── AuthContext.jsx   # 인증 상태 관리
│       ├── components/           # 공통 컴포넌트
│       └── pages/
│           ├── LoginPage.jsx
│           ├── CharacterSelectPage.jsx
│           ├── ChatPage.jsx
│           ├── DiaryListPage.jsx
│           └── DiaryDetailPage.jsx
└── docs/
    ├── 01_기능정의서.md
    ├── 02_아키텍처.md
    └── 03_API명세.md
```

---

## 로컬 실행

### 사전 준비

- Python 3.11+
- Node.js 18+
- PostgreSQL (pgvector 확장 포함)
- Gemini API 키
- Supabase 프로젝트

### Backend

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env에 GEMINI_API_KEY, DATABASE_URL, ALLOWED_ORIGINS 입력

# 서버 실행
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
# .env 파일 생성 후 아래 내용 입력:
# VITE_SUPABASE_URL=https://your-project.supabase.co
# VITE_SUPABASE_ANON_KEY=your-anon-key
# VITE_API_URL=http://localhost:8000/api/v1  (로컬 백엔드 사용 시)

# 개발 서버 실행
npm run dev
```

---

## 환경 변수

### Backend `.env`

```
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=postgresql://user:password@host:port/dbname
ALLOWED_ORIGINS=http://localhost:5173,https://your-domain.vercel.app
```

### Frontend `.env`

```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=https://your-railway-url/api/v1
```

---

## 배포

| 서비스 | 플랫폼 | 설정 파일 |
|--------|--------|-----------|
| Backend | Railway | `backend/Procfile` |
| Frontend | Vercel | `frontend/vercel.json` |
| Database | Supabase | — |

---

## 라이선스

MIT License