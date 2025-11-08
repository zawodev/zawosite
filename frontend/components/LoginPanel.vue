<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 dark:bg-opacity-60">
    <div class="card p-8 max-w-md mx-auto relative bg-white dark:bg-gray-800">
      <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <div class="space-y-6">
        <!-- Header -->
        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {{ isRegister ? 'Załóż konto' : 'Witaj ponownie!' }}
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            {{ isRegister ? 'Utwórz nowe konto, aby korzystać z aplikacji' : 'Zaloguj się, aby uzyskać dostęp do swojego konta' }}
          </p>
        </div>
        <!-- Social Login Buttons -->
        <div class="space-y-4" v-if="!isRegister">
          <a :href="googleLoginUrl" class="w-full flex justify-center items-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-200 font-medium">
            <svg class="w-5 h-5 mr-3" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Kontynuuj z Google
          </a>
          <a :href="facebookLoginUrl" class="w-full flex justify-center items-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-200 font-medium">
            <svg class="w-5 h-5 mr-3" fill="#1877F2" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            Kontynuuj z Facebook
          </a>
        </div>
        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">lub</span>
          </div>
        </div>
        <!-- Formularz logowania/rejestracji -->
        <form @submit.prevent="isRegister ? handleRegister() : handleLogin()" class="space-y-4">
          <div v-if="isRegister">
            <input v-model="registerUsername" type="text" placeholder="Nazwa użytkownika" class="input-field mb-2" required />
            <input v-model="registerPassword1" type="password" placeholder="Hasło" class="input-field mb-2" required />
            <input v-model="registerPassword2" type="password" placeholder="Powtórz hasło" class="input-field mb-2" required />
          </div>
          <div v-else>
            <input v-model="loginUsername" type="text" placeholder="Nazwa użytkownika" class="input-field mb-2" required />
            <input v-model="loginPassword" type="password" placeholder="Hasło" class="input-field mb-2" required />
          </div>
          <button type="submit" :disabled="loading" class="btn-primary w-full">
            <span v-if="loading" class="animate-spin mr-2">⏳</span>
            {{ isRegister ? 'Zarejestruj się' : 'Zaloguj się' }}
          </button>
        </form>
        <!-- Przełącznik trybu -->
        <div class="text-center mt-2">
          <button @click="isRegister = !isRegister" class="text-blue-600 dark:text-blue-400 hover:underline text-sm">
            {{ isRegister ? 'Masz już konto? Zaloguj się' : 'Nie masz konta? Zarejestruj się' }}
          </button>
        </div>
        <!-- Continue as Guest -->
        <button v-if="!isRegister" @click="continueAsGuest" :disabled="loading" class="w-full flex justify-center items-center px-4 py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-400 hover:border-gray-400 dark:hover:border-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors duration-200 font-medium">
          <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
          </svg>
          Kontynuuj jako gość
        </button>
        <!-- Error Message -->
        <div v-if="error" class="mt-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <div class="flex">
            <svg class="w-5 h-5 text-red-400 dark:text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.098 16.5c-.77.833.192 2.5 1.732 2.5z"/>
            </svg>
            <p class="text-red-700 dark:text-red-300 text-sm">{{ error }}</p>
          </div>
        </div>
        <!-- Info -->
        <div class="mt-6 text-center text-xs text-gray-500 dark:text-gray-400">
          Logując się, akceptujesz nasze warunki użytkowania i politykę prywatności
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRuntimeConfig } from '#imports'

const authStore = useAuthStore()
const config = useRuntimeConfig()

const loading = ref(false)
const error = ref('')
const isRegister = ref(false)

// Login form
const loginUsername = ref('')
const loginPassword = ref('')

// Register form
const registerUsername = ref('')
const registerPassword1 = ref('')
const registerPassword2 = ref('')

const googleLoginUrl = computed(() => `${config.public.apiBase}/api/v1/accounts/google/login/?process=login`)
const facebookLoginUrl = computed(() => `${config.public.apiBase}/api/v1/accounts/facebook/login/`)

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''
    await authStore.login(loginUsername.value, loginPassword.value)
    await navigateTo('/')
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('close-login-panel'))
    }, 100)
  } catch (err: any) {
    error.value = err.message || 'Błąd logowania'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (registerPassword1.value !== registerPassword2.value) {
    error.value = 'Hasła nie są zgodne'
    return
  }
  try {
    loading.value = true
    error.value = ''
    await authStore.register(registerUsername.value, registerPassword1.value, registerPassword2.value)
    await navigateTo('/')
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('close-login-panel'))
    }, 100)
  } catch (err: any) {
    error.value = err.message || 'Błąd rejestracji'
  } finally {
    loading.value = false
  }
}

const continueAsGuest = async () => {
  try {
    loading.value = true
    error.value = ''
    authStore.setGuestMode()
    await navigateTo('/')
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('close-login-panel'))
    }, 100)
  } catch (err: any) {
    error.value = err.message || 'Wystąpił błąd podczas ustawiania trybu gość'
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  error.value = ''
})
</script> 