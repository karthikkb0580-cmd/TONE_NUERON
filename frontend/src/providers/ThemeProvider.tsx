import { useEffect } from "react";
import type { ReactNode } from "react";
import { useThemeStore } from "../store/themeStore";

interface ThemeProviderProps {
  children: ReactNode;
}

export default function ThemeProvider({
  children,
}: ThemeProviderProps) {
  const theme = useThemeStore((state) => state.theme);

  useEffect(() => {
    const media = window.matchMedia(
      "(prefers-color-scheme: dark)"
    );

    const applyTheme = () => {
      const resolvedTheme =
        theme === "system"
          ? media.matches
            ? "dark"
            : "light"
          : theme;

      document.documentElement.setAttribute(
        "data-theme",
        resolvedTheme
      );
    };

    applyTheme();

    media.addEventListener("change", applyTheme);

    return () => {
      media.removeEventListener("change", applyTheme);
    };
  }, [theme]);

  return <>{children}</>;
}