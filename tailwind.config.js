/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./src/components/**/*.{js,jsx,ts,tsx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}"
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