<template>
  <div>
    <LoginForm />
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

// Watch for auth changes
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    navigateTo('/dashboard')
  }
})
</script>