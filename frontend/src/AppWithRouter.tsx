import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import App from './App';  // Existing dashboard app

export default function AppWithRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page - NEW */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Dashboard - EXISTING (unchanged) */}
        <Route path="/dashboard" element={<App />} />
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
