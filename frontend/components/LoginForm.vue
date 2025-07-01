<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full space-y-8 animate-fade-in">
      <div class="text-center">
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          Zaloguj się do aplikacji
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Wybierz sposób logowania
        </p>
      </div>

      <div class="card p-8 space-y-6">
        <!-- Google Login -->
        <button
            @click="handleGoogleLogin"
            :disabled="loading"
            class="w-full flex justify-center items-center px-4 py-3 border border-transparent text-sm font-medium rounded-lg text-white bg-red-500 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-0.5 transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          <span v-if="!loading">Zaloguj przez Google</span>
          <span v-else>Logowanie...</span>
        </button>

        <!-- Facebook Login -->
        <button
            @click="handleFacebookLogin"
            :disabled="loading"
            class="w-full flex justify-center items-center px-4 py-3 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-0.5 transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          <span v-if="!loading">Zaloguj przez Facebook</span>
          <span v-else>Logowanie...</span>
        </button>

        <div v-if="error" class="text-red-600 text-sm text-center animate-bounce-in">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const config = useRuntimeConfig()

const loading = ref(false)
const error = ref('')

// Google Login
const handleGoogleLogin = () => {
  loading.value = true
  error.value = ''

  if (typeof google !== 'undefined') {
    google.accounts.id.initialize({
      client_id: config.public.googleClientId,
      callback: handleGoogleResponse
    })
    google.accounts.id.prompt()
  } else {
    error.value = 'Google SDK nie został załadowany'
    loading.value = false
  }
}

const handleGoogleResponse = async (response: any) => {
  try {
    await authStore.loginWithGoogle(response.credential)
  } catch (err: any) {
    error.value = err.message || 'Błąd podczas logowania przez Google'
  } finally {
    loading.value = false
  }
}

// Facebook Login
const handleFacebookLogin = () => {
  loading.value = true
  error.value = ''

  if (typeof FB !== 'undefined') {
    FB.login((response: any) => {
      if (response.authResponse) {
        handleFacebookResponse(response.authResponse.accessToken)
      } else {
        error.value = 'Logowanie przez Facebook zostało anulowane'
        loading.value = false
      }
    }, { scope: 'email' })
  } else {
    // Fallback - redirect to Facebook OAuth
    const facebookUrl = `https://www.facebook.com/v18.0/dialog/oauth?client_id=${config.public.facebookAppId}&redirect_uri=${encodeURIComponent(window.location.origin)}/auth/facebook/callback&scope=email`
    window.location.href = facebookUrl
  }
}

const handleFacebookResponse = async (accessToken: string) => {
  try {
    await authStore.loginWithFacebook(accessToken)
  } catch (err: any) {
    error.value = err.message || 'Błąd podczas logowania przez Facebook'
  } finally {
    loading.value = false
  }
}

// Facebook SDK initialization
onMounted(() => {
  // Load Facebook SDK
  if (!document.getElementById('facebook-jssdk')) {
    const script = document.createElement('script')
    script.id = 'facebook-jssdk'
    script.src = 'https://connect.facebook.net/pl_PL/sdk.js'
    script.onload = () => {
      FB.init({
        appId: config.public.facebookAppId,
        cookie: true,
        xfbml: true,
        version: 'v18.0'
      })
    }
    document.head.appendChild(script)
  }
})
</script>