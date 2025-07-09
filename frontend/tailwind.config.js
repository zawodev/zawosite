/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./components/**/*.{js,vue,ts}",
        "./layouts/**/*.vue",
        "./pages/**/*.vue",
        "./plugins/**/*.{js,ts}",
        "./nuxt.config.{js,ts}",
        "./app.vue"
    ],
    darkMode: 'class', // Enable class-based dark mode
    theme: {
        extend: {
            // Custom animations
            animation: {
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'bounce-in': 'bounceIn 0.6s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'scale-in': 'scaleIn 0.2s ease-out'
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
                bounceIn: {
                    '0%': { opacity: '0', transform: 'scale(0.3)' },
                    '50%': { opacity: '1', transform: 'scale(1.05)' },
                    '70%': { transform: 'scale(0.9)' },
                    '100%': { opacity: '1', transform: 'scale(1)' }
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
                scaleIn: {
                    '0%': { opacity: '0', transform: 'scale(0.95)' },
                    '100%': { opacity: '1', transform: 'scale(1)' }
                }
            },
            // Custom colors for better dark mode support
            colors: {
                gray: {
                    50: '#f9fafb',
                    100: '#f3f4f6',
                    200: '#e5e7eb',
                    300: '#d1d5db',
                    400: '#9ca3af',
                    500: '#6b7280',
                    600: '#4b5563',
                    700: '#374151',
                    800: '#1f2937',
                    900: '#111827',
                    950: '#030712'
                }
            },
            // Enhanced shadows for dark mode
            boxShadow: {
                'dark': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.1)',
                'dark-lg': '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.1)'
            }
        },
    },
    plugins: [
        // Custom plugin for component styles
        function({ addComponents, theme }) {
            addComponents({
                '.btn-primary': {
                    '@apply bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800': {},
                    '@apply text-white font-semibold py-2 px-4 rounded-lg': {},
                    '@apply shadow-lg hover:shadow-xl transform hover:-translate-y-0.5': {},
                    '@apply transition-all duration-200': {},
                    '@apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50': {},
                    '@apply disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none': {},
                    '@apply dark:from-blue-500 dark:to-blue-600 dark:hover:from-blue-600 dark:hover:to-blue-700': {}
                },
                '.card': {
                    '@apply bg-white rounded-xl shadow-lg border border-gray-100': {},
                    '@apply dark:bg-gray-800 dark:border-gray-700 dark:shadow-dark': {},
                    '@apply transition-colors duration-200': {}
                },
                '.input-field': {
                    '@apply w-full px-3 py-2 border border-gray-300 rounded-lg': {},
                    '@apply focus:ring-2 focus:ring-blue-500 focus:border-transparent': {},
                    '@apply dark:bg-gray-700 dark:border-gray-600 dark:text-white': {},
                    '@apply dark:focus:ring-blue-400': {},
                    '@apply transition-colors duration-200': {}
                }
            })
        }
    ],
}