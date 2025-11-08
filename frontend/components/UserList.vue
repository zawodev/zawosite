<template>
  <div class="card p-6 bg-white dark:bg-gray-800">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Lista użytkowników</h2>
      <button
          @click="refreshUsers"
          :disabled="loading"
          class="btn-primary text-sm flex items-center"
      >
        <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        Odśwież
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && users.length === 0" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <svg class="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.098 16.5c-.77.833.192 2.5 1.732 2.5z"/>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Błąd ładowania</h3>
      <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
      <button @click="refreshUsers" class="btn-primary">
        Spróbuj ponownie
      </button>
    </div>

    <!-- Users Grid -->
    <div v-else-if="filteredUsers.length > 0" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <NuxtLink
          v-for="user in filteredUsers"
          :key="user.id"
          :to="`/profile/${user.username}`"
          class="bg-gradient-to-br from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-600 hover:border-blue-200 dark:hover:border-blue-500 transform hover:-translate-y-2 group"
      >
        <div class="flex flex-col items-center text-center">
          <!-- Avatar -->
          <div class="mb-4">
            <img
                v-if="user.avatar_url"
                :src="user.avatar_url"
                :alt="user.full_name"
                class="h-20 w-20 rounded-full object-cover ring-4 ring-white shadow-lg group-hover:ring-blue-200 transition-all"
            >
            <div
                v-else
                class="h-20 w-20 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-2xl shadow-lg"
            >
              {{ user.full_name.charAt(0).toUpperCase() }}
            </div>
          </div>

          <!-- User Info -->
          <div class="flex-1">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
              {{ user.full_name }}
            </h3>
            <p class="text-gray-600 dark:text-gray-300 mb-3">
              @{{ user.username }}
            </p>

            <!-- Provider Badge -->
            <div class="flex justify-center mb-3">
              <span
                  :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  user.provider === 'google' ? 'bg-red-100 text-red-800' :
                  user.provider === 'facebook' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                ]"
              >
                {{ user.provider === 'google' ? 'Google' : user.provider === 'facebook' ? 'Facebook' : 'Lokalny' }}
              </span>
            </div>

            <!-- Role Badge -->
            <div class="flex justify-center mb-4">
              <span
                  :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                ]"
              >
                {{ user.role === 'admin' ? 'Administrator' : 'Użytkownik' }}
              </span>
            </div>

            <!-- Friends Count -->
            <div class="flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
              </svg>
              {{ user.friends?.length || 0 }} znajomych
            </div>
          </div>

          <!-- View Profile Arrow -->
          <div class="mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </div>
        </div>
      </NuxtLink>
    </div>

    <!-- No Users Found -->
    <div v-else class="text-center py-12">
      <svg class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Nie znaleziono użytkowników</h3>
      <p class="text-gray-600 dark:text-gray-400">
        {{ searchQuery ? `Brak wyników dla "${searchQuery}"` : 'Brak użytkowników w systemie' }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { User } from '~/stores/auth'

interface Props {
  searchQuery?: string
}

const props = withDefaults(defineProps<Props>(), {
  searchQuery: ''
})

const authStore = useAuthStore()

const users = ref<User[]>([])
const loading = ref(false)
const error = ref('')

const filteredUsers = computed(() => {
  if (!props.searchQuery) return users.value

  const query = props.searchQuery.toLowerCase()
  return users.value.filter(user =>
      user.full_name.toLowerCase().includes(query) ||
      user.username.toLowerCase().includes(query)
  )
})

const refreshUsers = async () => {
  try {
    loading.value = true
    error.value = ''
    users.value = await authStore.fetchUsers()
  } catch (err: any) {
    console.error('Error fetching users:', err)
    error.value = err.data?.detail || err.message || 'Nie udało się pobrać listy użytkowników'
  } finally {
    loading.value = false
  }
}

// Load users on mount
onMounted(() => {
  refreshUsers()
})
</script>