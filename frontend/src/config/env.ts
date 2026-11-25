export const env = Object.freeze({
  appName: import.meta.env.VITE_APP_NAME || "Tone Neuron",
  appVersion: import.meta.env.VITE_APP_VERSION || "2.0.0",
  apiBaseUrl: (
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
  ).replace(/\/+$/, ""),
  enableMascot:
    import.meta.env.VITE_ENABLE_MASCOT === "true",
  enableScreenCapture:
    import.meta.env.VITE_ENABLE_SCREEN_CAPTURE === "true",
  enableDesktopBridge:
    import.meta.env.VITE_ENABLE_DESKTOP_BRIDGE === "true",
});