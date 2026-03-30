\# 하루AI (HaruAI) - AI 대화형 일기 서비스



\## 프로젝트 문서

아래 문서를 반드시 읽고 개발을 진행할 것:

\- docs/01\_기능정의서.md — 기능 정의, 대화 플로우, 감정 분석 구조

\- docs/02\_아키텍처.md — 시스템 구성, DB 모델, 데이터 흐름, 프롬프트 설계

\- docs/03\_API명세.md — API 엔드포인트 명세



\## 기술 스택

\- Backend: FastAPI

\- LLM: Gemini 2.5 Flash

\- Embedding: gemini-embedding-001

\- Vector DB: ChromaDB

\- RDB: PostgreSQL

\- ORM: SQLAlchemy



\## 현재 진행 상황

\- \[x] 프로젝트 문서 작성 완료

\- \[x] FastAPI 기본 구조 (models, schemas, routers)

\- \[ ] ChatService — Gemini API 연동, 대화 플로우 (← 다음 작업)

\- \[ ] DiaryService — 일기 생성/저장

\- \[ ] EmotionService — 감정 분석

\- \[ ] RAGService — ChromaDB 임베딩/검색



\## 개발 규칙

\- 한국어 주석, 한국어 커밋 메시지

\- 기존 코드 최소 변경, 필요한 부분만 수정

\- 서비스 레이어에 비즈니스 로직 집중 (라우터는 얇게)

