<template>
  <div class="min-h-screen flex flex-col items-center justify-center">
    <div class="w-full max-w-2xl mx-auto text-center animate-fade-in">
      <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-8">
        Witaj w zawosite!
      </h1>
      <div v-if="!authStore.isAuthenticated && !hideWarning" class="bg-yellow-100 border border-yellow-300 text-yellow-800 px-6 py-4 rounded-lg mb-8 relative flex items-center justify-center">
        <span class="mr-8">Nie jesteś zalogowany! Twoje postępy nie zostaną zapisane. Zaloguj się, aby korzystać w pełni z aplikacji.</span>
        <button @click="hideWarning = true" class="absolute right-4 top-1/2 -translate-y-1/2 text-yellow-600 hover:text-red-500">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div v-else-if="authStore.isAuthenticated" class="mb-8">
        <p class="text-green-600 font-semibold">Jesteś zalogowany jako {{ authStore.displayName }}</p>
      </div>
      <!-- Komponent rekomendacji gier -->
      <GameRecommendations v-if="authStore.isAuthenticated" />
    </div>
    <LoginPanel v-if="showLogin" @close="showLogin = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import GameRecommendations from '~/components/GameRecommendations.vue'
import LoginPanel from '~/components/LoginPanel.vue'

const authStore = useAuthStore()
const showLogin = ref(false)
const hideWarning = ref(false)

// Obsługa zamykania LoginPanel przez event globalny
const closeLoginPanel = () => { showLogin.value = false }
onMounted(() => {
  window.addEventListener('close-login-panel', closeLoginPanel)
})
onUnmounted(() => {
  window.removeEventListener('close-login-panel', closeLoginPanel)
})
</script>