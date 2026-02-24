module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
    // Ці плагіни можна залишити, якщо вони вам потрібні, але v4 вже вміє nesting
    "postcss-simple-vars": {},
    "postcss-nested": {}
  },
}