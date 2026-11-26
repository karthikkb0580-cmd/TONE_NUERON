import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  ShieldCheck,
  AudioLines,
  RefreshCw,
} from "lucide-react";
import { toast } from "sonner";
import api from "../../services/api";
import mascot from "../../assets/hero.png";

export default function ResetPasswordPage() {
  const navigate = useNavigate();

  const email = sessionStorage.getItem("reset_email") || "";

  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [countdown, setCountdown] = useState(30);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!email) {
      navigate("/forgot-password");
    }
  }, [email, navigate]);

  useEffect(() => {
    if (countdown <= 0) return;

    const timer = window.setTimeout(() => {
      setCountdown((value) => value - 1);
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [countdown]);

  const handleResend = async () => {
    if (countdown > 0 || resending) return;

    setResending(true);

    try {
      const response = await api.post("/api/v1/auth/forgot-password", {
        email,
      });

      toast.success(response.data.message);
      setCountdown(30);
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail ||
        "Unable to resend the reset code."
      );
    } finally {
      setResending(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!/^\d{6}$/.test(otp)) {
      toast.error("Enter a valid six-digit code.");
      return;
    }

    if (password.length < 8) {
      toast.error("Password must contain at least eight characters.");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/api/v1/auth/reset-password", {
        email,
        otp,
        new_password: password,
      });

      sessionStorage.removeItem("reset_email");

      sessionStorage.removeItem("access_token");
      sessionStorage.removeItem("refresh_token");

      setSuccess(true);
      toast.success(response.data.message);

      window.setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail ||
        "Unable to reset your password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-layout">
      <div className="auth-background" />

      <Link to="/login" className="auth-back">
        <ArrowLeft size={17} />
        Back to login
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
            <span>TONE<span>NEURON</span></span>
          </div>

          <div className="auth-mascot">
            <div className="auth-orbit" />

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
            <ShieldCheck size={20} />
            <h2>
              A fresh start.
              <br />
              A stronger password.
            </h2>
            <p>
              Secure your account and continue creating with Tone Neuron.
            </p>
          </div>
        </motion.div>

        <motion.div
          className="auth-form-panel"
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <div className="auth-form-heading">
            <span className="auth-eyebrow">
              <ShieldCheck size={15} />
              PASSWORD RECOVERY
            </span>

            <h1>
              {success ? "Password updated!" : "Create new password."}
            </h1>

            <p>
              {success
                ? "Your password has been updated. Redirecting to login..."
                : "Enter your email verification code and choose a new password."}
            </p>
          </div>

          {success ? (
            <div className="verification-success">
              <ShieldCheck size={70} />
              <h2>Password changed successfully</h2>
              <p>You can now sign in using your new password.</p>
            </div>
          ) : (
            <>
              <div className="verification-email">
                <LockKeyhole size={18} />
                <span>{email}</span>
              </div>

              <form onSubmit={handleSubmit} className="auth-form">
                <div className="auth-field">
                  <label>Six-digit reset code</label>

                  <div className="auth-input">
                    <LockKeyhole size={18} />

                    <input
                      type="text"
                      inputMode="numeric"
                      placeholder="Enter OTP"
                      value={otp}
                      onChange={(event) =>
                        setOtp(
                          event.target.value.replace(/\D/g, "").slice(0, 6)
                        )
                      }
                      maxLength={6}
                      required
                    />
                  </div>
                </div>

                <div className="auth-field">
                  <label>New password</label>

                  <div className="auth-input">
                    <LockKeyhole size={18} />

                    <input
                      type={showPassword ? "text" : "password"}
                      placeholder="Minimum 8 characters"
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
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

                <div className="auth-field">
                  <label>Confirm new password</label>

                  <div className="auth-input">
                    <LockKeyhole size={18} />

                    <input
                      type="password"
                      placeholder="Re-enter your password"
                      value={confirmPassword}
                      onChange={(event) =>
                        setConfirmPassword(event.target.value)
                      }
                      minLength={8}
                      maxLength={128}
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="auth-submit"
                  disabled={loading}
                >
                  {loading ? "Updating password..." : "Update password"}
                  {!loading && <ArrowRight size={18} />}
                </button>
              </form>

              <div className="otp-resend">
                <span>Didn't receive the code?</span>

                <button
                  type="button"
                  onClick={handleResend}
                  disabled={countdown > 0 || resending}
                >
                  <RefreshCw size={14} />

                  {resending
                    ? "Sending..."
                    : countdown > 0
                      ? `Resend in ${countdown}s`
                      : "Resend code"}
                </button>
              </div>
            </>
          )}

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