/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg1: '#0a0b0e',
        bg2: '#0d0f16',
        bg3: '#0f1117',
        border1: '#1e2130',
        border2: '#2a3050',
        accent: '#3b82f6',
        accent2: '#2563eb',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}