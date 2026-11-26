import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowDown,
  ArrowRight,
  AudioLines,
  BrainCircuit,
  ShieldCheck,
  Sparkles,
  Zap,
  Menu,
  X,
  MessageSquareText,
  WandSparkles,
  Globe2,
} from "lucide-react";
import { useState } from "react";
import mascot from "../assets/hero.png";
import "../App.css";

const features = [
  {
    icon: BrainCircuit,
    number: "01",
    title: "Intelligent Communication",
    description:
      "Understand context, analyze conversations and communicate with greater clarity using intelligent AI.",
  },
  {
    icon: WandSparkles,
    number: "02",
    title: "Writing Intelligence",
    description:
      "Rewrite, refine, summarize and transform your writing while preserving your unique voice.",
  },
  {
    icon: ShieldCheck,
    number: "03",
    title: "Privacy First",
    description:
      "Your workspace, your data and your permissions. Built with security at its foundation.",
  },
  {
    icon: Globe2,
    number: "04",
    title: "Global Communication",
    description:
      "Break language barriers and communicate naturally across different languages.",
  },
];

const capabilities = [
  "Tone analysis",
  "Sentiment detection",
  "Grammar correction",
  "AI rewriting",
  "Smart summarization",
  "Emotion recognition",
];

function Reveal({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) {
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      initial={reducedMotion ? false : { opacity: 0, y: 35 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <main className="site-shell">
      <nav className="navbar">
        <a href="#" className="brand" onClick={closeMenu}>
          <span className="brand-icon">
            <AudioLines size={25} />
          </span>
          <span>
            TONE<span className="brand-accent">NEURON</span>
            <small>INTELLIGENCE, REIMAGINED</small>
          </span>
        </a>

        <div className={`nav-links ${menuOpen ? "nav-open" : ""}`}>
          <a href="#home" onClick={closeMenu}>Home</a>
          <a href="#features" onClick={closeMenu}>Features</a>
          <a href="#intelligence" onClick={closeMenu}>Technology</a>
          <a href="#about" onClick={closeMenu}>About</a>
          <a href="#access" className="mobile-signin" onClick={closeMenu}>
            Get started <ArrowRight size={16} />
          </a>
        </div>

        <div className="nav-actions">
          <a href="#access" className="signin-link">Sign in</a>
          <a href="#access" className="nav-cta">
            Get started <ArrowRight size={15} />
          </a>
        </div>

        <button
          className="mobile-menu"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation"
        >
          {menuOpen ? <X /> : <Menu />}
        </button>
      </nav>

      <section className="hero-section" id="home">
        <div className="hero-grid"></div>
        <div className="hero-glow hero-glow-one"></div>
        <div className="hero-glow hero-glow-two"></div>

        <div className="hero-content">
          <motion.div
            className="hero-copy"
            initial={{ opacity: 0, x: -35 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, ease: "easeOut" }}
          >
            <div className="eyebrow">
              <span className="status-dot"></span>
              THE NEXT GENERATION OF AI
            </div>

            <h1>
              Intelligence
              <br />
              behind every
              <br />
              <span className="gradient-text">conversation.</span>
            </h1>

            <p className="hero-description">
              Think clearly. Communicate intelligently.
              Create without limits. Meet your personal
              AI-powered communication workspace.
            </p>

            <div className="hero-buttons">
              <a href="#access" className="primary-button">
                Enter Tone Neuron
                <ArrowRight size={18} />
              </a>

              <a href="#features" className="secondary-button">
                Discover more
                <ArrowDown size={17} />
              </a>
            </div>

            <div className="hero-trust">
              <ShieldCheck size={17} />
              <span>Built around privacy, intelligence and control</span>
            </div>
          </motion.div>

          <motion.div
            className="mascot-stage"
            initial={{ opacity: 0, x: 45 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1.2, delay: 0.2 }}
          >
            <div className="mascot-orbit orbit-one"></div>
            <div className="mascot-orbit orbit-two"></div>
            <div className="mascot-platform"></div>

            <motion.div
              className="mascot-image-wrapper"
              animate={{ y: [0, -12, 0] }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              <img
                src={mascot}
                alt="Neuro, the Tone Neuron AI mascot"
                className="mascot-image"
              />
            </motion.div>

            <motion.div
              className="floating-card floating-card-top"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 4, repeat: Infinity }}
            >
              <span className="floating-icon">
                <Sparkles size={17} />
              </span>
              <div>
                <strong>Neural intelligence</strong>
                <small>Always evolving</small>
              </div>
            </motion.div>

            <motion.div
              className="floating-card floating-card-bottom"
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 5, repeat: Infinity }}
            >
              <span className="floating-icon red-icon">
                <BrainCircuit size={18} />
              </span>
              <div>
                <strong>Context understood</strong>
                <small>AI processing ready</small>
              </div>
              <span className="online-indicator"></span>
            </motion.div>

            <div className="mascot-caption">
              <span>MEET YOUR AI COMPANION</span>
              <h3>Hey, I'm Neuro.</h3>
              <p>Let's make every interaction smarter.</p>
            </div>
          </motion.div>
        </div>

        <a href="#features" className="scroll-indicator">
          <span>SCROLL TO EXPLORE</span>
          <ArrowDown size={16} />
        </a>

        <div className="hero-index">01 / 04</div>
      </section>

      <section className="intro-section" id="about">
        <Reveal>
          <div className="section-label">
            <span>01</span> A DIFFERENT KIND OF INTELLIGENCE
          </div>

          <h2>
            Not just another AI tool.
            <br />
            <span className="muted-heading">
              Your intelligent workspace.
            </span>
          </h2>

          <p className="intro-description">
            Tone Neuron brings communication intelligence,
            writing assistance and personalized AI experiences
            together in one unified environment.
          </p>
        </Reveal>

        <div className="intro-stats">
          <Reveal delay={0.1}>
            <div className="stat-item">
              <Sparkles />
              <strong>AI</strong>
              <span>Intelligence at the core</span>
            </div>
          </Reveal>

          <Reveal delay={0.2}>
            <div className="stat-item">
              <Zap />
              <strong>Smart</strong>
              <span>Faster workflows</span>
            </div>
          </Reveal>

          <Reveal delay={0.3}>
            <div className="stat-item">
              <ShieldCheck />
              <strong>Secure</strong>
              <span>Privacy-focused design</span>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="features-section" id="features">
        <div className="section-heading">
          <Reveal>
            <div className="section-label">
              <span>02</span> WHAT MAKES US DIFFERENT
            </div>
            <h2>
              Intelligence that
              <br />
              <span className="gradient-text">works with you.</span>
            </h2>
          </Reveal>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => {
            const Icon = feature.icon;

            return (
              <Reveal key={feature.number} delay={index * 0.1}>
                <article className="feature-card">
                  <div className="feature-top">
                    <div className="feature-icon">
                      <Icon size={25} />
                    </div>
                    <span>{feature.number}</span>
                  </div>

                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>

                  <div className="feature-bottom">
                    <span>EXPLORE CAPABILITY</span>
                    <ArrowRight size={17} />
                  </div>
                </article>
              </Reveal>
            );
          })}
        </div>
      </section>

      <section className="intelligence-section" id="intelligence">
        <div className="intelligence-glow"></div>

        <Reveal>
          <div className="intelligence-copy">
            <div className="section-label">
              <span>03</span> ONE INTELLIGENT ECOSYSTEM
            </div>

            <h2>
              Every tool.
              <br />
              One <span className="gradient-text">intelligence.</span>
            </h2>

            <p>
              From understanding emotions to refining your writing,
              Tone Neuron gives you the tools to communicate better.
            </p>

            <div className="capability-list">
              {capabilities.map((capability) => (
                <div className="capability-item" key={capability}>
                  <Sparkles size={15} />
                  {capability}
                </div>
              ))}
            </div>
          </div>
        </Reveal>

        <Reveal delay={0.2}>
          <div className="intelligence-visual">
            <div className="visual-ring ring-one"></div>
            <div className="visual-ring ring-two"></div>

            <div className="intelligence-core">
              <AudioLines size={55} />
              <span>TONE NEURON</span>
              <small>INTELLIGENCE CORE</small>
            </div>

            <div className="visual-node node-one">
              <MessageSquareText />
            </div>
            <div className="visual-node node-two">
              <BrainCircuit />
            </div>
            <div className="visual-node node-three">
              <WandSparkles />
            </div>
            <div className="visual-node node-four">
              <Globe2 />
            </div>
          </div>
        </Reveal>
      </section>

      <section className="access-section" id="access">
        <Reveal>
          <div className="access-card">
            <div className="access-glow"></div>

            <div className="section-label">
              <span>04</span> YOUR NEXT CHAPTER STARTS HERE
            </div>

            <h2>
              Think beyond
              <br />
              <span className="gradient-text">the ordinary.</span>
            </h2>

            <p>
              Step into a smarter way of communicating,
              creating and thinking.
            </p>

            <a href="/login" className="primary-button">
              Access your workspace
              <ArrowRight size={18} />
            </a>

            <span className="access-note">
              PERSONALIZED AI. ONE PRIVATE WORKSPACE.
            </span>
          </div>
        </Reveal>
      </section>

      <footer className="footer">
        <a href="#" className="brand">
          <span className="brand-icon">
            <AudioLines size={22} />
          </span>
          <span>
            TONE<span className="brand-accent">NEURON</span>
            <small>INTELLIGENCE, REIMAGINED</small>
          </span>
        </a>

        <p>Designed for a more intelligent tomorrow.</p>

        <span>© 2026 Tone Neuron</span>
      </footer>
    </main>
  );
}