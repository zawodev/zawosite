<template>
  <div class="max-w-7xl mx-auto py-10 px-4">
    <h1 class="text-3xl font-bold mb-8 text-center">Lista gier</h1>
    
    <!-- Filters and Search Bar -->
    <div class="mb-8 space-y-4">
      <!-- Search Bar -->
      <div class="relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Szukaj gier po nazwie lub opisie..."
          class="w-full px-4 py-3 pl-12 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
        />
        <MagnifyingGlassIcon class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <button
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- Filters Row -->
      <div class="flex flex-wrap gap-4 items-center justify-between">
        <!-- Tag Filters -->
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in availableTags"
            :key="tag"
            @click="toggleTag(tag)"
            class="px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200"
            :class="selectedTags.includes(tag)
              ? 'bg-blue-600 text-white shadow-md'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'"
          >
            {{ tag }}
          </button>
          <button
            v-if="selectedTags.length > 0"
            @click="selectedTags = []"
            class="px-4 py-2 rounded-lg text-sm font-semibold bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-800 transition-all"
          >
            Wyczyść filtry
          </button>
        </div>

        <!-- Sort Toggle -->
        <button
          @click="toggleSortOrder"
          class="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-all font-semibold"
        >
          <ArrowsUpDownIcon class="w-5 h-5" />
          {{ sortOrder === 'desc' ? 'Najnowsze' : 'Najstarsze' }}
        </button>
      </div>

      <!-- Results Count -->
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Znaleziono: <span class="font-semibold">{{ filteredGames.length }}</span> {{ filteredGames.length === 1 ? 'gra' : 'gier' }}
      </div>
    </div>

    <!-- Games Grid -->
    <div v-if="filteredGames.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
      <NuxtLink
        v-for="game in filteredGames"
        :key="game.id"
        :to="game.url"
        class="relative group bg-white dark:bg-gray-800 rounded-3xl shadow-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:-translate-y-1"
      >
        <div class="h-48 w-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
          <img v-if="game.image" :src="game.image" :alt="game.title" class="object-cover w-full h-full transition-transform duration-500 group-hover:scale-110" />
          <div v-else class="text-gray-400 text-6xl">🎮</div>
        </div>
        <div class="p-6">
          <div class="flex justify-between items-start mb-2">
            <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 transition-colors">{{ game.title }}</h2>
            <span v-if="game.category" class="text-xs px-2 py-1 rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 font-semibold">
              {{ game.category }}
            </span>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-300 mb-4 line-clamp-3">{{ game.description }}</p>
          <div class="flex flex-wrap gap-2 mb-3">
            <span v-for="tag in game.tags" :key="tag.text" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200">
              <component :is="tag.icon" class="w-4 h-4 mr-1" />
              {{ tag.text }}
            </span>
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400">
            Dodano: {{ formatDate(game.addedDate) }}
          </div>
        </div>
        <div class="absolute inset-0 bg-blue-50 dark:bg-blue-900 opacity-0 group-hover:opacity-10 transition-opacity duration-300 pointer-events-none"></div>
      </NuxtLink>
    </div>

    <!-- No Results -->
    <div v-else class="text-center py-16">
      <div class="text-6xl mb-4">🎮</div>
      <h3 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Nie znaleziono gier</h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Spróbuj zmienić kryteria wyszukiwania lub wyczyść filtry
      </p>
      <button
        @click="clearFilters"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-semibold"
      >
        Wyczyść wszystkie filtry
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { GAMES } from '~/config/games'
import { MagnifyingGlassIcon, XMarkIcon, ArrowsUpDownIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()

// State
const searchQuery = ref('')
const selectedTags = ref<string[]>([])
const sortOrder = ref<'asc' | 'desc'>('desc') // desc = newest first

// Initialize from URL query params
onMounted(() => {
  const tagParam = route.query.tag
  if (tagParam) {
    const tag = Array.isArray(tagParam) ? tagParam[0] : tagParam
    if (tag && !selectedTags.value.includes(tag)) {
      selectedTags.value.push(tag)
    }
  }
})

// Watch for route changes (if user navigates with browser back/forward)
watch(() => route.query.tag, (newTag) => {
  if (newTag) {
    const tag = Array.isArray(newTag) ? newTag[0] : newTag
    if (tag && !selectedTags.value.includes(tag)) {
      selectedTags.value = [tag]
    }
  }
})

// Available tags (extract from all games)
const availableTags = computed(() => {
  const tags = new Set<string>()
  GAMES.forEach(game => {
    game.tags.forEach(tag => tags.add(tag.text))
  })
  return Array.from(tags).sort()
})

// Filtered and sorted games
const filteredGames = computed(() => {
  let games = GAMES.map(game => ({
    ...game,
    url: `/play/${game.slug}`
  }))

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    games = games.filter(game =>
      game.title.toLowerCase().includes(query) ||
      game.description.toLowerCase().includes(query) ||
      (game.category && game.category.toLowerCase().includes(query))
    )
  }

  // Filter by tags
  if (selectedTags.value.length > 0) {
    games = games.filter(game =>
      selectedTags.value.every(selectedTag =>
        game.tags.some(tag => tag.text === selectedTag)
      )
    )
  }

  // Sort by date
  games.sort((a, b) => {
    const dateA = new Date(a.addedDate).getTime()
    const dateB = new Date(b.addedDate).getTime()
    return sortOrder.value === 'desc' ? dateB - dateA : dateA - dateB
  })

  return games
})

// Actions
const toggleTag = (tag: string) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
    // Clear query param if tag was removed
    if (route.query.tag === tag) {
      router.replace({ query: {} })
    }
  } else {
    selectedTags.value.push(tag)
  }
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedTags.value = []
  router.replace({ query: {} })
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<style scoped>
.group:hover .group-hover\:scale-110 {
  transform: scale(1.10);
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
