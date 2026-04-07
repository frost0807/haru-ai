import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import ChatPage from "./pages/ChatPage";
import DiaryListPage from "./pages/DiaryListPage";
import DiaryDetailPage from "./pages/DiaryDetailPage";
import CharacterSelectPage from "./pages/CharacterSelectPage";
import LoginPage from "./pages/LoginPage";
import ReflectPage from "./pages/ReflectPage";
import NotFoundPage from "./pages/NotFoundPage";
import ErrorBoundary from "./components/ErrorBoundary";

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* 공개 라우트 */}
            <Route path="/login" element={<LoginPage />} />

            {/* 보호된 라우트 */}
            <Route path="/" element={<Navigate to="/diary" replace />} />
            <Route path="/select-character" element={<ProtectedRoute><CharacterSelectPage /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
            <Route path="/diary" element={<ProtectedRoute><DiaryListPage /></ProtectedRoute>} />
            <Route path="/diary/:id" element={<ProtectedRoute><DiaryDetailPage /></ProtectedRoute>} />
            <Route path="/reflect" element={<ProtectedRoute><ReflectPage /></ProtectedRoute>} />

            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}