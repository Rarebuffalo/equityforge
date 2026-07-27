/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        geojit: {
          navy: "#1a3a5c",
          accent: "#c0392b",
        },
      },
    },
  },
  plugins: [],
};
