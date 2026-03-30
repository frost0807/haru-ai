import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getCharacters, getUserCharacter, updateUserCharacter } from "../api/client";
import Spinner from "../components/Spinner";

export default function CharacterSelectPage() {
  const [characters, setCharacters] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // 캐릭터 목록 + 기존 저장된 선택 동시 로드
    Promise.all([getCharacters(), getUserCharacter().catch(() => null)])
      .then(([{ data: chars }, savedRes]) => {
        setCharacters(chars);
        if (savedRes) setSelected(savedRes.data.id);
        else setSelected(chars[0]?.id ?? null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleConfirm = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      await updateUserCharacter(selected);
      navigate("/chat");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const selectedChar = characters.find((c) => c.id === selected);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">

        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-indigo-600 mb-1">하루AI</h1>
          <p className="text-gray-500 text-sm">오늘 하루를 같이 들어줄 친구를 골라봐요</p>
        </div>

        {/* 캐릭터 목록 */}
        <div className="flex flex-col gap-3 mb-8">
          {characters.map((char) => (
            <button
              key={char.id}
              onClick={() => setSelected(char.id)}
              className={`w-full flex items-center gap-4 p-4 rounded-2xl border-2 transition text-left ${
                selected === char.id
                  ? "border-indigo-400 bg-indigo-50 shadow-sm"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <span className="text-3xl">{char.emoji}</span>
              <div>
                <p className={`font-semibold ${selected === char.id ? "text-indigo-600" : "text-gray-700"}`}>
                  {char.name}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">{char.description}</p>
              </div>
              {selected === char.id && (
                <span className="ml-auto text-indigo-400 text-lg">✓</span>
              )}
            </button>
          ))}
        </div>

        {/* 확인 버튼 */}
        <button
          onClick={handleConfirm}
          disabled={!selected || saving}
          className="w-full bg-indigo-500 hover:bg-indigo-600 text-white py-3 rounded-xl font-medium transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {saving
            ? <><Spinner size="sm" /><span>저장 중...</span></>
            : selectedChar ? `${selectedChar.emoji} ${selectedChar.name}와 일기 쓰기` : "선택해주세요"}
        </button>

        {/* 나중에 바꾸기 안내 */}
        <p className="text-center text-xs text-gray-400 mt-4">
          언제든지 새 일기를 시작할 때 바꿀 수 있어요
        </p>
      </div>
    </div>
  );
}