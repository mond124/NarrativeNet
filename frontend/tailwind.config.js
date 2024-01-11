/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        Quicksand: ["Quicksand"],
      },
      colors: {
        "bg-nav": "#4A90E2",
        "bg-jumbotron": "#CDE5FF"
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeOut: {
          "0%": { opacity: "1" },
          "100%": { opacity: "0" },
        },
      },
      animation: {
        fadeIn: "fadeIn 1s ease-in-out",
        fadeOut: "fadeIn 1s ease-out duration-200 ",
      },
    },
  },
  plugins: [require("daisyui")],
};
