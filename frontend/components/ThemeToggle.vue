<template>
  <div class="theme-toggle-wrapper">
    <button
        @click="toggleTheme"
        :aria-label="`Przełącz na tryb ${isDark ? 'jasny' : 'ciemny'}`"
        class="theme-toggle-button group"
        :class="{ 'active': isDark }"
    >
      <!-- Toggle Track -->
      <div class="toggle-track">
        <!-- Toggle Handle -->
        <div class="toggle-handle" :class="{ 'translate-x-6': isDark }">
          <!-- Icon Container -->
          <div class="icon-container">
            <transition name="icon-fade" mode="out-in">
              <SunIcon v-if="!isDark" key="sun" class="toggle-icon sun-icon" />
              <MoonIcon v-else key="moon" class="toggle-icon moon-icon" />
            </transition>
          </div>
        </div>

        <!-- Background Icons -->
        <div class="background-icons">
          <SunIcon class="bg-sun-icon" :class="{ 'opacity-0': isDark }" />
          <MoonIcon class="bg-moon-icon" :class="{ 'opacity-0': !isDark }" />
        </div>
      </div>

      <!-- Tooltip -->
      <div class="tooltip">
        {{ isDark ? 'Tryb jasny' : 'Tryb ciemny' }}
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { SunIcon, MoonIcon } from '@heroicons/vue/24/solid'

// Composables
const colorMode = useColorMode()

// Computed
const isDark = computed(() => colorMode.value === 'dark')

// Methods
const toggleTheme = () => {
  colorMode.preference = isDark.value ? 'light' : 'dark'
}

// Initialize theme on mount
onMounted(() => {
  // Ensure proper initialization
  if (!colorMode.preference) {
    colorMode.preference = 'system'
  }
})
</script>

<style scoped>
.theme-toggle-wrapper {
  @apply relative;
}

.theme-toggle-button {
  @apply relative w-14 h-7 rounded-full transition-all duration-300 ease-in-out;
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50;
  @apply hover:scale-105 active:scale-95;
}

.toggle-track {
  @apply relative w-full h-full rounded-full p-0.5 transition-all duration-300;
  @apply bg-gradient-to-r from-blue-400 to-blue-500;
  @apply dark:bg-gradient-to-r dark:from-slate-700 dark:to-slate-600;
  @apply shadow-inner;
}

.theme-toggle-button:hover .toggle-track {
  @apply shadow-lg;
  @apply bg-gradient-to-r from-blue-500 to-blue-600;
  @apply dark:bg-gradient-to-r dark:from-slate-600 dark:to-slate-500;
}

.toggle-handle {
  @apply relative w-6 h-6 bg-white rounded-full shadow-md;
  @apply transform transition-transform duration-300 ease-in-out;
  @apply flex items-center justify-center;
  @apply dark:bg-slate-800;
}

.theme-toggle-button:hover .toggle-handle {
  @apply shadow-lg scale-105;
}

.icon-container {
  @apply w-4 h-4 flex items-center justify-center;
}

.toggle-icon {
  @apply w-3.5 h-3.5 transition-all duration-200;
}

.sun-icon {
  @apply text-yellow-500;
}

.moon-icon {
  @apply text-blue-400;
}

.background-icons {
  @apply absolute inset-0 flex items-center justify-between px-1.5 pointer-events-none;
}

.bg-sun-icon,
.bg-moon-icon {
  @apply w-3 h-3 transition-opacity duration-300;
}

.bg-sun-icon {
  @apply text-yellow-300/60;
}

.bg-moon-icon {
  @apply text-slate-300/60;
}

.tooltip {
  @apply absolute -top-10 left-1/2 transform -translate-x-1/2;
  @apply bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap;
  @apply opacity-0 pointer-events-none transition-opacity duration-200;
  @apply dark:bg-white dark:text-gray-900;
}

.theme-toggle-button:hover .tooltip {
  @apply opacity-100;
}

/* Icon transition animations */
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all 0.2s ease-in-out;
}

.icon-fade-enter-from {
  opacity: 0;
  transform: scale(0.8) rotate(90deg);
}

.icon-fade-leave-to {
  opacity: 0;
  transform: scale(0.8) rotate(-90deg);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .theme-toggle-button {
    @apply w-12 h-6;
  }

  .toggle-handle {
    @apply w-5 h-5;
  }

  .toggle-handle.translate-x-6 {
    @apply translate-x-5;
  }

  .toggle-icon {
    @apply w-3 h-3;
  }
}
</style>