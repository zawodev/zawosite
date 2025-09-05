<template>
  <div class="max-w-6xl mx-auto py-10 px-4">
    <h1 class="text-3xl font-bold mb-8 text-center">Lista gier</h1>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
      <NuxtLink
        v-for="game in games" :key="game.id"
        :to="game.url"
        class="relative group bg-white dark:bg-gray-800 rounded-3xl shadow-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:-translate-y-1"
      >
        <div class="h-48 w-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
          <img v-if="game.image" :src="game.image" :alt="game.title" class="object-cover w-full h-full transition-transform duration-500 group-hover:scale-110" />
          <div v-else class="text-gray-400 text-6xl">🎮</div>
        </div>
        <div class="p-6">
          <h2 class="text-xl font-bold mb-2 text-gray-900 dark:text-gray-100 group-hover:text-blue-600 transition-colors">{{ game.title }}</h2>
          <p class="text-xs text-gray-600 dark:text-gray-300 mb-4">{{ game.description }}</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="tag in game.tags" :key="tag.text" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200">
              <component :is="tag.icon" class="w-4 h-4 mr-1" />
              {{ tag.text }}
            </span>
          </div>
        </div>
        <div class="absolute inset-0 bg-blue-50 dark:bg-blue-900 opacity-0 group-hover:opacity-10 transition-opacity duration-300 pointer-events-none"></div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UserGroupIcon, UserIcon } from '@heroicons/vue/24/solid'

const games = ref([
  {
    id: 1,
    title: 'zawomons',
    description: 'coś jak pokemony + heroes of might and magic 5 + shakes and fidget. Zbieraj, trenuj i walcz zawomonsami w turowych bitwach lokalnie i online.',
    image: '/games/zawomons/thumbnail.jpg',
    tags: [
      { icon: UserGroupIcon, text: 'Multiplayer' },
      { icon: UserIcon, text: 'Singleplayer' }
    ],
    url: '/play/zawomons'
  },
  {
    id: 2,
    title: 'Cleaning Time!',
    description: 'Gra zręcznościowa opowiadająca historię energicznego przedszkolaka, który ma ambicję posprzątać wszystkie zabawki w całym przedszkolu (sam), podczas gdy jego koledzy i koleżanki toczą własne boje w poszukiwaniu swych utraconych chromosomów.',
    image: '/games/cleaning-time/thumbnail.jpg',
    tags: [
      { icon: UserIcon, text: 'Singleplayer' }
    ],
    url: '/play/cleaning-time'
  },
  {
    id: 3,
    title: 'The Last Raccoon',
    description: 'Ostatni ocalały szop w świecie pozbawionym brudu. Obroń elektryczny samochód jego wybawiciela, stawiaj wieżyczki i pilnuj by nie padły z głodu na brak prądu. Tower defense w brudnym klimacie zbyt czystych miast.',
    image: '/games/the-last-raccoon/thumbnail.jpg',
    tags: [
      { icon: UserIcon, text: 'Singleplayer' }
    ],
    url: '/play/the-last-raccoon'
  }
])
</script>

<style scoped>
.group:hover .group-hover\:scale-110 {
  transform: scale(1.10);
}
</style>
