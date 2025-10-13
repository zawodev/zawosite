<template>
  <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex-shrink-0">
          <NuxtLink to="/" class="flex items-center space-x-2">
            <img src="/favicon-v2.png" alt="zawosite" class="h-8 w-8">
            <span class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              zawosite
            </span>
          </NuxtLink>
        </div>

        <!-- Navigation -->
        <nav class="hidden md:flex space-x-4">
          <NuxtLink to="/admin" class="nav-btn">
            <span class="nav-btn__icon">
              <AdjustmentsVerticalIcon class="w-5 h-5 mr-1" />
            </span>
            <span>Admin</span>
          </NuxtLink>
          <NuxtLink to="/play" class="nav-btn">
            <span class="nav-btn__icon">
              <PlayIcon class="w-5 h-5 mr-1" />
            </span>
            <span>Gry</span>
          </NuxtLink>
        </nav>

        <!-- User Info & Actions -->
        <div class="flex items-center space-x-4">
          <!-- Theme Toggle -->
          <!-- <ThemeToggle /> -->
          <!-- User Display -->
          <div v-if="authStore.isAuthenticated || authStore.isGuest" class="flex items-center space-x-3">
            <NuxtLink :to="authStore.isGuest ? '/profile/guest' : `/profile/${authStore.user?.username}`" class="flex items-center space-x-2 group">
              <img
                  v-if="authStore.user?.avatar_url"
                  :src="authStore.user.avatar_url"
                  :alt="authStore.user?.username"
                  class="h-8 w-8 rounded-full object-cover ring-2 ring-white shadow-sm"
              >
              <div
                  v-else
                  class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-semibold text-sm shadow-sm"
              >
                {{ authStore.isGuest ? 'G' : authStore.user?.username?.charAt(0).toUpperCase() }}
              </div>
              <div class="hidden sm:block">
                <p class="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                  {{ authStore.displayName }}
                </p>
                <p v-if="userRoleLabel" class="text-xs text-gray-500">
                  {{ userRoleLabel }}
                </p>
                <p v-else-if="authStore.isGuest" class="text-xs text-gray-500">
                  Gość
                </p>
              </div>
            </NuxtLink>
            <!-- Logout Button -->
            <button
                @click="handleLogout"
                class="text-gray-500 hover:text-red-600 transition-colors p-2 rounded-md hover:bg-gray-100"
                title="Wyloguj się"
            >
              <ArrowRightOnRectangleIcon class="w-5 h-5" />
            </button>
          </div>
          <!-- Login Button for non-authenticated users -->
          <div v-else>
            <button
                @click="showLogin = true"
                class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-5 py-2 rounded-lg text-sm font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              Zaloguj się
            </button>
          </div>
          <!-- Przycisk ustawień globalnych -->
          <button @click="showSettings = true" class="text-gray-500 hover:text-blue-600 transition-colors p-2 rounded-md hover:bg-gray-100 flex items-center justify-center" title="Ustawienia">
            <Cog6ToothIcon class="w-5 h-5" />
          </button>

          <!-- Mobile menu button -->
          <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <svg class="w-6 h-6" stroke="currentColor" viewBox="0 0 24 24">
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
              to="/admin"
              class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md"
              @click="mobileMenuOpen = false"
          >
            Panel Admina
          </NuxtLink>
          <NuxtLink
              to="/games"
              class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md"
              @click="mobileMenuOpen = false"
          >
            Gry
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
  <SettingsPanel v-if="showSettings" @close="showSettings = false" />
  <LoginPanel v-if="showLogin" @close="showLogin = false" />
</template>

<script setup lang="ts">
import SettingsPanel from '~/components/SettingsPanel.vue'
import LoginPanel from '~/components/LoginPanel.vue'
import { onMounted, onUnmounted, computed } from 'vue'
import { ArrowRightOnRectangleIcon, Cog6ToothIcon, WrenchScrewdriverIcon, PuzzlePieceIcon } from '@heroicons/vue/24/outline'
import { AdjustmentsVerticalIcon, PlayIcon } from '@heroicons/vue/24/solid'
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)
const showSettings = ref(false)
const showLogin = ref(false)

const userRoleLabel = computed(() => {
  if (authStore.user?.role === 'admin') return 'Administrator'
  if (authStore.user?.role === 'user') return 'Użytkownik'
  return ''
})

const handleLogout = async () => {
  await authStore.logout()
  mobileMenuOpen.value = false
  navigateTo('/')
}

// Close the mobile menu when clicking outside
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

// Obsługa zamykania LoginPanel przez event globalny
const closeLoginPanel = () => { showLogin.value = false }
onMounted(() => {
  window.addEventListener('close-login-panel', closeLoginPanel)
})
onUnmounted(() => {
  window.removeEventListener('close-login-panel', closeLoginPanel)
})
</script>

<style scoped>
.nav-btn {
  @apply flex items-center px-4 py-2 rounded-lg font-semibold transition-all duration-200 shadow-sm bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-700 dark:to-gray-800 text-gray-800 dark:text-white hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-900 dark:hover:to-purple-900 hover:shadow-lg hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50;
  position: relative;
  overflow: hidden;
}
.nav-btn__icon {
  @apply flex items-center;
}
.nav-btn::after {
  content: '';
  position: absolute;
  left: 0; top: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg,rgba(59,130,246,0.08),rgba(168,85,247,0.08));
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 0;
}
.nav-btn:hover::after {
  opacity: 1;
}
.nav-btn:active {
  @apply scale-95;
}
</style>