<template>
  <div class="card p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Lista użytkowników</h2>
      <button
          @click="refreshUsers"
          :disabled="loading"
          class="btn-primary text-sm"
      >
        <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Odśwież
      </button>
    </div>

    <div v-if="error" class="mb-4 p-4 bg-red-50 border-l-4 border-red-400 text-red-700 animate-slide-in">
      {{ error }}
    </div>

    <div v-if="loading && !users.length" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="users.length === 0" class="text-center py-12 text-gray-500">
      Brak użytkowników do wyświetlenia
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
          v-for="(user, index) in users"
          :key="user.id"
          class="bg-gradient-to-br from-white to-gray-50 rounded-lg p-6 shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100 animate-fade-in"
          :style="{ animationDelay: `${index * 100}ms` }"
      >
        <div class="flex items-center space-x-4">
          <div class="flex-shrink-0">
            <img
                v-if="user.avatar_url"
                :src="user.avatar_url"
                :alt="user.full_name"
                class="h-12 w-12 rounded-full object-cover ring-2 ring-white shadow-md"
            >
            <div
                v-else
                class="h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-semibold text-lg shadow-md"
            >
              {{ user.full_name.charAt(0).toUpperCase() }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-lg font-semibold text-gray-900 truncate">
              {{ user.full_name }}
            </p>
            <p class="text-sm text-gray-600 truncate">
              {{ user.email }}
            </p>
          </div>
        </div>

        <div class="mt-4 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500">Provider:</span>
            <div class="flex items-center space-x-1">
              <svg v-if="user.provider === 'google'" class="w-4 h-4 text-red-500" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <svg v-else-if="user.provider === 'facebook'" class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              <span class="text-sm font-medium capitalize">{{ user.provider }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500">Rola:</span>
            <span
                :class="{
                'bg-green-100 text-green-800': user.role === 'admin',
                'bg-blue-100 text-blue-800': user.role === 'user'
              }"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            >
              <svg v-if="user.role === 'admin'" class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              <svg v-else class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
              {{ user.role === 'admin' ? 'Administrator' : 'Użytkownik' }}
            </span>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500">Status:</span>
            <span
                :class="{
                'bg-green-100 text-green-800': user.is_active,
                'bg-red-100 text-red-800': !user.is_active
              }"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            >
              <div
                  :class="{
                  'bg-green-400': user.is_active,
                  'bg-red-400': !user.is_active
                }"
                  class="w-2 h-2 rounded-full mr-1.5"
              ></div>
              {{ user.is_active ? 'Aktywny' : 'Nieaktywny' }}
            </span>
          </div>

          <div class="mt-3 pt-3 border-t border-gray-200">
            <span class="text-xs text-gray-500">
              Dołączył: {{ formatDate(user.created_at) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')

const users = computed(() => authStore.users)

const refreshUsers = async () => {
  loading.value = true
  error.value = ''

  try {
    await authStore.fetchUsers()
  } catch (err: any) {
    error.value = err.message || 'Błąd podczas pobierania użytkowników'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Load users on component mount
onMounted(() => {
  refreshUsers()
})
</script>