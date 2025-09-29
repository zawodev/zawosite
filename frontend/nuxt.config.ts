export default defineNuxtConfig({
    compatibilityDate: '2025-07-01',
    devtools: { enabled: true },
    css: ['~/assets/css/main.css'],
    modules: [
        '@nuxtjs/tailwindcss',
        '@nuxtjs/color-mode',
        '@pinia/nuxt',
        '@vueuse/nuxt',
    ],
    colorMode: {
        preference: 'system', // default theme
        dataValue: 'theme', // activate data-theme in <html> tag
        classSuffix: '', // no suffix for CSS classes
        classPrefix: '',
        storageKey: 'nuxt-color-mode'
    },
    tailwindcss: {
        cssPath: '~/assets/css/main.css',
        configPath: 'tailwind.config.js',
        exposeConfig: false,
        viewer: true,
    },
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
                { rel: 'icon', type: 'image/x-icon', href: '/favicon-krecik.ico' },
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