import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  AudioLines,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  User,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import api from "../../services/api";
import mascot from "../../assets/hero.png";

type AuthMode = "login" | "register";

export default function AuthPage() {
  const [searchParams] = useSearchParams();
  const initialMode =
  searchParams.get("mode") === "register" ||
  window.location.pathname === "/register"
    ? "register"
    : "login";

  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  const navigate = useNavigate();

  const updateField = (field: string, value: string) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    setLoading(true);

    try {
      if (mode === "register") {
        const response = await api.post("/api/v1/auth/register", {
          username: form.username,
          email: form.email,
          password: form.password,
        });

        sessionStorage.setItem("verification_email", form.email);

        toast.success(
          response.data.message || "Account created successfully"
        );

        navigate("/verify-email");
        return;
      }

      const response = await api.post("/api/v1/auth/login", {
        email: form.email,
        password: form.password,
      });

      sessionStorage.setItem(
        "access_token",
        response.data.access_token
      );

      sessionStorage.setItem(
        "refresh_token",
        response.data.refresh_token
      );

      toast.success("Welcome back to Tone Neuron");

      navigate("/dashboard");
    } catch (error: any) {
      const message =
        error.response?.data?.detail ||
        "Something went wrong. Please try again.";

      toast.error(
        typeof message === "string"
          ? message
          : "Please check your details and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-layout">
      <div className="auth-background"></div>

      <Link to="/" className="auth-back">
        <ArrowLeft size={17} />
        Back to home
      </Link>

      <section className="auth-container">
        <motion.div
          className="auth-visual"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="auth-brand">
            <AudioLines size={28} />
            <span>
              TONE<span>NEURON</span>
            </span>
          </div>

          <div className="auth-mascot">
            <div className="auth-orbit"></div>

            <motion.img
              src={mascot}
              alt="Neuro AI mascot"
              animate={{ y: [0, -10, 0] }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </div>

          <div className="auth-visual-text">
            <Sparkles size={18} />

            <h2>
              Your intelligence.
              <br />
              Your possibilities.
            </h2>

            <p>
              A smarter way to think, write and communicate.
              Welcome to your AI workspace.
            </p>
          </div>
        </motion.div>

        <motion.div
          className="auth-form-panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
        >
          <div className="auth-form-heading">
            <span className="auth-eyebrow">
              <ShieldCheck size={15} />
              YOUR PRIVATE AI WORKSPACE
            </span>

            <h1>
              {mode === "login" ? "Welcome back." : "Create account."}
            </h1>

            <p>
              {mode === "login"
                ? "Sign in to continue your journey."
                : "Start experiencing a smarter way to work."}
            </p>
          </div>

          <div className="auth-switch">
            <button
              className={mode === "login" ? "active" : ""}
              onClick={() => setMode("login")}
              type="button"
            >
              Sign in
            </button>

            <button
              className={mode === "register" ? "active" : ""}
              onClick={() => setMode("register")}
              type="button"
            >
              Create account
            </button>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {mode === "register" && (
              <div className="auth-field">
                <label>Username</label>

                <div className="auth-input">
                  <User size={18} />

                  <input
                    type="text"
                    placeholder="Choose a username"
                    value={form.username}
                    onChange={(e) =>
                      updateField("username", e.target.value)
                    }
                    minLength={3}
                    maxLength={50}
                    required
                  />
                </div>
              </div>
            )}

            <div className="auth-field">
              <label>Email address</label>

              <div className="auth-input">
                <Mail size={18} />

                <input
                  type="email"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={(e) =>
                    updateField("email", e.target.value)
                  }
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <label>Password</label>

              <div className="auth-input">
                <LockKeyhole size={18} />

                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={(e) =>
                    updateField("password", e.target.value)
                  }
                  minLength={8}
                  maxLength={128}
                  required
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {mode === "login" && (
              <div className="auth-options">
                <Link to="/forgot-password">
                  Forgot password?
                </Link>
              </div>
            )}

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading
                ? "Please wait..."
                : mode === "login"
                  ? "Sign in to workspace"
                  : "Create your account"}

              {!loading && <ArrowRight size={18} />}
            </button>
          </form>

          <div className="auth-security">
            <ShieldCheck size={16} />
            Your account is protected with secure authentication.
          </div>

          <div className="auth-footer">
            © 2026 Tone Neuron. All rights reserved.
          </div>
        </motion.div>
      </section>
    </main>
  );
}