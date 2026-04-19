import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0e0818',
        bg2: '#160d24',
        bg3: '#1e1035',
        surface: 'rgba(30,16,53,0.75)',
        pink: '#f0177a',
        pink2: '#ff4da6',
        pdim: 'rgba(240,23,122,0.12)',
        purple: '#8b5cf6',
        cyan: '#06d6c7',
        text: '#ede9f8',
        muted: '#8b7aaa',
        border: 'rgba(240,23,122,0.2)',
        border2: 'rgba(139,92,246,0.2)',
      },
      fontFamily: {
        syne: ["'Syne'"],
        mono: ["'Space Mono'"],
        sans: ["'DM Sans'"],
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: 0, transform: 'translateY(14px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        bounce: {
          '0%, 80%, 100%': { transform: 'translateY(0)' },
          '40%': { transform: 'translateY(-6px)' },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.35s ease both',
        bounce: 'bounce 0.6s ease-in-out infinite',
      },
      boxShadow: {
        'pink-glow': '0 0 22px rgba(240,23,122,0.35)',
      },
    },
  },
  plugins: [],
};

export default config;

