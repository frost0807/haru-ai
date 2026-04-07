import logging
import uuid
from datetime import date, datetime, timedelta

from google.genai import types
from sqlalchemy.orm import Session

from app.services import diary_service, emotion_service, rag_service
from app.services.characters import get_character
from app.services.gemini_client import get_gemini_client, CHAT_MODEL

logger = logging.getLogger("haruai.chat")

# AI가 종료를 제안할 때 포함하는 신호 문구
_READY_SIGNALS = ["일기 정리해줄까", "일기 써줄까", "일기로 남겨줄까"]

# 인메모리 세션 저장소 { session_id: 세션 데이터 }
_sessions: dict[str, dict] = {}


def _get_time_context(current_hour: int | None) -> str:
    """현재 시간 기반 시간대 컨텍스트 생성"""
    if current_hour is None:
        return ""
    if 0 <= current_hour < 6:
        return "지금은 새벽이야. 하루가 아직 안 끝났거나 잠 못 자고 있는 걸 수도 있어. 하루가 완전히 마무리되지 않았을 수 있으니 단정짓지 마."
    elif 6 <= current_hour < 12:
        return "지금은 오전이야. 하루가 막 시작됐거나 어제 이야기를 하는 걸 수도 있어. 아직 하루가 다 안 지났으니 오늘 일을 단정짓지 마."
    elif 12 <= current_hour < 18:
        return "지금은 오후야. 하루가 아직 진행 중이야. 오늘 일을 다 마무리된 것처럼 말하지 마."
    elif 18 <= current_hour < 22:
        return "지금은 저녁이야. 하루가 어느 정도 마무리되고 있어."
    else:
        return "지금은 밤이야. 하루가 거의 끝났어."


def _build_system_prompt(character_id: str, recent_diaries: list, today: date, current_hour: int | None) -> str:
    """캐릭터 기반 시스템 프롬프트 + 최근 일기 컨텍스트 생성"""
    character = get_character(character_id)
    prompt = character["system_prompt"]

    # 오늘 날짜 + 시간대 컨텍스트
    prompt += f"\n\n[현재 상황]\n오늘 날짜: {today.strftime('%Y년 %m월 %d일')}"
    time_ctx = _get_time_context(current_hour)
    if time_ctx:
        prompt += f"\n{time_ctx}"

    # 최근 일기 컨텍스트 (날짜 포함)
    if recent_diaries:
        prompt += "\n\n[최근 일기 컨텍스트]\n"
        for d in recent_diaries:
            diff = (today - d.diary_date).days
            if diff == 0:
                label = "오늘 일기"
            elif diff == 1:
                label = "어제 일기"
            else:
                label = f"{diff}일 전 일기 ({d.diary_date.strftime('%m/%d')})"
            prompt += f"{label}: {d.content[:200]}\n"
        prompt += "→ 일기의 날짜를 파악하고, 이전 내용과 자연스럽게 연결되는 질문을 섞어줘."

    return prompt


def _to_gemini_contents(history: list[dict]) -> list[types.Content]:
    """내부 대화 이력을 Gemini API 형식으로 변환"""
    return [
        types.Content(role=item["role"], parts=[types.Part(text=item["content"])])
        for item in history
    ]


def _build_rag_contents(history: list[dict], user_id: str, user_message: str, today: date) -> list[types.Content]:
    """RAG 검색 결과를 현재 턴 사용자 메시지에 주입. 실패하면 기본 contents 반환"""
    try:
        results = rag_service.search(user_id, user_message, top_k=3)
    except Exception:
        return _to_gemini_contents(history)

    if not results:
        return _to_gemini_contents(history)

    # 최근 7일 이내 일기는 이미 system_prompt에 포함되므로 제외
    cutoff = (today - timedelta(days=7)).isoformat()
    filtered = [r for r in results if r["diary_date"] < cutoff]

    if not filtered:
        return _to_gemini_contents(history)

    # 날짜 레이블 + 미리보기
    lines = []
    for r in filtered:
        diff = (today - date.fromisoformat(r["diary_date"])).days
        if diff < 14:
            label = f"{diff}일 전 ({r['diary_date'][5:]})"
        elif diff < 60:
            label = f"{diff // 7}주 전 ({r['diary_date'][5:]})"
        else:
            label = f"{diff // 30}달 전 ({r['diary_date'][5:]})"
        lines.append(f"- {label}: {r['document'][:150]}")

    context_block = "[관련된 과거 일기 (자동 참고)]\n" + "\n".join(lines)

    # 마지막 user 메시지에만 컨텍스트 주입 (session history는 그대로 유지)
    enriched_message = f"{context_block}\n\n---\n\n{user_message}"
    contents = _to_gemini_contents(history[:-1])
    contents.append(types.Content(role="user", parts=[types.Part(text=enriched_message)]))
    return contents


def _is_ready_to_finish(ai_message: str, turn_count: int) -> bool:
    """대화 종료 가능 여부 판단 (5~10회 대화 기준)"""
    if turn_count >= 10:
        return True
    if turn_count >= 5:
        return any(signal in ai_message for signal in _READY_SIGNALS)
    return False


def start_session(user_id: str, diary_date: date, db: Session, character_id: str = "haru", current_hour: int | None = None) -> dict:
    """세션 시작 — 최근 일기 로드 후 AI 첫 질문 반환"""
    # 해당 날짜 일기가 이미 존재하면 중복 에러
    existing = diary_service.get_diary_by_date(db, user_id, diary_date)
    if existing is not None:
        raise ValueError(f"DIARY_EXISTS:{existing.id}")

    recent_diaries = diary_service.get_recent_diaries(db, user_id, days=7)
    system_prompt = _build_system_prompt(character_id, recent_diaries, diary_date, current_hour)

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

    # Gemini 호출 — 3턴 이상 + 10자 이상일 때 RAG 컨텍스트 주입
    client = get_gemini_client()
    use_rag = session["turn_count"] >= 3 and len(user_message.strip()) >= 10
    if use_rag:
        contents = _build_rag_contents(
            session["history"], session["user_id"], user_message, session["diary_date"]
        )
    else:
        contents = _to_gemini_contents(session["history"])
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=session["system_prompt"]),
    )
    ai_message = response.text.strip()
    session["history"].append({"role": "model", "content": ai_message})

    signals_found = [s for s in _READY_SIGNALS if s in ai_message]
    status = (
        "ready_to_finish"
        if _is_ready_to_finish(ai_message, session["turn_count"])
        else "in_progress"
    )

    logger.info(
        "[%s] turn=%d | use_rag=%s | status=%s | signals=%s\n  user: %s\n  ai:   %s",
        session_id, session["turn_count"], use_rag, status, signals_found,
        user_message[:100], ai_message[:200],
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