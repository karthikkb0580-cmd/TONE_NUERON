import { Sun, Moon, Monitor } from "lucide-react";
import { useThemeStore } from "../../store/themeStore";
import type { Theme } from "../../store/themeStore";
import { cn } from "../../utils/cn";

const themes = [
  { value: "light", icon: Sun, label: "Light" },
  { value: "dark", icon: Moon, label: "Dark" },
  { value: "system", icon: Monitor, label: "System" },
] as const;

export default function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();

  return (
    <div className="inline-flex gap-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-1">
      {themes.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          type="button"
          title={label}
          aria-label={`${label} theme`}
          aria-pressed={theme === value}
          onClick={() => setTheme(value as Theme)}
          className={cn(
            "flex h-10 w-10 items-center justify-center rounded-lg transition-colors",
            theme === value
              ? "bg-[var(--primary)] text-white"
              : "text-[var(--muted)] hover:bg-[var(--surface-hover)]"
          )}
        >
          <Icon size={18} />
        </button>
      ))}
    </div>
  );
}