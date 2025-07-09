<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <!-- Logo/Brand -->
        <div class="footer-brand">
          <NuxtLink to="/" class="brand-link">
            <span class="brand-text">OAuth App</span>
          </NuxtLink>
          <p class="brand-description">
            Nowoczesna aplikacja z autentykacją SSO
          </p>
        </div>

        <!-- Links -->
        <div class="footer-links">
          <div class="link-group">
            <h3 class="link-group-title">Nawigacja</h3>
            <ul class="link-list">
              <li><NuxtLink to="/dashboard" class="footer-link">Dashboard</NuxtLink></li>
              <li><NuxtLink to="/users" class="footer-link">Użytkownicy</NuxtLink></li>
              <li v-if="authStore.user">
                <NuxtLink :to="`/profile/${authStore.user.username}`" class="footer-link">
                  Mój Profil
                </NuxtLink>
              </li>
            </ul>
          </div>

          <div class="link-group">
            <h3 class="link-group-title">Informacje</h3>
            <ul class="link-list">
              <li><a href="#" class="footer-link">O aplikacji</a></li>
              <li><a href="#" class="footer-link">Polityka prywatności</a></li>
              <li><a href="#" class="footer-link">Warunki użytkowania</a></li>
            </ul>
          </div>

          <div class="link-group">
            <h3 class="link-group-title">Kontakt</h3>
            <ul class="link-list">
              <li><a href="mailto:support@example.com" class="footer-link">Wsparcie</a></li>
              <li><a href="#" class="footer-link">Dokumentacja</a></li>
              <li><a href="#" class="footer-link">GitHub</a></li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="footer-bottom">
        <div class="footer-bottom-content">
          <p class="copyright">
            © {{ currentYear }} OAuth App. Wszystkie prawa zastrzeżone.
          </p>
          <div class="theme-info">
            <span class="theme-text">Motyw:</span>
            <span class="theme-badge">{{ colorMode.value === 'dark' ? '🌙 Ciemny' : '☀️ Jasny' }}</span>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const colorMode = useColorMode()

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.footer {
  @apply bg-white border-t border-gray-200 mt-auto;
  @apply dark:bg-gray-800 dark:border-gray-700;
  @apply transition-colors duration-200;
}

.footer-container {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.footer-content {
  @apply py-12 grid grid-cols-1 md:grid-cols-4 gap-8;
}

.footer-brand {
  @apply md:col-span-1;
}

.brand-link {
  @apply inline-block mb-4;
}

.brand-text {
  @apply text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent;
}

.brand-description {
  @apply text-gray-600 dark:text-gray-400 text-sm;
}

.footer-links {
  @apply md:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-8;
}

.link-group-title {
  @apply text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4;
}

.link-list {
  @apply space-y-2;
}

.footer-link {
  @apply text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 transition-colors;
}
.footer-bottom {
  @apply bg-gray-100 dark:bg-gray-700 py-4;
}

</style>