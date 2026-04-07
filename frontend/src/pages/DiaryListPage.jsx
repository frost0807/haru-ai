import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getDiaries } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import EmotionBadge from "../components/EmotionBadge";
import Spinner from "../components/Spinner";

export default function DiaryListPage() {
  const [diaries, setDiaries] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { signOut } = useAuth();

  useEffect(() => {
    getDiaries()
      .then(({ data }) => {
        setDiaries(data.items);
        setTotal(data.total);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-lg mx-auto">

        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-indigo-600">내 일기</h1>
            <p className="text-sm text-gray-400 mt-1">총 {total}개의 일기</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate("/reflect")}
              className="text-indigo-400 hover:text-indigo-600 text-sm px-3 py-2 rounded-full border border-indigo-200 hover:border-indigo-400 transition"
            >
              나와의 대화
            </button>
            <button
              onClick={() => navigate("/chat")}
              className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-full text-sm font-medium transition"
            >
              + 새 일기
            </button>
            <button
              onClick={signOut}
              className="text-gray-400 hover:text-gray-600 text-sm px-2 py-2 transition"
              title="로그아웃"
            >
              로그아웃
            </button>
          </div>
        </div>

        {/* 목록 */}
        {loading ? (
          <div className="flex justify-center mt-20"><Spinner /></div>
        ) : diaries.length === 0 ? (
          <div className="text-center mt-20">
            <p className="text-gray-400 mb-4">아직 일기가 없어요</p>
            <button
              onClick={() => navigate("/chat")}
              className="bg-indigo-500 text-white px-6 py-2 rounded-full text-sm"
            >
              첫 일기 쓰기
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {diaries.map((diary) => (
              <div
                key={diary.diary_id}
                onClick={() => navigate(`/diary/${diary.diary_id}`)}
                className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 cursor-pointer hover:border-indigo-200 hover:shadow-md transition"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-500">
                    {diary.diary_date}
                  </span>
                  {diary.primary_emotion && (
                    <EmotionBadge emotion={diary.primary_emotion} />
                  )}
                </div>
                <p className="text-sm text-gray-700 leading-relaxed line-clamp-2">
                  {diary.content}
                </p>
                {diary.emotion_summary && (
                  <p className="text-xs text-gray-400 mt-2">{diary.emotion_summary}</p>
                )}
              </div>
            ))}
          </div>
        )}
        {/* 암호화 안내 */}
        <p className="text-center text-xs text-gray-300 mt-6">🔒 일기 내용은 암호화되어 저장됩니다</p>
      </div>
    </div>
  );
}