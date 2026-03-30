# API 명세

## Base URL

```
http://localhost:8000/api/v1
```

## 1. 대화 (Chat)

### POST /chat/start
일기 작성 세션을 시작한다. AI의 첫 질문을 반환한다.

**Request:**
```json
{
  "user_id": "user_001",
  "diary_date": "2025-03-09"     // 선택. 기본값 오늘
}
```

**Response:**
```json
{
  "session_id": "sess_abc123",
  "message": "오늘 하루 어땠어?",
  "status": "in_progress"
}
```

### POST /chat/message
대화를 이어간다. 사용자 답변을 보내면 AI 후속 질문을 반환한다.

**Request:**
```json
{
  "session_id": "sess_abc123",
  "message": "좀 피곤했어, 야근함"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123",
  "message": "뭐 때문에 야근했어?",
  "status": "in_progress"        // "in_progress" | "ready_to_finish"
}
```

`status`가 `ready_to_finish`이면 AI가 충분한 대화가 이루어졌다고 판단한 것.
이후 `/chat/finish` 호출 또는 대화 계속 가능.

### POST /chat/finish
대화를 종료하고 일기를 생성한다.

**Request:**
```json
{
  "session_id": "sess_abc123"
}
```

**Response:**
```json
{
  "diary_id": 42,
  "diary_date": "2025-03-09",
  "content": "오늘은 LWC 모바일 이슈 때문에 야근을 했다. 버그를 절반쯤 잡았는데...",
  "emotion": {
    "primary_emotion": "anger",
    "secondary_emotion": "anxiety",
    "intensity": 7,
    "keywords": ["야근", "버그", "마감"],
    "summary": "업무 과부하로 인한 스트레스"
  }
}
```

## 2. 일기 (Diary)

### GET /diary
일기 목록을 조회한다.

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| user_id | string | Y | 사용자 ID |
| start_date | string | N | 조회 시작일 (YYYY-MM-DD) |
| end_date | string | N | 조회 종료일 (YYYY-MM-DD) |
| emotion | string | N | 감정 필터 (joy, sadness, anger, anxiety, calm, excited) |
| page | integer | N | 페이지 (기본값 1) |
| size | integer | N | 페이지당 건수 (기본값 10) |

**Response:**
```json
{
  "total": 30,
  "page": 1,
  "size": 10,
  "items": [
    {
      "diary_id": 42,
      "diary_date": "2025-03-09",
      "content": "오늘은 LWC 모바일 이슈 때문에...",
      "primary_emotion": "anger",
      "emotion_intensity": 7,
      "emotion_summary": "업무 과부하로 인한 스트레스"
    }
  ]
}
```

### GET /diary/{diary_id}
일기 상세를 조회한다. 대화 내역 포함.

**Response:**
```json
{
  "diary_id": 42,
  "diary_date": "2025-03-09",
  "content": "오늘은 LWC 모바일 이슈 때문에 야근을 했다...",
  "emotion": {
    "primary_emotion": "anger",
    "secondary_emotion": "anxiety",
    "intensity": 7,
    "keywords": ["야근", "버그", "마감"],
    "summary": "업무 과부하로 인한 스트레스"
  },
  "conversation": [
    { "role": "assistant", "message": "오늘 하루 어땠어?" },
    { "role": "user", "message": "좀 피곤했어, 야근함" },
    { "role": "assistant", "message": "뭐 때문에 야근했어?" },
    { "role": "user", "message": "LWC 모바일 이슈" },
    { "role": "assistant", "message": "해결은 됐어?" },
    { "role": "user", "message": "반쯤" }
  ],
  "created_at": "2025-03-09T23:30:00"
}
```

### DELETE /diary/{diary_id}
일기를 삭제한다. PostgreSQL + ChromaDB 동시 삭제.

**Response:**
```json
{
  "message": "삭제 완료",
  "diary_id": 42
}
```

## 3. 검색 (Search) — Phase 2

### POST /search
자연어로 과거 일기를 검색한다.

**Request:**
```json
{
  "user_id": "user_001",
  "query": "회사에서 힘들었던 날",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "최근 3개월간 업무 스트레스를 언급한 일기가 8건 있어요. 특히 2월 둘째 주에 집중되어 있네요.",
  "related_diaries": [
    {
      "diary_id": 38,
      "diary_date": "2025-02-12",
      "content": "오늘도 야근...",
      "primary_emotion": "anger",
      "relevance_score": 0.92
    }
  ]
}
```

## 4. 인사이트 (Insight) — Phase 2

### GET /insight/weekly
주간 리포트를 조회한다.

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| user_id | string | Y | 사용자 ID |
| week_start | string | N | 주 시작일 (기본값: 이번 주) |

**Response:**
```json
{
  "week_start": "2025-03-03",
  "week_end": "2025-03-09",
  "diary_count": 5,
  "emotion_stats": {
    "joy": 2,
    "anger": 2,
    "calm": 1
  },
  "avg_intensity": 5.8,
  "report": "이번 주는 기쁨과 화남이 반반이었어요. 주 초반에는 프로젝트 완료로 기분이 좋았지만, 후반에 새로운 이슈가 터지면서 스트레스를 받았네요.",
  "patterns": [
    "야근 후 다음 날 감정 강도가 높아지는 패턴이 있어요",
    "수요일에 스트레스가 집중되는 경향이 있어요"
  ]
}
```

### GET /insight/monthly
월간 리포트를 조회한다. (구조는 weekly와 유사, 기간만 다름)

## 5. 음성 (Voice) — Phase 3

### POST /voice/transcribe
음성 파일을 텍스트로 변환한다.

**Request:** `multipart/form-data`
| 필드 | 타입 | 설명 |
|------|------|------|
| audio | file | 음성 파일 (wav, mp3, webm) |

**Response:**
```json
{
  "text": "좀 피곤했어 야근함",
  "duration_seconds": 3.2
}
```

변환된 텍스트는 `/chat/message`로 전달하여 같은 플로우를 탄다.

## 6. 에러 코드

| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 (필수 파라미터 누락 등) |
| 404 | 일기/세션을 찾을 수 없음 |
| 409 | 해당 날짜에 이미 일기가 존재함 |
| 429 | API 호출 한도 초과 (LLM) |
| 500 | 서버 내부 오류 |

**에러 응답 형식:**
```json
{
  "error": {
    "code": 404,
    "message": "해당 일기를 찾을 수 없습니다",
    "detail": "diary_id=99 not found"
  }
}
```
