import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/auth/AuthPage";
import VerifyEmailPage from "./pages/auth/VerifyEmailPage";
import ForgotPasswordPage from "./pages/auth/ForgotPasswordPage";
import ResetPasswordPage from "./pages/auth/ResetPasswordPage";

function DashboardPlaceholder() {
  return (
    <main className="site-shell min-h-screen grid place-items-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">
          Welcome to Tone Neuron
        </h1>
        <p className="mt-4 text-gray-400">
          Your private workspace is coming next.
        </p>
      </div>
    </main>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" theme="dark" />

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/register" element={<AuthPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/dashboard" element={<DashboardPlaceholder />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
      </Routes>
    </BrowserRouter>
  );
}