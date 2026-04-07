from google.genai import types

from app.services import rag_service
from app.services.gemini_client import get_gemini_client, CHAT_MODEL

_REFLECT_SYSTEM_PROMPT = """너는 사용자의 과거 일기를 기억하는 친구야.

규칙:
- 주어진 일기 내용만 근거로 대답해. 절대 지어내지 마.
- 반말로, 짧고 자연스럽게 대답해.
- 일기 날짜를 구체적으로 언급하면서 대답해줘. 예: "3월 18일 일기에서...", "2주 전에..."
- 관련 일기가 없거나 내용이 부족하면 솔직하게 "관련된 일기를 못 찾겠어" 또는 "그런 내용은 일기에 없었어" 라고 답해.
- 질문이 일기 내용과 맞지 않으면 "일기에서는 못 찾겠어. 더 적어줬으면 알 수 있었을 텐데!" 라고 답해."""


def ask(user_id: str, question: str) -> dict:
    """자연어 질문으로 과거 일기 기반 답변 생성"""
    relevant = rag_service.search(user_id, question, top_k=5)

    if not relevant:
        # 일기 자체가 없는 경우
        return {
            "answer": "아직 일기가 없어서 찾기가 어려워. 일기를 쓰고 나서 물어봐!",
            "sources": [],
        }

    # 일기 컨텍스트 구성
    context = "\n\n".join([
        f"[{r['diary_date']}]\n{r['document']}"
        for r in relevant
    ])
    user_input = f"내 일기:\n{context}\n\n질문: {question}"

    client = get_gemini_client()
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[types.Content(role="user", parts=[types.Part(text=user_input)])],
        config=types.GenerateContentConfig(system_instruction=_REFLECT_SYSTEM_PROMPT),
    )

    sources = [
        {
            "diary_id": r["diary_id"],
            "diary_date": r["diary_date"],
            "preview": r["document"][:100],
        }
        for r in relevant
    ]

    return {"answer": response.text.strip(), "sources": sources}