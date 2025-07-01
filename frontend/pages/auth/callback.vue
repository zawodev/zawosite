<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <div v-if="loading" class="space-y-4">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
        <h2 class="text-xl font-semibold text-gray-900">Logowanie w toku...</h2>
        <p class="text-gray-600">Proszę czekać, trwa uwierzytelnianie</p>
      </div>

      <div v-else-if="error" class="space-y-4">
        <svg class="w-16 h-16 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.098 16.5c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
        <h2 class="text-xl font-semibold text-gray-900">Błąd logowania</h2>
        <p class="text-gray-600">{{ error }}</p>
        <NuxtLink to="/login" class="btn-primary inline-block">
          Spróbuj ponownie
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const token = route.query.token as string
    const userData = route.query.user as string

    if (!token || !userData) {
      throw new Error('Brak wymaganych danych uwierzytelniania')
    }

    // Parse user data
    const user = JSON.parse(decodeURIComponent(userData))

    // Set authentication
    authStore.setAuth(token, user)

    // Redirect to dashboard
    await navigateTo('/dashboard')
  } catch (err: any) {
    error.value = err.message || 'Wystąpił błąd podczas logowania'
    loading.value = false
  }
})

// Set page metadata
useHead({
  title: 'Logowanie - OAuth App'
})
</script>