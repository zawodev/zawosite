export const content = [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}",
    "./app.vue"
];
export const theme = {
    extend: {
        animation: {
            'fade-in': 'fadeIn 0.5s ease-in-out',
            'slide-in': 'slideIn 0.3s ease-out',
            'bounce-in': 'bounceIn 0.6s ease-out',
            'pulse-slow': 'pulse 3s infinite',
        },
        keyframes: {
            fadeIn: {
                '0%': {opacity: '0'},
                '100%': {opacity: '1'},
            },
            slideIn: {
                '0%': {transform: 'translateY(-10px)', opacity: '0'},
                '100%': {transform: 'translateY(0)', opacity: '1'},
            },
            bounceIn: {
                '0%': {transform: 'scale(0.3)', opacity: '0'},
                '50%': {transform: 'scale(1.1)'},
                '70%': {transform: 'scale(0.9)'},
                '100%': {transform: 'scale(1)', opacity: '1'},
            }
        },
        colors: {
            primary: {
                50: '#eff6ff',
                500: '#3b82f6',
                600: '#2563eb',
                700: '#1d4ed8',
            }
        }
    },
};
export const plugins = [];
