/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-base': '#0d0f14',
        'bg-surface': '#131720',
        'bg-elevated': '#1a1f2e',
        'bg-overlay': '#1e2435',
        'border-default': '#252d3d',
        'border-subtle': '#1c2230',
        'text-primary': '#e8eaf0',
        'text-secondary': '#8892a4',
        'text-tertiary': '#4a5568',
        'accent-cyan': '#00d4aa',
        'status-critical': '#ef4444',
        'status-high': '#f97316',
        'status-medium': '#eab308',
        'status-normal': '#22c55e',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        '2xs': '0.625rem',
      },
    },
  },
  plugins: [],
}
