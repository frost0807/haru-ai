import json
import re

from google.genai import types

from app.services.gemini_client import get_gemini_client, CHAT_MODEL

_SYSTEM_PROMPT = """아래 일기를 읽고 감정을 분석해줘.

분석 기준:
- primary_emotion: 하루 중 가장 강하게 느낀 감정 (마지막 감정이 아닌, 가장 두드러진 감정)
- secondary_emotion: 하루를 마무리하는 시점의 감정 또는 두 번째로 강한 감정
- intensity: primary_emotion의 강도 (1~10)
- keywords: 감정을 유발한 핵심 사건/단어 3개
- summary: 하루의 감정 흐름을 20자 이내로 요약

사용 가능한 감정 목록:
- 긍정: joy(기쁨), proud(뿌듯함), excited(설렘), grateful(감사), relieved(안도), content(만족)
- 중립: calm(평온), bored(지루함), nostalgic(그리움)
- 부정: tired(피곤), sadness(슬픔), anger(화남), anxiety(불안), lonely(외로움), frustrated(답답함)

반드시 다음 JSON 형식으로만 응답:
{
  "primary_emotion": "위 목록 중 하나",
  "secondary_emotion": "위 목록 중 하나 또는 null",
  "intensity": 1~10,
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "summary": "20자 이내 감정 요약"
}"""


def _parse_json(text: str) -> dict:
    # 마크다운 코드블록 제거 후 JSON 파싱
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    result = json.loads(text)

    # "null" 문자열 → None 변환
    if result.get("secondary_emotion") == "null":
        result["secondary_emotion"] = None

    return result


def analyze_emotion(diary_content: str) -> dict:
    """일기 텍스트로 감정 분석 수행"""
    client = get_gemini_client()
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=diary_content,
        config=types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
    )
    return _parse_json(response.text.strip())