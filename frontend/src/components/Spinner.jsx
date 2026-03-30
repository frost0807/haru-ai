export default function Spinner({ size = "md" }) {
  const sizeClass = size === "sm" ? "w-4 h-4 border-2" : "w-8 h-8 border-4";

  return (
    <div
      className={`${sizeClass} border-indigo-300 border-t-indigo-600 rounded-full animate-spin`}
    />
  );
}