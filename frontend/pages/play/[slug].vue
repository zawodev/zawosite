<template>
  <div class="max-w-7xl mx-auto py-10 px-4">
    <div class="mb-6">
      <NuxtLink to="/play" class="text-blue-600 hover:underline text-sm">&larr; Powrót do listy gier</NuxtLink>
      <div class="flex items-start justify-between mt-4">
        <div class="flex-1">
          <h1 class="text-3xl font-bold">{{ gameTitle }}</h1>
          <div class="flex flex-wrap gap-2 mt-3">
            <NuxtLink 
              v-for="tag in currentGame?.tags" 
              :key="tag.text"
              :to="`/play?tag=${encodeURIComponent(tag.text)}`"
              class="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            >
              <component :is="tag.icon" class="w-4 h-4" />
              {{ tag.text }}
            </NuxtLink>
          </div>
        </div>
        <div class="text-right ml-4">
          <div v-if="currentGame?.category" class="inline-block px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full text-sm font-medium mb-2">
            {{ currentGame.category }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            Dodano: {{ formatDate(currentGame?.addedDate) }}
          </div>
        </div>
      </div>
      <p v-if="currentGame?.description" class="mt-4 text-gray-700 dark:text-gray-300">
        {{ currentGame.description }}
      </p>
    </div>
    
    <div v-if="gameExists" class="relative w-full aspect-video bg-gray-200 dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden flex items-center justify-center mb-8">
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

    <!-- Comments Section -->
    <div v-if="gameExists" class="mt-12">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold">Komentarze ({{ comments.length }})</h2>
        <button 
          @click="toggleSortBy"
          class="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors text-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
          </svg>
          {{ sortBy === 'karma' ? 'Według karmy' : 'Najnowsze' }}
        </button>
      </div>

      <!-- Add Comment Form (if authenticated) -->
      <div v-if="authStore.isAuthenticated" class="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Dodaj komentarz</h3>
        <textarea
          v-model="newCommentContent"
          placeholder="Podziel się swoją opinią..."
          class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 resize-none"
          rows="4"
        ></textarea>
        <div class="flex justify-end gap-3 mt-4">
          <button 
            v-if="newCommentContent.trim()"
            @click="newCommentContent = ''"
            class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            Anuluj
          </button>
          <button 
            @click="submitComment"
            :disabled="submitting || newCommentContent.trim().length < 3"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ submitting ? 'Wysyłanie...' : 'Wyślij' }}
          </button>
        </div>
      </div>

      <!-- Login Prompt -->
      <div v-else class="mb-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 text-center">
        <p class="text-gray-700 dark:text-gray-300 mb-3">Zaloguj się, aby dodać komentarz</p>
        <NuxtLink to="/" class="text-blue-600 hover:underline font-medium">Przejdź do logowania</NuxtLink>
      </div>

      <!-- Comments List -->
      <div v-if="loadingComments" class="text-center py-8">
        <svg class="animate-spin h-8 w-8 text-blue-600 mx-auto" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <div v-else-if="comments.length === 0" class="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <svg class="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <p class="text-gray-600 dark:text-gray-400">Brak komentarzy. Bądź pierwszy!</p>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="comment in comments" 
          :key="comment.id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
        >
          <div class="flex items-start gap-4">
            <!-- Vote Controls -->
            <div class="flex flex-col items-center gap-1">
              <button 
                @click="voteComment(comment.id, 'up')"
                :disabled="!authStore.isAuthenticated"
                :class="[
                  'p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors',
                  comment.user_vote === 'up' ? 'text-green-600' : 'text-gray-400',
                  !authStore.isAuthenticated && 'cursor-not-allowed opacity-50'
                ]"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                </svg>
              </button>
              <span :class="[
                'font-bold text-sm',
                comment.karma > 0 ? 'text-green-600' : comment.karma < 0 ? 'text-red-600' : 'text-gray-600'
              ]">
                {{ comment.karma }}
              </span>
              <button 
                @click="voteComment(comment.id, 'down')"
                :disabled="!authStore.isAuthenticated"
                :class="[
                  'p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors',
                  comment.user_vote === 'down' ? 'text-red-600' : 'text-gray-400',
                  !authStore.isAuthenticated && 'cursor-not-allowed opacity-50'
                ]"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.105-1.79l-.05-.025A4 4 0 0011.055 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
                </svg>
              </button>
            </div>

            <!-- Comment Content -->
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <div class="flex items-center gap-2">
                  <img 
                    v-if="comment.avatar_url" 
                    :src="comment.avatar_url" 
                    :alt="comment.username"
                    class="w-8 h-8 rounded-full"
                  />
                  <div v-else class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
                    {{ comment.username[0].toUpperCase() }}
                  </div>
                  <span class="font-semibold text-gray-900 dark:text-gray-100">{{ comment.username }}</span>
                </div>
                <span class="text-sm text-gray-500">{{ formatCommentDate(comment.created_at) }}</span>
                <button
                  v-if="authStore.user?.username === comment.username"
                  @click="deleteComment(comment.id)"
                  class="ml-auto text-red-600 hover:text-red-700 text-sm"
                >
                  Usuń
                </button>
              </div>
              <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ comment.content }}</p>
              <div v-if="comment.created_at !== comment.updated_at" class="text-xs text-gray-500 mt-2">
                (edytowano)
              </div>
            </div>
          </div>
        </div>
      </div>
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
const config = useRuntimeConfig()
const authStore = useAuthStore()
const slug = computed(() => route.params.slug as string)
const loading = ref(true)
const error = ref(false)
const iframeVisible = ref(true)

// Comments state
const comments = ref<any[]>([])
const loadingComments = ref(false)
const newCommentContent = ref('')
const submitting = ref(false)
const sortBy = ref<'date' | 'karma'>('date')

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
  
  // Load comments for new game
  fetchComments()
})

onMounted(() => {
  console.log('Component mounted, slug:', slug.value)
  loading.value = true
  error.value = false
  
  // Słuchaj czy Unity się załadowało i wyślij token
  if (process.client) {
    setupUnityTokenSender()
  }
  
  // Load comments
  fetchComments()
})

// Tytuł gry z centralnej konfiguracji
const gameTitle = computed(() => {
  return currentGame.value?.title || 'Gra'
})

function onLoad() {
  console.log('iframe loaded for:', slug.value)
  loading.value = false
  error.value = false
  
  // Send token immediately after iframe loads
  sendTokenToUnityViaPostMessage()
}

function onError() {
  console.log('iframe error for:', slug.value)
  loading.value = false
  error.value = true
}

function setupUnityTokenSender() {
  // Send token after a short delay to ensure iframe is ready
  setTimeout(() => {
    sendTokenToUnityViaPostMessage()
  }, 1000)
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
    console.log('✅ Token sent to game:', token ? token.substring(0, 10) + '...' : 'empty')
  } catch (error) {
    console.error('Błąd wysyłania tokena do gry:', error)
  }
}

function reload() {
  loading.value = true
  error.value = false
  window.location.reload()
}

// Date formatting
function formatDate(dateString: string | undefined) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatCommentDate(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'przed chwilą'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} min temu`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} godz. temu`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} dni temu`
  
  return date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'short', day: 'numeric' })
}

// Comments API functions
async function fetchComments() {
  loadingComments.value = true
  try {
    const sortParam = sortBy.value === 'karma' ? '?sort_by=karma' : '?sort_by=date'
    const response = await $fetch(`${config.public.apiBase}/api/v1/games/comments/${slug.value}/${sortParam}`, {
      headers: authStore.token ? {
        'Authorization': `Token ${authStore.token}`
      } : {}
    })
    comments.value = response as any[]
  } catch (err) {
    console.error('Error fetching comments:', err)
  } finally {
    loadingComments.value = false
  }
}

async function submitComment() {
  if (!authStore.isAuthenticated || newCommentContent.value.trim().length < 3) return
  
  submitting.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/games/comments/${slug.value}/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: {
        content: newCommentContent.value
      }
    })
    
    // Add comment to list (optimistic update)
    comments.value.unshift(response as any)
    newCommentContent.value = ''
  } catch (err: any) {
    console.error('Error submitting comment:', err)
    alert(err.data?.content?.[0] || 'Nie udało się dodać komentarza')
  } finally {
    submitting.value = false
  }
}

async function voteComment(commentId: number, voteType: 'up' | 'down') {
  if (!authStore.isAuthenticated) return
  
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/games/comments/${slug.value}/${commentId}/vote/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: { vote_type: voteType }
    })
    
    // Update comment in list
    const index = comments.value.findIndex(c => c.id === commentId)
    if (index !== -1) {
      comments.value[index] = response as any
    }
  } catch (err) {
    console.error('Error voting:', err)
  }
}

async function deleteComment(commentId: number) {
  if (!confirm('Czy na pewno chcesz usunąć ten komentarz?')) return
  
  try {
    await $fetch(`${config.public.apiBase}/api/v1/games/comments/${slug.value}/${commentId}/delete_comment/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })
    
    // Remove comment from list
    comments.value = comments.value.filter(c => c.id !== commentId)
  } catch (err) {
    console.error('Error deleting comment:', err)
    alert('Nie udało się usunąć komentarza')
  }
}

function toggleSortBy() {
  sortBy.value = sortBy.value === 'date' ? 'karma' : 'date'
  fetchComments()
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
