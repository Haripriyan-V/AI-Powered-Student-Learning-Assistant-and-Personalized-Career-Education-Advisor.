/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        // "Iris" - primary brand hue: trust, focus, AI guidance
        iris: {
          50: '#F1F1FE',
          100: '#E3E4FC',
          200: '#C7C9F9',
          300: '#A3A6F3',
          400: '#7C7FEE',
          500: '#5B5FEF',
          600: '#4548D6',
          700: '#3536AC',
          800: '#292A85',
          900: '#1F2065',
          950: '#14153F',
        },
        // "Marigold" - accent hue: achievement, milestones, celebration
        marigold: {
          50: '#FFF8E8',
          100: '#FFEDC2',
          200: '#FFDD8A',
          300: '#FDC74F',
          400: '#F5A524',
          500: '#E08E0F',
          600: '#BA710A',
          700: '#92560A',
          800: '#6E410C',
          900: '#4F2E0C',
        },
        // "Growth" - secondary accent: progress, success, learning momentum
        growth: {
          50: '#ECFDF7',
          100: '#D2FAEC',
          200: '#A6F2DA',
          300: '#6CE3C2',
          400: '#34C8A4',
          500: '#0D9488',
          600: '#0A766F',
          700: '#0B5D59',
          800: '#0C4946',
          900: '#0B3B39',
        },
        // "Ink" - neutral scale used for both light & dark surfaces
        ink: {
          0: '#FFFFFF',
          25: '#FAFBFD',
          50: '#F5F6FA',
          100: '#EEF0F6',
          200: '#E1E4ED',
          300: '#C8CCDA',
          400: '#9CA1B5',
          500: '#6E7390',
          600: '#4F5470',
          700: '#383B52',
          800: '#23253A',
          850: '#1A1C2C',
          900: '#14151F',
          950: '#0E0F17',
        },
        danger: {
          50: '#FDF1F3',
          400: '#E2436B',
          500: '#C8264E',
          600: '#A11E40',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        soft: '0 1px 2px 0 rgba(20, 21, 31, 0.04), 0 2px 8px -2px rgba(20, 21, 31, 0.06)',
        lift: '0 4px 16px -4px rgba(20, 21, 31, 0.12), 0 2px 6px -2px rgba(20, 21, 31, 0.06)',
        glow: '0 0 0 1px rgba(91, 95, 239, 0.15), 0 8px 24px -8px rgba(91, 95, 239, 0.35)',
      },
      borderRadius: {
        xl2: '1.25rem',
      },
      backgroundImage: {
        'gradient-iris': 'linear-gradient(135deg, #4548D6 0%, #5B5FEF 50%, #7C7FEE 100%)',
        'gradient-marigold': 'linear-gradient(135deg, #E08E0F 0%, #F5A524 50%, #FDC74F 100%)',
        'gradient-dusk': 'linear-gradient(135deg, #1F2065 0%, #4548D6 45%, #0D9488 100%)',
        'trail-dots': 'radial-gradient(circle, currentColor 1.5px, transparent 1.5px)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'trail-draw': {
          '0%': { strokeDashoffset: '1000' },
          '100%': { strokeDashoffset: '0' },
        },
        'pulse-dot': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.6', transform: 'scale(1.15)' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.5s ease-out forwards',
        'trail-draw': 'trail-draw 1.8s ease-out forwards',
        'pulse-dot': 'pulse-dot 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
