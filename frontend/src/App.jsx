import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ChatPage from "./pages/ChatPage";
import DiaryListPage from "./pages/DiaryListPage";
import DiaryDetailPage from "./pages/DiaryDetailPage";
import CharacterSelectPage from "./pages/CharacterSelectPage";
import NotFoundPage from "./pages/NotFoundPage";
import ErrorBoundary from "./components/ErrorBoundary";

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/diary" replace />} />
          <Route path="/select-character" element={<CharacterSelectPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/diary" element={<DiaryListPage />} />
          <Route path="/diary/:id" element={<DiaryDetailPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}