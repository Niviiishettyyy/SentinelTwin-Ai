/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0B1220",
        surface: "#121A2B",
        raised: "#172136",
        border: "#1E2A44",
        ink: "#E6EAF2",
        muted: "#8A96AC",
        accent: "#38BDF8",
        success: "#34D399",
        warning: "#F59E0B",
        critical: "#F43F5E",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.03)",
      },
    },
  },
  plugins: [],
};
