<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center animate-fade-in">
      <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-8">
        OAuth App
      </h1>
      <p class="text-gray-600 mb-8 text-lg">
        Aplikacja z autentykacją SSO
      </p>
      <NuxtLink
          to="/login"
          class="btn-primary text-lg px-8 py-3 inline-block"
      >
        Zaloguj się
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()

// Redirect if already authenticated
onMounted(() => {
  authStore.loadFromStorage()
  if (authStore.isAuthenticated) {
    navigateTo('/dashboard')
  }
})
</script>