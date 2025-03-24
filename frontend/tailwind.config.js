/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            color: '#475569',
            a: {
              color: '#5D83E4',
              '&:hover': {
                color: '#7FA1F9',
              },
            },
            h1: {
              color: '#334155',
            },
            h2: {
              color: '#334155',
            },
            h3: {
              color: '#334155',
            },
            h4: {
              color: '#334155',
            },
            blockquote: {
              color: '#64748B',
              borderLeftColor: '#5D83E4',
            },
            code: {
              color: '#F5CA45',
              backgroundColor: 'rgba(93, 131, 228, 0.1)',
              padding: '0.2em 0.4em',
              borderRadius: '0.25rem',
            },
            pre: {
              backgroundColor: '#1e293b',
              code: {
                backgroundColor: 'transparent',
                color: '#e2e8f0',
              },
            },
          },
        },
        invert: {
          css: {
            color: '#e2e8f0',
            a: {
              color: '#7AE9DC',
              '&:hover': {
                color: '#9FF5EB',
              },
            },
            h1: {
              color: '#f8fafc',
            },
            h2: {
              color: '#f8fafc',
            },
            h3: {
              color: '#f8fafc',
            },
            h4: {
              color: '#f8fafc',
            },
            blockquote: {
              color: '#94A3B8',
              borderLeftColor: '#7AE9DC',
            },
            code: {
              color: '#F5CA45',
              backgroundColor: 'rgba(122, 233, 220, 0.1)',
            },
            pre: {
              backgroundColor: '#1e293b',
              code: {
                backgroundColor: 'transparent',
              },
            },
            strong: {
              color: '#f8fafc',
            },
          },
        },
      },
      colors: {
        primary: {
          dark: '#4C6FCC',  // Krishna blue - darker
          DEFAULT: '#5D83E4', // Krishna blue
          light: '#7FA1F9', // Krishna blue - lighter
        },
        secondary: {
          dark: '#59B9C6',
          DEFAULT: '#79D3DF',
          light: '#9FE4ED',
        },
        accent: {
          dark: '#D6B03A', // Gold/yellow for spiritual connection
          DEFAULT: '#F5CA45',
          light: '#FFDC6B',
        },
        highlight: {
          dark: '#5DD6C8',
          DEFAULT: '#7AE9DC',
          light: '#9FF5EB',
        },
        spiritual: {
          dark: '#9B59B6', // Purple - spiritual connection
          DEFAULT: '#AF7AC5',
          light: '#D2B4DE',
        },
        background: {
          dark: '#F2F8FF',
          DEFAULT: '#FBFCFE',
          light: '#FFFFFF',
        },
        text: {
          dark: '#334155',
          DEFAULT: '#475569',
          light: '#64748B',
          muted: '#94A3B8',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
        heading: ['Montserrat', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        accent: ['Quicksand', 'sans-serif'],
        script: ['Dancing Script', 'cursive'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gentle-gradient': 'linear-gradient(to bottom right, #F9FAFF, #EEF6FF, #F5FAFF)',
        'soft-glow': 'radial-gradient(circle at center, rgba(161, 196, 253, 0.3) 0%, rgba(255, 255, 255, 0) 70%)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow-1': 'spin 30s linear infinite',
        'spin-slow-2': 'spin 40s linear infinite reverse',
        'spin-slow-3': 'spin 50s linear infinite',
        'spin-slow-4': 'spin 60s linear infinite reverse',
        'float': 'float 6s ease-in-out infinite',
        'wave': 'wave 8s linear infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'slide-left': 'slideLeft 0.6s ease-out forwards',
        'draw': 'drawPath 3s ease-out forwards',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        wave: {
          '0%': { transform: 'translateX(0) translateY(0)' },
          '25%': { transform: 'translateX(5px) translateY(-5px)' },
          '50%': { transform: 'translateX(0) translateY(0)' },
          '75%': { transform: 'translateX(-5px) translateY(5px)' },
          '100%': { transform: 'translateX(0) translateY(0)' },
        },
        glow: {
          '0%, 100%': { filter: 'brightness(1)' },
          '50%': { filter: 'brightness(1.1)' },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        slideLeft: {
          '0%': { transform: 'translateX(20px)', opacity: 0 },
          '100%': { transform: 'translateX(0)', opacity: 1 },
        },
        drawPath: {
          '0%': { strokeDasharray: '0 1000', opacity: 0 },
          '20%': { opacity: 1 },
          '100%': { strokeDasharray: '1000 1000', opacity: 1 }
        },
      },
      boxShadow: {
        'soft-sm': '0 2px 10px rgba(203, 213, 225, 0.3)',
        'soft-md': '0 4px 20px rgba(203, 213, 225, 0.4)',
        'soft-lg': '0 8px 30px rgba(203, 213, 225, 0.5)',
        'glow-sm': '0 0 15px rgba(122, 233, 220, 0.3)',
        'glow-md': '0 0 25px rgba(122, 233, 220, 0.4)',
        'glow-lg': '0 0 35px rgba(122, 233, 220, 0.5)',
        'accent-glow': '0 0 15px rgba(217, 191, 239, 0.4)',
        'primary-glow': '0 0 15px rgba(123, 167, 217, 0.4)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}