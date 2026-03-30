import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getDiary, deleteDiary } from "../api/client";
import EmotionBadge from "../components/EmotionBadge";
import ChatBubble from "../components/ChatBubble";
import Spinner from "../components/Spinner";

export default function DiaryDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [diary, setDiary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showConversation, setShowConversation] = useState(false);

  useEffect(() => {
    getDiary(id)
      .then(({ data }) => setDiary(data))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!confirm("일기를 삭제할까요?")) return;
    await deleteDiary(id);
    navigate("/diary");
  };

  if (loading) return <div className="flex justify-center mt-20"><Spinner /></div>;
  if (!diary) return <p className="text-center mt-20 text-gray-400">일기를 찾을 수 없어요</p>;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-lg mx-auto">

        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate("/diary")}
            className="text-gray-400 hover:text-gray-600 text-sm transition"
          >
            ← 목록
          </button>
          <button
            onClick={handleDelete}
            className="text-red-400 hover:text-red-600 text-sm transition"
          >
            삭제
          </button>
        </div>

        {/* 날짜 + 감정 */}
        <div className="flex items-center gap-3 mb-4">
          <span className="text-lg font-bold text-gray-700">{diary.diary_date}</span>
          {diary.emotion?.primary_emotion && (
            <EmotionBadge emotion={diary.emotion.primary_emotion} />
          )}
          {diary.emotion?.secondary_emotion && (
            <EmotionBadge emotion={diary.emotion.secondary_emotion} />
          )}
        </div>

        {/* 일기 본문 */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 mb-4">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {diary.content}
          </p>
        </div>

        {/* 감정 분석 */}
        {diary.emotion && (
          <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-4">
            <h3 className="text-sm font-semibold text-gray-500 mb-3">감정 분석</h3>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs text-gray-400">강도</span>
              <div className="flex-1 bg-gray-100 rounded-full h-2">
                <div
                  className="bg-indigo-400 h-2 rounded-full"
                  style={{ width: `${(diary.emotion.intensity / 10) * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-500">{diary.emotion.intensity}/10</span>
            </div>
            {diary.emotion.keywords?.length > 0 && (
              <div className="flex gap-1 flex-wrap mt-2">
                {diary.emotion.keywords.map((kw) => (
                  <span key={kw} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                    {kw}
                  </span>
                ))}
              </div>
            )}
            {diary.emotion.summary && (
              <p className="text-xs text-gray-400 mt-2">{diary.emotion.summary}</p>
            )}
          </div>
        )}

        {/* 대화 내역 (접기/펼치기) */}
        {diary.conversation?.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
            <button
              onClick={() => setShowConversation((prev) => !prev)}
              className="w-full text-left px-4 py-3 text-sm font-semibold text-gray-500 flex justify-between items-center"
            >
              대화 내역
              <span className="text-gray-300">{showConversation ? "▲" : "▼"}</span>
            </button>
            {showConversation && (
              <div className="px-4 pb-4">
                {diary.conversation.map((msg, i) => (
                  <ChatBubble key={i} role={msg.role} message={msg.message} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}