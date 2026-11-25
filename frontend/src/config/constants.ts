export const APP_NAME = "Tone Neuron";

export const APP_TAGLINE =
  "Intelligence Behind Every Conversation";

export const APP_VERSION = "2.0.0";

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  VERIFY_EMAIL: "/verify-email",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",
  DASHBOARD: "/dashboard",
  ANALYZE: "/dashboard/analyze",
  REWRITE: "/dashboard/rewrite",
  TRANSLATE: "/dashboard/translate",
  CONVERSATIONS: "/dashboard/conversations",
  COACH: "/dashboard/coach",
  CULTURAL_INSIGHTS: "/dashboard/cultural-insights",
  ANALYTICS: "/dashboard/analytics",
  MASCOT: "/dashboard/mascot",
  SCREEN_INTELLIGENCE: "/dashboard/screen",
  DESKTOP_BRIDGE: "/dashboard/desktop",
  SETTINGS: "/dashboard/settings",
  PRIVACY: "/dashboard/privacy",
} as const;

export const STORAGE_KEYS = {
  THEME: "tone-neuron-theme",
  LANGUAGE: "tone-neuron-language",
  PREFERENCES: "tone-neuron-preferences",
} as const;

export const SCREEN_CONFIG = {
  CAPTURE_INTERVAL_MS: 3000,
  MAX_FRAME_WIDTH: 1280,
  MAX_FRAME_HEIGHT: 720,
} as const;