<template>
  <client-only>
    <button
        @click="toggleTheme"
        :aria-label="`Switch to ${nextTheme} mode`"
        class="w-12 h-6 flex items-center justify-start rounded-full p-1 bg-gray-300 dark:bg-gray-500 transition-colors duration-300"
    >
      <div
          class="w-4 h-4 bg-white rounded-full shadow transform transition-transform duration-300"
          :class="isDark ? 'translate-x-6' : 'translate-x-0'"
      >
        <component
            :is="isDark ? MoonIcon : SunIcon"
            class="w-3 h-3 text-yellow-500 m-auto mt-0.5"
        />
      </div>
    </button>
  </client-only>
</template>

<script setup lang="ts">
import { useColorMode } from '#imports'
import { computed } from 'vue'
import { SunIcon, MoonIcon } from '@heroicons/vue/24/solid'

const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')
const nextTheme = computed(() => isDark.value ? 'light' : 'dark')

function toggleTheme() {
  colorMode.preference = nextTheme.value
}
</script>
