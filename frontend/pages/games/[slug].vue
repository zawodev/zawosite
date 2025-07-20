<template>
  <div class="max-w-4xl mx-auto py-10 px-4">
    <div class="mb-6 flex items-center space-x-4">
      <button @click="$router.back()" class="text-blue-600 hover:underline text-sm">&larr; Powrót do listy gier</button>
      <h1 class="text-2xl font-bold">{{ gameTitle }}</h1>
    </div>
    <div class="relative w-full aspect-video bg-gray-200 dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden flex items-center justify-center">
      <iframe
        v-if="iframeSrc"
        :src="iframeSrc"
        class="w-full h-full border-0 rounded-2xl"
        allowfullscreen
        @load="onLoad"
        @error="onError"
      ></iframe>
      <div v-if="loading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/80 dark:bg-gray-900/80 z-10">
        <svg class="animate-spin h-10 w-10 text-blue-600 mb-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-600 dark:text-gray-300">Ładowanie gry...</span>
      </div>
      <div v-if="error" class="absolute inset-0 flex flex-col items-center justify-center bg-white/90 dark:bg-gray-900/90 z-10">
        <p class="text-red-600 font-semibold mb-2">Nie udało się załadować gry.</p>
        <button @click="reload" class="btn-primary">Spróbuj ponownie</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, computed } from 'vue'

const route = useRoute()
const slug = computed(() => route.params.slug as string)
const loading = ref(true)
const error = ref(false)

const iframeSrc = computed(() => `/games/${slug.value}/index.html`)
const gameTitle = computed(() => {
  // Możesz rozwinąć o pobieranie tytułu z API lub na podstawie slug
  if (slug.value === 'zawomons') return 'Zawomons'
  if (slug.value === 'logic-game') return 'Gra logiczna'
  return 'Gra'
})

function onLoad() {
  loading.value = false
  error.value = false
}
function onError() {
  loading.value = false
  error.value = true
}
function reload() {
  loading.value = true
  error.value = false
  // Wymuszenie przeładowania iframe przez zmianę klucza
  window.location.reload()
}
</script>

<style scoped>
.aspect-video {
  aspect-ratio: 16/9;
  min-height: 320px;
}
</style> 