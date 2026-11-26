import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Mail, ShieldCheck, RefreshCw, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import api from "../../services/api";
import mascot from "../../assets/hero.png";

export default function VerifyEmailPage() {
  const navigate = useNavigate();
  const email = sessionStorage.getItem("verification_email") || "";

  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [countdown, setCountdown] = useState(30);
  const [verified, setVerified] = useState(false);

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (!email) {
      navigate("/register");
    }
  }, [email, navigate]);

  useEffect(() => {
    if (countdown <= 0) return;

    const timer = window.setTimeout(() => {
      setCountdown((value) => value - 1);
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [countdown]);

  const updateOtp = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);

    const updated = [...otp];
    updated[index] = digit;
    setOtp(updated);

    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (event: React.ClipboardEvent<HTMLInputElement>) => {
    event.preventDefault();

    const pasted = event.clipboardData
      .getData("text")
      .replace(/\D/g, "")
      .slice(0, 6);

    const updated = Array.from({ length: 6 }, (_, index) => pasted[index] || "");

    setOtp(updated);

    inputRefs.current[Math.min(pasted.length, 5)]?.focus();
  };

  const handleKeyDown = (
    index: number,
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (event.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = async (event: React.FormEvent) => {
    event.preventDefault();

    const code = otp.join("");

    if (code.length !== 6) {
      toast.error("Please enter all six digits.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/api/v1/auth/verify-email", {
        email,
        otp: code,
      });

      setVerified(true);
      toast.success(response.data.message || "Email verified successfully.");

      sessionStorage.removeItem("verification_email");

      window.setTimeout(() => {
        navigate("/login");
      }, 1800);
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail || "Invalid or expired verification code."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (countdown > 0 || resending) return;

    setResending(true);

    try {
      const response = await api.post("/api/v1/auth/send-otp", {
        email,
      });

      toast.success(response.data.message);
      setCountdown(30);
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail || "Unable to resend the verification code."
      );
    } finally {
      setResending(false);
    }
  };

  return (
    <main className="auth-layout">
      <div className="auth-background" />

      <Link to="/register" className="auth-back">
        <ArrowLeft size={17} />
        Back to registration
      </Link>

      <section className="auth-container">
        <motion.div
          className="auth-visual"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="auth-brand">
            <Mail size={27} />
            <span>
              TONE<span>NEURON</span>
            </span>
          </div>

          <div className="auth-mascot">
            <div className="auth-orbit" />
            <motion.img
              src={mascot}
              alt="Neuro AI mascot"
              animate={{ y: [0, -10, 0], rotate: [0, 1, 0] }}
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
              One small step.
              <br />
              A smarter journey.
            </h2>
            <p>
              Verify your email to unlock your personal AI workspace.
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
              EMAIL VERIFICATION
            </span>

            <h1>
              {verified ? "You're verified!" : "Check your inbox."}
            </h1>

            <p>
              {verified
                ? "Your account is ready. Taking you to login..."
                : "We've sent a six-digit verification code to your email address."}
            </p>
          </div>

          {verified ? (
            <motion.div
              initial={{ scale: 0.7, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="verification-success"
            >
              <CheckCircle2 size={75} />
              <h2>Email verified successfully</h2>
              <p>Your Tone Neuron journey starts here.</p>
            </motion.div>
          ) : (
            <>
              <div className="verification-email">
                <Mail size={18} />
                <span>{email}</span>
              </div>

              <form onSubmit={handleVerify} className="auth-form">
                <label className="otp-label">Enter verification code</label>

                <div className="otp-input-group">
                  {otp.map((digit, index) => (
                    <input
                      key={index}
                      ref={(element) => {
                        inputRefs.current[index] = element;
                      }}
                      value={digit}
                      onChange={(event) =>
                        updateOtp(index, event.target.value)
                      }
                      onKeyDown={(event) => handleKeyDown(index, event)}
                      onPaste={handlePaste}
                      type="text"
                      inputMode="numeric"
                      autoComplete={index === 0 ? "one-time-code" : "off"}
                      maxLength={1}
                      aria-label={`OTP digit ${index + 1}`}
                      required
                    />
                  ))}
                </div>

                <button
                  type="submit"
                  className="auth-submit"
                  disabled={loading || otp.join("").length !== 6}
                >
                  {loading ? "Verifying..." : "Verify email"}
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
            Your verification is protected by secure authentication.
          </div>

          <div className="auth-footer">
            © 2026 Tone Neuron. All rights reserved.
          </div>
        </motion.div>
      </section>
    </main>
  );
}