/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./hub/**/*.{js,ts,jsx,tsx,mdx}",
    "./architecture-map/**/*.{js,ts,jsx,tsx,mdx}",
    "./*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        'terminal-dark': '#0f0f1a',
        'terminal-green': '#00ff41',
        'terminal-blue': '#00bfff',
        'terminal-purple': '#8000ff'
      }
    },
  },
  plugins: [],
}
