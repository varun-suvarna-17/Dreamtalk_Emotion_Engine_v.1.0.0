/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "#FFFFFF",
        primary: "#60A5FA",
        secondary: "#BAE6FD",
        charcoal: "#1E293B",
        subtle: "#F0F9FF",
        success: "#22C55E",
        error: "#EF4444",
      },
      fontFamily: {
        sans: ['Inter', 'Poppins', 'sans-serif'],
      },
      boxShadow: {
        floating: '0 10px 40px -10px rgba(96, 165, 250, 0.15)',
        'floating-hover': '0 20px 40px -10px rgba(96, 165, 250, 0.25)',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      },
      animation: {
        'fade-in': 'fade-in 0.4s ease-out',
        'slide-up': 'slide-up 0.5s ease-out forwards',
        'float': 'float 6s ease-in-out infinite',
      }
    },
  },
  plugins: [],
}
