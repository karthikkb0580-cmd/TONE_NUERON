import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Mail, ShieldCheck, AudioLines } from "lucide-react";
import { toast } from "sonner";
import api from "../../services/api";
import mascot from "../../assets/hero.png";

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await api.post("/api/v1/auth/forgot-password", {
        email,
      });

      sessionStorage.setItem("reset_email", email.trim().toLowerCase());

      toast.success(response.data.message);

      navigate("/reset-password");
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail ||
        "Unable to process your request. Please try again."
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
              Every great journey
              <br />
              deserves another chance.
            </h2>
            <p>
              Let's get you back to your personal AI workspace.
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
              ACCOUNT RECOVERY
            </span>

            <h1>Forgot password?</h1>

            <p>
              Enter your registered email address. We'll send you a password
              reset code.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-field">
              <label>Email address</label>

              <div className="auth-input">
                <Mail size={18} />

                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading ? "Sending reset code..." : "Send reset code"}
              {!loading && <ArrowRight size={18} />}
            </button>
          </form>

          <div className="auth-security">
            <ShieldCheck size={16} />
            Your account recovery is protected.
          </div>

          <div className="auth-footer">
            © 2026 Tone Neuron. All rights reserved.
          </div>
        </motion.div>
      </section>
    </main>
  );
}