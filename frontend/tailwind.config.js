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
        // Enhanced Modern Fintech Palette
        brand: {
          50: '#f0f9ff',   // Lightest sky
          100: '#e0f2fe',  // Very light sky
          200: '#bae6fd',  // Light sky
          300: '#7dd3fc',  // Medium light sky
          400: '#38bdf8',  // Medium sky
          500: '#0ea5e9',  // Base sky (primary)
          600: '#0284c7',  // Dark sky (CTA buttons)
          700: '#0369a1',  // Darker sky (hover)
          800: '#075985',  // Very dark sky
          900: '#0c4a6e',  // Darkest sky
        },
        neutral: {
          50: '#fafafa',   // Pure white-alternative
          100: '#f5f5f5',  // Very light gray
          200: '#e5e5e5',  // Light gray
          300: '#d4d4d4',  // Medium light gray
          400: '#a3a3a3',  // Medium gray
          500: '#737373',  // Base gray
          600: '#525252',  // Dark gray
          700: '#404040',  // Darker gray
          800: '#262626',  // Very dark gray
          900: '#171717',  // Almost black
        },
        // Yacht Club Premium Palette (for dashboard)
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
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
        'gradient-soft': 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        'gradient-hero': 'linear-gradient(135deg, #ffffff 0%, #f1f5f9 50%, #e2e8f0 100%)',
      },
      boxShadow: {
        'soft': '0 2px 8px 0 rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 16px 0 rgba(0, 0, 0, 0.08)',
        'strong': '0 8px 32px 0 rgba(0, 0, 0, 0.12)',
        'brand': '0 4px 16px 0 rgba(2, 132, 199, 0.15)',
      },
      fontFamily: {
        'playfair': ['Playfair Display', 'serif'],
        'inter': ['Inter', 'sans-serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
