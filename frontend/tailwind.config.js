

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'bg-nav': '#4A90E2',
      }
    },
  },
  plugins: [require('daisyui')],
};
