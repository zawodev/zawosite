export default defineNuxtRouteMiddleware((to, from) => {
    const authStore = useAuthStore()

    // Load auth from storage if not already loaded
    if (!authStore.isAuthenticated && import.meta.client) {
        authStore.loadFromStorage()
    }

    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
        return navigateTo('/')
    }

    // Check if user is admin
    if (authStore.user?.role !== 'admin') {
        return navigateTo('/')
    }
})

