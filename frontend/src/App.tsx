import { motion } from "framer-motion";
import {
  AudioLines,
  Sparkles,
  ShieldCheck,
  Globe,
} from "lucide-react";
import { toast } from "sonner";
import {
  Button,
  Card,
  Input,
  Badge,
  Spinner,
  ThemeToggle,
} from "./components/ui";

export default function App() {
  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-[var(--border)] px-6 py-5 md:px-12">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--primary)] text-white">
            <AudioLines size={24} />
          </div>

          <div>
            <h1 className="text-xl font-bold">
              Tone Neuron
            </h1>

            <p className="text-xs text-[var(--muted)]">
              Version 2.0
            </p>
          </div>
        </div>

        <ThemeToggle />
      </header>

      <div className="mx-auto max-w-6xl px-6 py-16">
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <Badge>Design System 2.0</Badge>

          <h2 className="mt-5 text-4xl font-bold md:text-6xl">
            Intelligence Behind
            <br />
            <span className="text-[var(--primary)]">
              Every Conversation.
            </span>
          </h2>

          <p className="mt-5 max-w-xl text-[var(--muted)]">
            A unified design foundation for the next
            generation of intelligent communication.
          </p>
        </motion.section>

        <div className="grid gap-5 md:grid-cols-3">
          {[
            {
              icon: Sparkles,
              title: "AI Intelligence",
              description: "Context-aware communication tools.",
            },
            {
              icon: ShieldCheck,
              title: "Privacy First",
              description: "User-controlled permissions and data.",
            },
            {
              icon: Globe,
              title: "Global Communication",
              description: "Multilingual communication experiences.",
            },
          ].map(({ icon: Icon, title, description }) => (
            <Card key={title} hoverable>
              <Icon
                size={30}
                className="mb-5 text-[var(--primary)]"
              />

              <h3 className="text-lg font-semibold">
                {title}
              </h3>

              <p className="mt-2 text-sm text-[var(--muted)]">
                {description}
              </p>
            </Card>
          ))}
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <Card>
            <h3 className="mb-5 text-lg font-semibold">
              Buttons
            </h3>

            <div className="flex flex-wrap gap-3">
              <Button
                onClick={() =>
                  toast.success("Button is working")
                }
              >
                Primary
              </Button>

              <Button variant="secondary">
                Secondary
              </Button>

              <Button variant="outline">
                Outline
              </Button>

              <Button variant="ghost">
                Ghost
              </Button>

              <Button variant="danger">
                Danger
              </Button>

              <Button loading>
                Processing
              </Button>
            </div>
          </Card>

          <Card>
            <h3 className="mb-5 text-lg font-semibold">
              Form Components
            </h3>

            <div className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                placeholder="Enter your email"
              />

              <Input
                label="Password"
                type="password"
                placeholder="Enter your password"
              />
            </div>
          </Card>

          <Card>
            <h3 className="mb-5 text-lg font-semibold">
              Status Indicators
            </h3>

            <div className="flex flex-wrap gap-3">
              <Badge>Default</Badge>
              <Badge variant="success">Success</Badge>
              <Badge variant="warning">Warning</Badge>
              <Badge variant="danger">Error</Badge>
              <Badge variant="info">Information</Badge>
            </div>
          </Card>

          <Card>
            <h3 className="mb-5 text-lg font-semibold">
              Loading State
            </h3>

            <Spinner label="Loading preview" />
          </Card>
        </div>
      </div>
    </main>
  );
}