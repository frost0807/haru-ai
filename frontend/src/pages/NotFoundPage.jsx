import { useNavigate } from "react-router-dom";

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="text-center">
        <p className="text-6xl mb-4">🌙</p>
        <h1 className="text-2xl font-bold text-gray-700 mb-2">페이지를 찾을 수 없어요</h1>
        <p className="text-sm text-gray-400 mb-8">주소가 잘못되었거나 삭제된 페이지예요</p>
        <button
          onClick={() => navigate("/diary")}
          className="bg-indigo-500 hover:bg-indigo-600 text-white px-6 py-2 rounded-full text-sm font-medium transition"
        >
          내 일기로 가기
        </button>
      </div>
    </div>
  );
}
