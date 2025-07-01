<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex-shrink-0">
          <NuxtLink to="/" class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            OAuth App
          </NuxtLink>
        </div>

        <!-- Navigation -->
        <nav class="hidden md:flex space-x-8">
          <NuxtLink to="/dashboard" class="text-gray-700 hover:text-blue-600 transition-colors">
            Dashboard
          </NuxtLink>
          <NuxtLink to="/users" class="text-gray-700 hover:text-blue-600 transition-colors">
            Użytkownicy
          </NuxtLink>
          <NuxtLink v-if="authStore.user" :to="`/profile/${authStore.user.username}`" class="text-gray-700 hover:text-blue-600 transition-colors">
            Mój Profil
          </NuxtLink>
        </nav>

        <!-- User Info & Actions -->
        <div class="flex items-center space-x-4">
          <!-- User Display -->
          <div v-if="authStore.isAuthenticated || authStore.isGuest" class="flex items-center space-x-3">
            <div class="flex items-center space-x-2">
              <img
                  v-if="authStore.user?.avatar_url"
                  :src="authStore.user.avatar_url"
                  :alt="authStore.user.full_name"
                  class="h-8 w-8 rounded-full object-cover ring-2 ring-white shadow-sm"
              >
              <div
                  v-else
                  class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-semibold text-sm shadow-sm"
              >
                {{ authStore.isGuest ? 'G' : authStore.user?.full_name?.charAt(0).toUpperCase() }}
              </div>
              <div class="hidden sm:block">
                <p class="text-sm font-medium text-gray-900">
                  {{ authStore.displayName }}
                </p>
                <p v-if="authStore.user" class="text-xs text-gray-500">
                  {{ authStore.user.role === 'admin' ? 'Administrator' : 'Użytkownik' }}
                </p>
                <p v-else-if="authStore.isGuest" class="text-xs text-gray-500">
                  Gość
                </p>
              </div>
            </div>

            <!-- Logout Button -->
            <button
                @click="handleLogout"
                class="text-gray-500 hover:text-red-600 transition-colors p-2 rounded-md hover:bg-gray-100"
                title="Wyloguj się"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
            </button>
          </div>

          <!-- Login Button for non-authenticated users -->
          <div v-else>
            <NuxtLink
                to="/login"
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Zaloguj się
            </NuxtLink>
          </div>

          <!-- Mobile menu button -->
          <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1 border-t border-gray-200">
          <NuxtLink
              to="/dashboard"
              class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md"
              @click="mobileMenuOpen = false"
          >
            Dashboard
          </NuxtLink>
          <NuxtLink
              to="/users"
              class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md"
              @click="mobileMenuOpen = false"
          >
            Użytkownicy
          </NuxtLink>
          <NuxtLink
              v-if="authStore.user"
              :to="`/profile/${authStore.user.username}`"
              class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md"
              @click="mobileMenuOpen = false"
          >
            Mój Profil
          </NuxtLink>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  mobileMenuOpen.value = false
}

// Close mobile menu when clicking outside
onMounted(() => {
  const handleClickOutside = (event: Event) => {
    const header = document.querySelector('header')
    if (header && !header.contains(event.target as Node)) {
      mobileMenuOpen.value = false
    }
  }

  document.addEventListener('click', handleClickOutside)

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
})
</script>