import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
});

// 임시 사용자 ID (Phase 2에서 인증으로 교체)
const USER_ID = "user_001";

// 채팅
export const getCharacters = () =>
  api.get("/chat/characters");

export const startChat = (diaryDate, characterId) =>
  api.post("/chat/start", { user_id: USER_ID, diary_date: diaryDate, character_id: characterId });

export const sendMessage = (sessionId, message) =>
  api.post("/chat/message", { session_id: sessionId, message });

export const finishChat = (sessionId) =>
  api.post("/chat/finish", { session_id: sessionId });

// 일기
export const getDiaries = (params) =>
  api.get("/diary", { params: { user_id: USER_ID, ...params } });

export const getDiary = (diaryId) =>
  api.get(`/diary/${diaryId}`);

export const deleteDiary = (diaryId) =>
  api.delete(`/diary/${diaryId}`);

// 사용자 캐릭터 설정
export const getUserCharacter = () =>
  api.get(`/users/${USER_ID}/character`);

export const updateUserCharacter = (characterId) =>
  api.put(`/users/${USER_ID}/character`, { character_id: characterId });