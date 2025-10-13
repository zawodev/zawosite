<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <!-- Logo/Brand -->
        <div class="footer-brand">
          <div class="brand-link">
            <div class="flex items-center space-x-2 mb-4">
              <img src="/favicon-v2.png" alt="zawosite" class="h-8 w-8">
              <span class="brand-text">zawosite</span>
            </div>
            <p class="brand-description">
              Strona internetowa na moje projekty typu gry czy inne ciekawe rzeczy, które będę miał ochotę tu wrzucić.
            </p>
          </div>
        </div>

        <!-- Social Links -->
        <div class="footer-social">
          <h3 class="social-title">Moje socjale</h3>
          <div class="social-links">
            <a
              href="https://github.com/zawodev"
              target="_blank"
              rel="noopener noreferrer"
              class="social-link"
              title="GitHub"
            >
              <Icon icon="mdi:github" class="w-6 h-6" />
            </a>
            
            <a
              href="https://zawo.itch.io"
              target="_blank"
              rel="noopener noreferrer"
              class="social-link"
              title="itch.io"
            >
              <Icon icon="simple-icons:itchdotio" class="w-6 h-6" />
            </a>
            
            <a
              href="https://leetcode.com/u/zawodev/"
              target="_blank"
              rel="noopener noreferrer"
              class="social-link"
              title="LeetCode"
            >
              <Icon icon="simple-icons:leetcode" class="w-6 h-6" />
            </a>
          </div>
        </div>
      </div>

    </div>

    <!-- Bottom bar -->
    <div class="footer-bottom">
      <div class="footer-bottom-content">
        <p class="copyright">
          © {{ currentYear }} zawosite - wszelkie prawa zastrzeżone
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
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
  @apply py-12 grid grid-cols-1 md:grid-cols-2 gap-8;
}

.footer-brand {
  @apply flex flex-col;
}

.brand-text {
  @apply text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent;
}

.brand-description {
  @apply text-gray-600 dark:text-gray-400 text-sm;
}

.footer-social {
  @apply flex flex-col justify-center items-end;
}

.social-title {
  @apply text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4;
}

.social-links {
  @apply flex space-x-4;
}

.social-link {
  @apply text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700;
}

.footer-bottom {
  @apply bg-gray-100 dark:bg-gray-700 py-4;
}

.footer-bottom-content {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-center;
}

.copyright {
  @apply text-gray-600 dark:text-gray-400 text-sm;
}
</style>