<template>
  <div
      class="
      min-h-screen
      bg-gradient-to-br from-blue-50 to-indigo-100
      dark:bg-gradient-to-br dark:from-gray-900 dark:to-gray-800
      transition-colors duration-300
    "
  >
    <AppHeader />
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()

// Load auth state on app initialization
onMounted(async () => {
  await authStore.loadFromStorage()
})
</script>