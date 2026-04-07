import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { askReflect } from "../api/client";
import Spinner from "../components/Spinner";

export default function ReflectPage() {
  const [items, setItems] = useState([]); // [{ question, answer, sources, loading }]
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ block: "nearest" });
    }
  }, [items]);

  const handleSubmit = async () => {
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setLoading(true);
    setItems((prev) => [...prev, { question, answer: null, sources: [] }]);

    try {
      const { data } = await askReflect(question);
      setItems((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          question,
          answer: data.answer,
          sources: data.sources,
        };
        return updated;
      });
    } catch {
      setItems((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          question,
          answer: "오류가 발생했어. 잠시 후 다시 시도해줘.",
          sources: [],
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-50 flex flex-col overflow-hidden">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-100 px-4 py-3 flex items-center gap-3">
        <button
          onClick={() => navigate("/diary")}
          className="text-gray-400 hover:text-gray-600 transition"
        >
          ←
        </button>
        <div>
          <h1 className="font-semibold text-gray-800">나와의 대화</h1>
          <p className="text-xs text-gray-400">과거 일기에 질문해봐</p>
        </div>
      </div>

      {/* 대화 영역 */}
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4 space-y-6 max-w-lg mx-auto w-full">
        {items.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full mt-24 text-center text-gray-400 gap-2">
            <span className="text-4xl">📖</span>
            <p className="text-sm">네 일기를 기억하고 있어.<br />뭐든지 물어봐!</p>
            <div className="mt-4 flex flex-col gap-2 text-xs text-gray-400">
              <span className="bg-white border border-gray-200 rounded-full px-3 py-1">지난달에 뭐가 제일 힘들었어?</span>
              <span className="bg-white border border-gray-200 rounded-full px-3 py-1">요즘 자주 느끼는 감정이 뭐야?</span>
              <span className="bg-white border border-gray-200 rounded-full px-3 py-1">최근에 기뻤던 일이 뭐야?</span>
            </div>
          </div>
        )}

        {items.map((item, i) => (
          <div key={i} className="space-y-3">
            {/* 사용자 질문 */}
            <div className="flex justify-end">
              <div className="bg-indigo-500 text-white text-sm px-4 py-2 rounded-2xl rounded-br-sm max-w-xs">
                {item.question}
              </div>
            </div>

            {/* AI 답변 */}
            <div className="flex justify-start">
              <div className="bg-white border border-gray-100 shadow-sm text-sm px-4 py-3 rounded-2xl rounded-bl-sm max-w-xs text-gray-700 leading-relaxed">
                {item.answer === null ? (
                  <Spinner size="sm" />
                ) : (
                  item.answer
                )}
              </div>
            </div>

            {/* 참고 일기 카드 */}
            {item.sources?.length > 0 && (
              <div className="ml-1">
                <p className="text-xs text-gray-400 mb-1">참고 일기</p>
                <div className="flex flex-col gap-2">
                  {item.sources.map((src) => (
                    <button
                      key={src.diary_id}
                      onClick={() => navigate(`/diary/${src.diary_id}`)}
                      className="text-left bg-gray-100 hover:bg-gray-200 rounded-xl px-3 py-2 transition"
                    >
                      <span className="text-xs font-medium text-gray-500 block">{src.diary_date}</span>
                      <span className="text-xs text-gray-600 line-clamp-1">{src.preview}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        <div ref={bottomRef} />
      </div>

      {/* 입력창 */}
      <div className="bg-white border-t border-gray-100 px-4 py-3 max-w-lg mx-auto w-full">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="궁금한 거 물어봐..."
            rows={1}
            disabled={loading}
            className="flex-1 resize-none rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:border-indigo-300 disabled:opacity-50"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !input.trim()}
            className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition disabled:opacity-40"
          >
            {loading ? <Spinner size="sm" /> : "전송"}
          </button>
        </div>
      </div>
    </div>
  );
}