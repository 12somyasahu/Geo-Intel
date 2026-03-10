/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: { 900: '#0a0f1e', 800: '#0d1526', 700: '#111d35', 600: '#1a2d4a' },
        accent: { cyan: '#00b4d8', red: '#e84040', gold: '#f4a261' },
      },
      fontFamily: { mono: ['JetBrains Mono', 'Fira Code', 'monospace'] },
    },
  },
  plugins: [],
}
