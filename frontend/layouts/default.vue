<template>
  <div class="app-container">
    <AppHeader />
    <main class="main-content">
      <div class="content-wrapper">
        <slot />
      </div>
    </main>
    <AppFooter v-if="showFooter" />
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const route = useRoute()

// Show footer on certain pages
const showFooter = computed(() => {
  const hideFooterRoutes = ['/login', '/auth/callback']
  return !hideFooterRoutes.includes(route.path)
})

// Load auth state on app initialization
onMounted(async () => {
  await authStore.loadFromStorage()
})

// Set up proper color mode handling
const colorMode = useColorMode()

// Watch for system color scheme changes
onMounted(() => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

  const handleChange = (e: MediaQueryListEvent) => {
    if (colorMode.preference === 'system') {
      // Force update when system preference changes
      colorMode.value = e.matches ? 'dark' : 'light'
    }
  }

  mediaQuery.addEventListener('change', handleChange)

  onUnmounted(() => {
    mediaQuery.removeEventListener('change', handleChange)
  })
})
</script>

<style scoped>
.app-container {
  @apply min-h-screen flex flex-col;
  @apply bg-gradient-to-br from-blue-50 via-white to-indigo-50;
  @apply dark:bg-gradient-to-br dark:from-gray-900 dark:via-gray-800 dark:to-slate-900;
  @apply transition-all duration-500 ease-in-out;
}

.main-content {
  @apply flex-1 relative;
}

.content-wrapper {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8;
  @apply min-h-[calc(100vh-4rem)]; /* Adjust based on header height */
}

/* Improved background patterns */
.app-container::before {
  content: '';
  @apply absolute inset-0 opacity-30 pointer-events-none;
  @apply bg-gradient-to-br from-transparent via-blue-100/20 to-purple-100/20;
  @apply dark:from-transparent dark:via-blue-900/10 dark:to-purple-900/10;
  background-image:
      radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.1) 0%, transparent 50%);
}

.dark .app-container::before {
  background-image:
      radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(34, 197, 94, 0.05) 0%, transparent 50%);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .content-wrapper {
    @apply px-3 py-4;
  }
}

/* Smooth scrolling */
html {
  @apply scroll-smooth;
}

/* Custom scrollbar for webkit browsers */
::-webkit-scrollbar {
  @apply w-2;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}
</style>