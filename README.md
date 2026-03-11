# 하루AI (HaruAI)

> AI 대화형 일기 서비스 — 말하듯 쓰고, 물어보듯 돌아보는 나만의 일기장

## 프로젝트 소개

하루AI는 빈 페이지 앞에서 고민할 필요 없는 일기 서비스입니다.
AI가 질문하고, 짧게 답하면 오늘의 일기가 완성됩니다.
쌓인 일기는 AI가 분석해서 나도 몰랐던 내 패턴을 알려줍니다.

### 핵심 가치
- **쓰기 귀찮음 해결** — AI 대화로 일기 작성, 타이핑 최소화
- **기억 보조** — "그때 내가 뭐라고 했지?" 시맨틱 검색으로 과거 일기 탐색
- **자기 인사이트** — 감정 패턴, 반복되는 고민, 변화 추이를 AI가 분석

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | FastAPI |
| LLM | Gemini 2.5 Flash |
| Embedding | gemini-embedding-001 |
| Vector DB | ChromaDB |
| RDB | PostgreSQL |
| STT | Whisper API (Phase 3) |
| Frontend | Web (Phase 2+) |

## 디렉토리 구조

```
haru-ai/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py             # 환경설정
│   ├── models/               # DB 모델 (SQLAlchemy)
│   │   ├── diary.py
│   │   └── conversation.py
│   ├── schemas/              # Pydantic 스키마
│   │   ├── diary.py
│   │   └── chat.py
│   ├── services/             # 비즈니스 로직
│   │   ├── chat_service.py       # 대화 관리
│   │   ├── diary_service.py      # 일기 생성/저장
│   │   ├── emotion_service.py    # 감정 분석
│   │   ├── rag_service.py        # RAG 검색
│   │   └── insight_service.py    # 패턴 분석
│   ├── routers/              # API 라우터
│   │   ├── chat.py
│   │   ├── diary.py
│   │   └── insight.py
│   └── prompts/              # 프롬프트 템플릿
│       ├── diary_chat.py
│       ├── diary_generate.py
│       └── emotion_analyze.py
├── docs/
│   ├── 01_기능정의서.md
│   ├── 02_아키텍처.md
│   └── 03_API명세.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 개발 로드맵

### Phase 1 — MVP: 대화형 일기 작성
- AI 대화로 일기 이끌어내기
- 일기 자동 생성 + 감정 태깅
- PostgreSQL 저장 + ChromaDB 임베딩
- 기본 일기 조회 (날짜별)

### Phase 2 — RAG 인사이트
- 과거 일기 시맨틱 검색 ("내가 언제 힘들었지?")
- 맥락 기반 질문 ("어제 그 건 해결됐어?")
- 주간/월간 감정 리포트
- 패턴 분석 ("요즘 야근 많이 한다")

### Phase 3 — 음성 입력
- Whisper API 연동
- 음성 → 텍스트 → 대화 플로우
- 핸즈프리 일기 작성

## 시작하기

```bash
# 환경 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 의존성 설치
pip install -r requirements.txt

# PostgreSQL DB 생성
createdb haru_ai

# 서버 실행
uvicorn app.main:app --reload
```

## 라이선스

MIT License
