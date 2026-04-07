import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
});

// 로그인한 사용자 ID (AuthContext에서 setUserId로 주입)
let _userId = null;
export const setUserId = (id) => { _userId = id; };
export const getUserId = () => _userId;

// 채팅
export const getCharacters = () =>
  api.get("/chat/characters");

export const startChat = (diaryDate, characterId) =>
  api.post("/chat/start", {
    user_id: _userId,
    diary_date: diaryDate,
    character_id: characterId,
    current_hour: new Date().getHours(),  // 0~23, 시간대 인식용
  });

export const sendMessage = (sessionId, message) =>
  api.post("/chat/message", { session_id: sessionId, message });

export const finishChat = (sessionId) =>
  api.post("/chat/finish", { session_id: sessionId });

// 일기
export const getDiaries = (params) =>
  api.get("/diary", { params: { user_id: _userId, ...params } });

export const getDiary = (diaryId) =>
  api.get(`/diary/${diaryId}`);

export const deleteDiary = (diaryId) =>
  api.delete(`/diary/${diaryId}`);

// 나와의 대화
export const askReflect = (question) =>
  api.post("/reflect/ask", { user_id: _userId, question });

// 사용자 캐릭터 설정
export const getUserCharacter = () =>
  api.get(`/users/${_userId}/character`);

export const updateUserCharacter = (characterId) =>
  api.put(`/users/${_userId}/character`, { character_id: characterId });