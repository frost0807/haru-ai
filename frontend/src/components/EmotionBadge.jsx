const EMOTION_STYLE = {
  // 긍정
  joy:       { label: "기쁨",   color: "bg-yellow-100 text-yellow-700" },
  proud:     { label: "뿌듯함", color: "bg-amber-100 text-amber-700" },
  excited:   { label: "설렘",   color: "bg-pink-100 text-pink-700" },
  grateful:  { label: "감사",   color: "bg-lime-100 text-lime-700" },
  relieved:  { label: "안도",   color: "bg-teal-100 text-teal-700" },
  content:   { label: "만족",   color: "bg-emerald-100 text-emerald-700" },
  // 중립
  calm:      { label: "평온",   color: "bg-sky-100 text-sky-700" },
  bored:     { label: "지루함", color: "bg-gray-100 text-gray-600" },
  nostalgic: { label: "그리움", color: "bg-violet-100 text-violet-700" },
  // 부정
  tired:      { label: "피곤",   color: "bg-slate-100 text-slate-600" },
  sadness:    { label: "슬픔",   color: "bg-blue-100 text-blue-700" },
  anger:      { label: "화남",   color: "bg-red-100 text-red-700" },
  anxiety:    { label: "불안",   color: "bg-orange-100 text-orange-700" },
  lonely:     { label: "외로움", color: "bg-indigo-100 text-indigo-700" },
  frustrated: { label: "답답함", color: "bg-rose-100 text-rose-700" },
};

export default function EmotionBadge({ emotion }) {
  const style = EMOTION_STYLE[emotion] ?? { label: emotion, color: "bg-gray-100 text-gray-600" };

  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${style.color}`}>
      {style.label}
    </span>
  );
}