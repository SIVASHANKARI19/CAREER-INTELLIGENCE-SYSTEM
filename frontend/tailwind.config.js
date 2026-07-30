/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        linkedin: {
          blue: '#0A66C2',
          hover: '#004182',
          lightBg: '#F3F2EF',
          darkBg: '#1D2226',
          darkCard: '#242B31',
          accent: '#70B5F9',
        }
      }
    },
  },
  plugins: [],
}
