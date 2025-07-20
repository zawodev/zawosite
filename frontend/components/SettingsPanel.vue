<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8 w-full max-w-md relative">
      <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-400 hover:text-red-500">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">Ustawienia</h2>
      <div class="space-y-6">
        <div>
          <h3 class="font-semibold mb-2 text-gray-800 dark:text-gray-200">Motyw</h3>
          <ThemeToggle />
        </div>
        <!-- Tu można dodać kolejne ustawienia globalne -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeToggle from './ThemeToggle.vue'
</script> 