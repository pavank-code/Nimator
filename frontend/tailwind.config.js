/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Nimator Brand Colors
        nimator: {
          red: '#F24C4C',      // Primary brand red from logo
          coral: '#FF5A5A',    // Lighter coral accent
          dark: '#1A1A1A',     // Brand dark
        },
        // Accent Colors (complementing Nimator Red)
        vercel: {
          blue: '#0070F3',
          violet: '#7928CA',
          cyan: '#50E3C2',
          pink: '#FF0080',
          orange: '#FF4D4D',
        },
        // Remap Slate (used for backgrounds) to Dark Scale
        slate: {
          50: '#fafafa',
          100: '#eaeaea',
          200: '#999999',
          300: '#888888',
          400: '#666666',
          500: '#444444',
          600: '#333333',
          700: '#111111',
          800: '#0a0a0a',
          900: '#050505',
          950: '#000000',
        },
        // Remap Gray to Neutral
        gray: {
          50: '#fafafa',
          100: '#eaeaea',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '26': '6.5rem',
        '30': '7.5rem',
        '96': '24rem',
        '128': '32rem',
      },
      fontSize: {
        '5xl': ['3rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        '6xl': ['3.75rem', { lineHeight: '1', letterSpacing: '-0.02em' }],
        '7xl': ['4.5rem', { lineHeight: '1', letterSpacing: '-0.04em' }],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.5s ease-out forwards',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'border-beam': 'border-beam calc(var(--duration)*1s) infinite linear',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'border-beam': {
          '100%': {
            'offset-distance': '100%',
          },
        },
      },
    },
  },
  plugins: [],
}