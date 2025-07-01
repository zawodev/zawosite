export default defineNuxtConfig({
    compatibilityDate: '2025-07-01',
    devtools: { enabled: true },
    modules: [
        '@nuxtjs/tailwindcss',
        '@pinia/nuxt',
        '@vueuse/nuxt',
        '@nuxtjs/color-mode',
    ],
    colorMode: {
        classSuffix: '',
        preference: 'system',
        fallback: 'light',
        storageKey: 'color-mode'
    },
    css: ['~/assets/css/main.css'],
    runtimeConfig: {
        public: {
            apiBase: process.env.API_BASE_URL || 'http://localhost:8000',
            googleClientId: process.env.GOOGLE_CLIENT_ID || '',
            facebookAppId: process.env.FACEBOOK_APP_ID || ''
        }
    },
    app: {
        head: {
            title: 'zawosite',
            link : [
                { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
                //{ rel: 'icon', type: 'image/png', href: '/myicon.png' },
            ],
            meta: [
                { charset: 'utf-8' },
                { name: 'viewport', content: 'width=device-width, initial-scale=1' }
            ],
            script: [
                {
                    src: 'https://accounts.google.com/gsi/client',
                    async: true,
                    defer: true
                }
            ]
        }
    }
})