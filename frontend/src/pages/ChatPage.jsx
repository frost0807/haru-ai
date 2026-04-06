import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { startChat, sendMessage, finishChat, getUserCharacter } from "../api/client";
import ChatBubble from "../components/ChatBubble";
import Spinner from "../components/Spinner";

export default function ChatPage() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | in_progress | ready_to_finish | finishing
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const [character, setCharacter] = useState(null); // { id, name, emoji, description }
  const [charLoading, setCharLoading] = useState(true);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  // DB에서 저장된 캐릭터 불러오기 (없으면 선택 페이지로)
  useEffect(() => {
    getUserCharacter()
      .then(({ data }) => setCharacter(data))
      .catch(() => navigate("/select-character", { replace: true }))
      .finally(() => setCharLoading(false));
  }, [navigate]);

  // 새 메시지 추가 시 자동 스크롤
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // AI 응답 완료 후 입력창 포커스
  useEffect(() => {
    if (!loading && status === "in_progress" || !loading && status === "ready_to_finish") {
      inputRef.current?.focus();
    }
  }, [loading, status]);

  if (charLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Spinner size="md" />
      </div>
    );
  }

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await startChat(null, character?.id ?? "haru");
      setSessionId(data.session_id);
      setMessages([{ role: "model", content: data.message }]);
      setStatus("in_progress");
    } catch (e) {
      if (e.response?.status === 409) {
        const diaryId = e.response.data.detail?.diary_id;
        navigate(`/diary/${diaryId}`);
      } else {
        setError("시작 중 오류가 발생했습니다. 다시 시도해주세요.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);
    setLastMessage(userMessage);
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const { data } = await sendMessage(sessionId, userMessage);
      setMessages((prev) => [...prev, { role: "model", content: data.message }]);
      // ready_to_finish 이후엔 다시 in_progress로 돌아가지 않음
      setStatus((prev) => prev === "ready_to_finish" ? "ready_to_finish" : data.status);
    } catch (e) {
      const msg = e.response?.data?.detail ?? "AI 응답 중 오류가 발생했습니다.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleFinish = async () => {
    setStatus("finishing");
    setLoading(true);
    try {
      const { data } = await finishChat(sessionId);
      navigate(`/diary/${data.diary_id}`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-8 px-4">
      <div className="w-full max-w-lg flex flex-col" style={{ height: "90vh" }}>

        {/* 헤더 */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-indigo-600">하루AI</h1>
          {character ? (
            <div className="flex items-center justify-center gap-1 mt-1">
              <span className="text-sm text-gray-500">
                {character.emoji} {character.name}와 이야기 중
              </span>
              {status === "idle" && (
                <button
                  onClick={() => navigate("/select-character")}
                  className="text-xs text-indigo-400 hover:text-indigo-600 underline ml-1"
                >
                  바꾸기
                </button>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-400 mt-1">오늘 하루를 이야기해요</p>
          )}
        </div>

        {/* 채팅 영역 */}
        <div className="flex-1 bg-gray-100 rounded-2xl p-4 overflow-y-auto">
          {status === "idle" ? (
            <div className="h-full flex flex-col items-center justify-center gap-4">
              <p className="text-gray-400 text-sm">오늘 하루 어땠나요?</p>
              <button
                onClick={handleStart}
                disabled={loading}
                className="bg-indigo-500 hover:bg-indigo-600 text-white px-6 py-3 rounded-full font-medium transition disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? <><Spinner size="sm" /><span>연결 중...</span></> : "일기 시작하기"}
              </button>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <ChatBubble key={i} role={msg.role} message={msg.content} />
              ))}
              {error && (
                <div className="flex justify-center mb-3">
                  <div className="bg-red-50 border border-red-200 px-4 py-2 rounded-2xl text-sm text-red-500 flex items-center gap-3">
                    <span>{error}</span>
                    <button
                      onClick={() => {
                        setInput(lastMessage);
                        setError(null);
                        setMessages((prev) => prev.slice(0, -1)); // 실패한 메시지 제거
                      }}
                      className="text-xs text-red-600 underline font-medium whitespace-nowrap"
                    >
                      다시 시도
                    </button>
                  </div>
                </div>
              )}
              {loading && (
                <div className="flex justify-start mb-3">
                  <div className="bg-white border border-gray-200 px-4 py-2 rounded-2xl flex items-center gap-2">
                    <Spinner size="sm" />
                    <span className="text-gray-400 text-sm">입력 중...</span>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </>
          )}
        </div>

        {/* 입력 영역 */}
        {status !== "idle" && (
          <div className="mt-4 flex flex-col gap-2">
            {status === "ready_to_finish" || status === "finishing" ? (
              <button
                onClick={handleFinish}
                disabled={loading}
                className="w-full bg-emerald-500 hover:bg-emerald-600 text-white py-2 rounded-xl font-medium transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? <><Spinner size="sm" /><span>일기 쓰는 중...</span></> : "일기 쓰기 ✍️"}
              </button>
            ) : (
              <div className="flex gap-2">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="메시지를 입력하세요..."
                  rows={2}
                  disabled={loading}
                  className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 disabled:opacity-50"
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 rounded-xl transition disabled:opacity-50 flex items-center justify-center w-16"
                >
                  {loading ? <Spinner size="sm" /> : "전송"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}