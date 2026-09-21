/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef7f6",
          100: "#d3ece8",
          200: "#a7d9d1",
          300: "#79c3b7",
          400: "#4ba898",
          500: "#2f8b7c",
          600: "#1f6f63",
          700: "#195a51",
          800: "#154841",
          900: "#123b36",
        },
        accent: {
          50: "#fff4ed",
          100: "#ffe4d1",
          200: "#ffc6a3",
          300: "#ffa066",
          400: "#fb7a35",
          500: "#f2590f",
          600: "#d8420a",
          700: "#b2310c",
          800: "#8f2810",
          900: "#752411",
        },
        ink: {
          50: "#f5f7f8",
          100: "#e8ecee",
          200: "#cfd8dc",
          300: "#a9b8bf",
          400: "#7c919b",
          500: "#5e7580",
          600: "#4a5e69",
          700: "#3e4e57",
          800: "#37444b",
          900: "#1c2429",
        },
      },
      fontFamily: {
        sans: ["'Inter'", "system-ui", "sans-serif"],
        display: ["'Sora'", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 10px 40px -12px rgba(18, 59, 54, 0.25)",
        card: "0 2px 12px rgba(28, 36, 41, 0.06)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      keyframes: {
        pulseSlow: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.55 },
        },
      },
      animation: {
        pulseSlow: "pulseSlow 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
