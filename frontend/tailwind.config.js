/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        // Yacht Club Premium Palette
        primary: "#1C3D5A",       // Navy
        secondary: "#7A5C45",     // Brown
        accent: "#C9A66B",        // Sand Gold
        yachtBackground: "#FDFBF7",    // Cream
        cardBeige: "#EDE9E3",     // Beige
        textMain: "#000000",      // Headings
        textSecondary: "#5A6A73", // Body
        success: "#22C55E",       // Gains
        danger: "#DC2626"         // Losses
      },
      fontFamily: {
        'playfair': ['Playfair Display', 'serif'],
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
