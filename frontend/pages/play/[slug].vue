<template>
  <div class="max-w-4xl mx-auto py-10 px-4">
    <div class="mb-6">
      <NuxtLink to="/play" class="text-blue-600 hover:underline text-sm">&larr; Powrót do listy gier</NuxtLink>
      <h1 class="text-2xl font-bold mt-2">{{ gameTitle }}</h1>
    </div>
    
    <div v-if="gameExists" class="relative w-full aspect-video bg-gray-200 dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden flex items-center justify-center">
      <client-only>
        <iframe
          v-if="iframeVisible"
          :src="iframeSrcWithKey"
          class="w-full h-full border-0 rounded-2xl"
          allowfullscreen
          @load="onLoad"
          @error="onError"
          :key="slug"
        ></iframe>
      </client-only>
      <div v-if="loading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/80 dark:bg-gray-900/80 z-10">
        <svg class="animate-spin h-10 w-10 text-blue-600 mb-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-600 dark:text-gray-300">Ładowanie gry...</span>
      </div>
      <div v-if="error" class="absolute inset-0 flex flex-col items-center justify-center bg-white/90 dark:bg-gray-900/90 z-10">
        <p class="text-red-600 font-semibold mb-2">Nie udało się załadować gry.</p>
        <button @click="reload" class="text-blue-600 hover:underline">Spróbuj ponownie</button>
      </div>
    </div>
    
    <div v-else class="flex flex-col items-center justify-center py-20">
      <svg class="w-16 h-16 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-1.414 1.414A9 9 0 105.636 18.364l1.414-1.414A7 7 0 1116.95 7.05z" />
      </svg>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Gra nie istnieje</h2>
      <p class="text-gray-600 dark:text-gray-300 mb-6">Nie znaleziono gry o podanym adresie.</p>
      <NuxtLink to="/play" class="text-blue-600 hover:underline">Powrót do listy gier</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { getGameBySlug, gameExists as isGameExists } from '~/config/games'

console.log('Play page loading...')

definePageMeta({
  layout: 'default'
})

const route = useRoute()
const authStore = useAuthStore()
const slug = computed(() => route.params.slug as string)
const loading = ref(true)
const error = ref(false)
const iframeVisible = ref(true)

console.log('Current slug:', slug.value)

// Sprawdzenie czy gra istnieje
const gameExists = computed(() => isGameExists(slug.value))
const currentGame = computed(() => getGameBySlug(slug.value))

// Ścieżka do gry
const iframeSrc = computed(() => `/games/${slug.value}/index.html`)
const iframeSrcWithKey = computed(() => `${iframeSrc.value}?v=${slug.value}`)

// Obsługa zmiany route
watch(slug, async (newSlug, oldSlug) => {
  console.log('Route changed from', oldSlug, 'to', newSlug)
  iframeVisible.value = false
  loading.value = true
  error.value = false
  await nextTick()
  setTimeout(() => {
    iframeVisible.value = true
    console.log('iframe visible set to true')
  }, 100)
})

onMounted(() => {
  console.log('Component mounted, slug:', slug.value)
  loading.value = true
  error.value = false
  
  // Słuchaj czy Unity się załadowało i wyślij token
  if (process.client) {
    setupUnityTokenSender()
  }
})

// Tytuł gry z centralnej konfiguracji
const gameTitle = computed(() => {
  return currentGame.value?.title || 'Gra'
})

function onLoad() {
  console.log('iframe loaded for:', slug.value)
  loading.value = false
  error.value = false
  
  // Po załadowaniu iframe, spróbuj wysłać token ponownie za chwilę
  setTimeout(() => {
    sendTokenToUnity()
  }, 2000)
}

function onError() {
  console.log('iframe error for:', slug.value)
  loading.value = false
  error.value = true
}

function setupUnityTokenSender() {
  // Wyślij token natychmiast przez postMessage do iframe
  setTimeout(() => {
    sendTokenToUnityViaPostMessage()
  }, 3000) // Daj Unity czas na załadowanie
  
  // Powtarzaj co 2 sekundy przez pierwsze 10 sekund
  const sendInterval = setInterval(() => {
    sendTokenToUnityViaPostMessage()
  }, 2000)
  
  setTimeout(() => {
    clearInterval(sendInterval)
  }, 10000)
}

function sendTokenToUnityViaPostMessage() {
  const iframe = document.querySelector('iframe')
  if (!iframe || !iframe.contentWindow) {
    console.error('iframe nie jest dostępny')
    return
  }
  
  // Pobierz token z store lub localStorage
  const token = authStore.token || localStorage.getItem('token') || localStorage.getItem('access_token')
  
  const message = {
    type: 'AUTH_TOKEN',
    token: token || ''
  }
  
  try {
    // Wyślij wiadomość do iframe
    iframe.contentWindow.postMessage(message, '*')
    console.log('Token wysłany do Unity przez postMessage:', token ? token.substring(0, 10) + '...' : 'empty')
  } catch (error) {
    console.error('Błąd wysyłania tokena do Unity:', error)
  }
}

function sendTokenToUnity() {
  // Stare podejście - zostaw jako fallback
  if (window.unityInstance) {
    const token = authStore.token || localStorage.getItem('token') || localStorage.getItem('access_token')
    
    if (token) {
      try {
        window.unityInstance.SendMessage('GameManager', 'SetAuthToken', token)
        console.log('Token wysłany do Unity (stare API):', token.substring(0, 10) + '...')
      } catch (error) {
        console.error('Błąd wysyłania tokena do Unity (stare API):', error)
      }
    } else {
      window.unityInstance.SendMessage('GameManager', 'SetAuthToken', '')
    }
  } else {
    console.log('window.unityInstance nie dostępny, używam postMessage')
    sendTokenToUnityViaPostMessage()
  }
}

function reload() {
  loading.value = true
  error.value = false
  window.location.reload()
}

// Dodaj typ dla window.unityInstance
declare global {
  interface Window {
    unityInstance?: {
      SendMessage: (objectName: string, methodName: string, value: string) => void
    }
  }
}
</script>

<style scoped>
.aspect-video {
  aspect-ratio: 16/9;
  min-height: 320px;
}
</style>
