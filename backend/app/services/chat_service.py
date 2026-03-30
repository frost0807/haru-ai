import uuid
from datetime import date, datetime

from google.genai import types
from sqlalchemy.orm import Session

from app.services import diary_service, emotion_service, rag_service
from app.services.characters import get_character
from app.services.gemini_client import get_gemini_client, CHAT_MODEL

# AI가 종료를 제안할 때 포함하는 신호 문구
_READY_SIGNALS = ["일기 정리해줄까", "일기 써줄까", "일기로 남겨줄까"]

# 인메모리 세션 저장소 { session_id: 세션 데이터 }
_sessions: dict[str, dict] = {}


def _build_system_prompt(character_id: str, recent_diaries: list) -> str:
    """캐릭터 기반 시스템 프롬프트 + 최근 일기 컨텍스트 생성"""
    character = get_character(character_id)
    prompt = character["system_prompt"]
    if recent_diaries:
        prompt += "\n\n[최근 일기 컨텍스트]\n"
        labels = ["어제 일기", "그저께 일기", "3일 전 일기"]
        for i, d in enumerate(recent_diaries):
            label = labels[i] if i < len(labels) else f"{i + 1}일 전 일기"
            prompt += f"{label}: {d.content[:150]}\n"
        prompt += "→ 이전 내용과 연결되는 질문을 자연스럽게 섞어줘"
    return prompt


def _to_gemini_contents(history: list[dict]) -> list[types.Content]:
    """내부 대화 이력을 Gemini API 형식으로 변환"""
    return [
        types.Content(role=item["role"], parts=[types.Part(text=item["content"])])
        for item in history
    ]


def _is_ready_to_finish(ai_message: str, turn_count: int) -> bool:
    """대화 종료 가능 여부 판단 (5~10회 대화 기준)"""
    if turn_count >= 10:
        return True
    if turn_count >= 5:
        return any(signal in ai_message for signal in _READY_SIGNALS)
    return False


def start_session(user_id: str, diary_date: date, db: Session, character_id: str = "haru") -> dict:
    """세션 시작 — 최근 일기 로드 후 AI 첫 질문 반환"""
    # 해당 날짜 일기가 이미 존재하면 중복 에러
    existing = diary_service.get_diary_by_date(db, user_id, diary_date)
    if existing is not None:
        raise ValueError(f"DIARY_EXISTS:{existing.id}")

    recent_diaries = diary_service.get_recent_diaries(db, user_id, days=3)
    system_prompt = _build_system_prompt(character_id, recent_diaries)

    # Gemini 호출 — 첫 질문 생성
    client = get_gemini_client()
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[types.Content(role="user", parts=[types.Part(text="일기 시작할게")])],
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )
    first_question = response.text.strip()

    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    _sessions[session_id] = {
        "user_id": user_id,
        "diary_date": diary_date,
        "system_prompt": system_prompt,
        "history": [
            {"role": "user", "content": "일기 시작할게"},
            {"role": "model", "content": first_question},
        ],
        "turn_count": 0,
        "created_at": datetime.now(),
    }

    return {"session_id": session_id, "message": first_question, "status": "in_progress"}


def send_message(session_id: str, user_message: str) -> dict:
    """사용자 메시지 처리 — AI 후속 질문 반환"""
    session = _sessions.get(session_id)
    if session is None:
        raise KeyError(f"세션을 찾을 수 없습니다: {session_id}")

    # 사용자 메시지 추가 및 턴 카운트 증가
    session["history"].append({"role": "user", "content": user_message})
    session["turn_count"] += 1

    # Gemini 호출
    client = get_gemini_client()
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=_to_gemini_contents(session["history"]),
        config=types.GenerateContentConfig(system_instruction=session["system_prompt"]),
    )
    ai_message = response.text.strip()
    session["history"].append({"role": "model", "content": ai_message})

    status = (
        "ready_to_finish"
        if _is_ready_to_finish(ai_message, session["turn_count"])
        else "in_progress"
    )

    return {"session_id": session_id, "message": ai_message, "status": status}


def finish_session(session_id: str, db: Session) -> dict:
    """세션 종료 — 일기 생성, 감정 분석, DB 저장"""
    session = _sessions.get(session_id)
    if session is None:
        raise KeyError(f"세션을 찾을 수 없습니다: {session_id}")

    history = session["history"]

    # 일기 본문 생성
    diary_content = diary_service.generate_diary(history)

    # 감정 분석
    emotion = emotion_service.analyze_emotion(diary_content)

    # PostgreSQL 저장
    saved_diary = diary_service.save_diary(
        db=db,
        user_id=session["user_id"],
        diary_date=session["diary_date"],
        content=diary_content,
        emotion=emotion,
        conversation_history=history,
    )

    # ChromaDB 임베딩 저장
    rag_service.store_diary(saved_diary)

    # 세션 삭제
    del _sessions[session_id]

    return {
        "diary_id": saved_diary.id,
        "diary_date": str(saved_diary.diary_date),
        "content": diary_content,
        "emotion": emotion,
    }