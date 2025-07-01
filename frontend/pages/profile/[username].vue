<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-20">
      <div class="card p-8 max-w-md mx-auto">
        <svg class="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.098 16.5c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
        <h2 class="text-xl font-semibold text-gray-900 mb-2">Użytkownik nie znaleziony</h2>
        <p class="text-gray-600 mb-6">{{ error }}</p>
        <NuxtLink to="/users" class="btn-primary">
          Powrót do listy użytkowników
        </NuxtLink>
      </div>
    </div>

    <!-- Profile Content -->
    <div v-else-if="userProfile" class="space-y-6">
      <!-- Profile Header -->
      <div class="card p-8">
        <div class="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
          <!-- Avatar -->
          <div class="flex-shrink-0">
            <img
                v-if="userProfile.avatar_url"
                :src="userProfile.avatar_url"
                :alt="userProfile.full_name"
                class="h-32 w-32 rounded-full object-cover ring-4 ring-white shadow-lg"
            >
            <div
                v-else
                class="h-32 w-32 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-4xl shadow-lg"
            >
              {{ userProfile.full_name.charAt(0).toUpperCase() }}
            </div>
          </div>

          <!-- Profile Info -->
          <div class="flex-1 text-center md:text-left">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
              {{ userProfile.full_name }}
            </h1>
            <p class="text-xl text-gray-600 mb-4">
              @{{ userProfile.username }}
            </p>

            <!-- Bio -->
            <p v-if="userProfile.bio" class="text-gray-700 mb-4 max-w-2xl">
              {{ userProfile.bio }}
            </p>

            <!-- Stats -->
            <div class="flex justify-center md:justify-start space-x-6 mb-6">
              <div class="text-center">
                <div class="text-2xl font-bold text-blue-600">{{ userProfile.friends.length }}</div>
                <div class="text-sm text-gray-500">Znajomych</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">
                  {{ userProfile.provider === 'google' ? 'Google' : userProfile.provider === 'facebook' ? 'Facebook' : 'Lokalny' }}
                </div>
                <div class="text-sm text-gray-500">Provider</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-purple-600">
                  {{ userProfile.role === 'admin' ? 'Admin' : 'User' }}
                </div>
                <div class="text-sm text-gray-500">Rola</div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div v-if="authStore.user && authStore.user.username !== userProfile.username" class="flex justify-center md:justify-start space-x-4">
              <button
                  v-if="!isFriend"
                  @click="handleAddFriend"
                  :disabled="actionLoading"
                  class="btn-primary flex items-center"
              >
                <svg v-if="actionLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
                Dodaj do znajomych
              </button>
              <button
                  v-else
                  @click="handleRemoveFriend"
                  :disabled="actionLoading"
                  class="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 flex items-center"
              >
                <svg v-if="actionLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
                Usuń ze znajomych
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Friends List -->
      <div v-if="userProfile.friends.length > 0" class="card p-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
          Znajomi ({{ userProfile.friends.length }})
        </h2>

        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <NuxtLink
              v-for="friend in userProfile.friends"
              :key="friend.id"
              :to="`/profile/${friend.username}`"
              class="bg-gradient-to-br from-white to-gray-50 rounded-lg p-4 shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100 hover:border-blue-200 transform hover:-translate-y-1 group"
          >
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <img
                    v-if="friend.avatar_url"
                    :src="friend.avatar_url"
                    :alt="friend.full_name"
                    class="h-12 w-12 rounded-full object-cover ring-2 ring-white shadow-md group-hover:ring-blue-200 transition-all"
                >
                <div
                    v-else
                    class="h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-semibold text-lg shadow-md"
                >
                  {{ friend.full_name.charAt(0).toUpperCase() }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-lg font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                  {{ friend.full_name }}
                </p>
                <p class="text-sm text-gray-600 truncate">
                  @{{ friend.username }}
                </p>
              </div>
              <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- No Friends Message -->
      <div v-else class="card p-8 text-center">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Brak znajomych</h3>
        <p class="text-gray-600">
          {{ userProfile.username === authStore.user?.username ? 'Nie masz jeszcze żadnych znajomych.' : `${userProfile.full_name} nie ma jeszcze żadnych znajomych.` }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UserProfile } from '~/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const userProfile = ref<UserProfile | null>(null)
const loading = ref(true)
const error = ref('')
const actionLoading = ref(false)

const username = computed(() => route.params.username as string)

const isFriend = computed(() => {
  if (!authStore.user || !userProfile.value) return false
  return userProfile.value.friends.some(friend => friend.username === authStore.user?.username)
})

const fetchUserProfile = async () => {
  try {
    loading.value = true
    error.value = ''
    userProfile.value = await authStore.fetchUserProfile(username.value)
  } catch (err: any) {
    error.value = err.data?.detail || 'Nie udało się pobrać profilu użytkownika'
  } finally {
    loading.value = false
  }
}

const handleAddFriend = async () => {
  if (!authStore.isAuthenticated) {
    await navigateTo('/login')
    return
  }

  try {
    actionLoading.value = true
    await authStore.addFriend(username.value)
    // Refresh profile to update friends list
    await fetchUserProfile()
  } catch (err: any) {
    error.value = err.data?.detail || 'Nie udało się dodać znajomego'
  } finally {
    actionLoading.value = false
  }
}

const handleRemoveFriend = async () => {
  if (!authStore.isAuthenticated) {
    await navigateTo('/login')
    return
  }

  try {
    actionLoading.value = true
    await authStore.removeFriend(username.value)
    // Refresh profile to update friends list
    await fetchUserProfile()
  } catch (err: any) {
    error.value = err.data?.detail || 'Nie udało się usunąć znajomego'
  } finally {
    actionLoading.value = false
  }
}

// Load user profile on mount and when username changes
watch(username, fetchUserProfile, { immediate: true })

// Set page title
useHead({
  title: computed(() => {
    if (userProfile.value) {
      return `${userProfile.value.full_name} (@${userProfile.value.username}) - OAuth App`
    }
    return 'Profil użytkownika - OAuth App'
  })
})
</script>