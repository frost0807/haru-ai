export default function ChatBubble({ role, message }) {
  const isAI = role === "model" || role === "assistant";

  return (
    <div className={`flex ${isAI ? "justify-start" : "justify-end"} mb-3`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm leading-relaxed ${
          isAI
            ? "bg-white text-gray-800 border border-gray-200"
            : "bg-indigo-500 text-white"
        }`}
      >
        {message}
      </div>
    </div>
  );
}