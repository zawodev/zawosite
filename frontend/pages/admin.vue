<template>
  <div class="space-y-6 animate-fade-in bg-white dark:bg-gray-900 min-h-screen py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Wszyscy Użytkownicy
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Przeglądaj profile użytkowników w systemie
        </p>
      </div>

      <!-- Search Bar -->
      <div class="card p-4 bg-white dark:bg-gray-800 mt-6">
        <div class="relative">
          <input
              v-model="searchQuery"
              type="text"
              placeholder="Szukaj użytkowników..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
          >
          <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
      </div>

      <UserList :search-query="searchQuery" />
    </div>
  </div>
</template>

<script setup lang="ts">
const searchQuery = ref('')

// Page metadata
useHead({
  title: 'Panel Administratora - zawosite'
})

// Protect the page - only admins can access
definePageMeta({
  middleware: 'admin'
})
</script>