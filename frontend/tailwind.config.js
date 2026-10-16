/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        cyber: {
          950: '#020817',
          900: '#0f172a',
          800: '#111827',
          700: '#1e293b',
          500: '#38bdf8',
          400: '#67e8f9',
          300: '#a5f3fc',
          green: '#22c55e',
          amber: '#f59e0b',
          purple: '#8b5cf6',
        },
      },
      boxShadow: {
        glow: '0 0 20px rgba(56, 189, 248, 0.28)',
      },
    },
  },
  plugins: [],
};
