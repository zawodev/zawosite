<template>
  <div class="max-w-3xl mx-auto py-10 space-y-10">
    <!-- Dane użytkownika -->
    <section class="card p-6 flex items-center space-x-6">
      <div>
        <div class="h-20 w-20 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-3xl shadow-lg">
          {{ userProfile?.full_name?.charAt(0).toUpperCase() || '?' }}
        </div>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ userProfile?.full_name || username }}</h2>
        <p class="text-gray-500">@{{ username }}</p>
        <p class="text-gray-400 text-sm mt-1">{{ userProfile?.bio }}</p>
      </div>
    </section>

    <!-- Sekcja znajomych -->
    <section class="card p-6">
      <h3 class="text-xl font-semibold mb-4">Znajomi</h3>
      <div v-if="friends.length > 0" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <NuxtLink v-for="friend in friends" :key="friend.username" :to="`/profile/${friend.username}`" class="flex items-center space-x-3 p-3 rounded-lg hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors">
          <div class="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-lg shadow-md">
            {{ friend.full_name.charAt(0).toUpperCase() }}
          </div>
          <div>
            <div class="font-semibold text-gray-900 dark:text-gray-100">{{ friend.full_name }}</div>
            <div class="text-gray-500 text-sm">@{{ friend.username }}</div>
          </div>
        </NuxtLink>
      </div>
      <div v-else class="text-gray-500">Brak znajomych</div>
    </section>

    <!-- Sekcja zaproszeń -->
    <section class="card p-6">
      <h3 class="text-xl font-semibold mb-4">Zaproszenia</h3>
      <div v-if="invitations.length > 0" class="space-y-4">
        <div v-for="invite in invitations" :key="invite.username" class="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <NuxtLink :to="`/profile/${invite.username}`" class="flex items-center space-x-3 group">
            <div class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-base shadow-md">
              {{ invite.full_name.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 transition-colors">{{ invite.full_name }}</div>
              <div class="text-gray-500 text-sm">@{{ invite.username }}</div>
            </div>
          </NuxtLink>
          <div class="flex space-x-2">
            <button @click="acceptInvite(invite.username)" class="btn-primary px-3 py-1 text-sm">Akceptuj</button>
            <button @click="declineInvite(invite.username)" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm">Odrzuć</button>
          </div>
        </div>
      </div>
      <div v-else class="text-gray-500">Brak zaproszeń</div>
    </section>

    <!-- Dodaj przycisk 'Dodaj do znajomych' na profilu innym niż nasz -->
    <section v-if="!isOwnProfile && !isFriend" class="card p-6 mt-4">
      <button @click="sendFriendRequest(username)" class="btn-primary w-full">Dodaj do znajomych</button>
    </section>

    <!-- Sekcja wyszukiwania użytkowników -->
    <section class="card p-6">
      <h3 class="text-xl font-semibold mb-4">Wyszukaj użytkownika</h3>
      <input v-model="searchQuery" type="text" placeholder="Wpisz nick..." class="w-full px-4 py-2 border rounded-lg mb-4" />
      <div v-if="filteredUsers.length > 0" class="space-y-2">
        <div v-for="user in filteredUsers" :key="user.username" class="flex items-center justify-between p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors">
          <NuxtLink :to="`/profile/${user.username}`" class="flex items-center space-x-3 group">
            <div class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-base shadow-md">
              {{ user.full_name.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 transition-colors">{{ user.full_name }}</div>
              <div class="text-gray-500 text-sm">@{{ user.username }}</div>
            </div>
          </NuxtLink>
          <button v-if="!isOwnProfileUser(user) && !isFriendUser(user)" @click="sendFriendRequest(user.username)" class="btn-primary px-3 py-1 text-sm">Dodaj do znajomych</button>
        </div>
      </div>
      <div v-else class="text-gray-500">Brak wyników</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { useRuntimeConfig } from '#imports'

const route = useRoute()
const username = computed(() => route.params.username as string)
const userProfile = ref<any>({
  full_name: 'Jan Kowalski',
  bio: 'Miłośnik gier i programowania.'
}) // Placeholder na dane profilu

const authStore = useAuthStore()
const isOwnProfile = computed(() => authStore.user && authStore.user.username === username.value)
const isFriend = computed(() => friends.value.some(f => f.username === username.value))

// Mockowane dane znajomych
const friends = ref([
  { username: 'ania', full_name: 'Anna Nowak' },
  { username: 'marek', full_name: 'Marek Zieliński' }
])

// Mockowane zaproszenia
const invitations = ref([
  { username: 'piotr', full_name: 'Piotr Wiśniewski' }
])

const searchQuery = ref('')
// Mockowana lista wszystkich użytkowników
const allUsers = ref([
  { username: 'ania', full_name: 'Anna Nowak' },
  { username: 'marek', full_name: 'Marek Zieliński' },
  { username: 'piotr', full_name: 'Piotr Wiśniewski' },
  { username: 'janek', full_name: 'Janek Kowalski' },
  { username: 'gosia', full_name: 'Małgorzata Lewandowska' }
])
const filteredUsers = computed(() => {
  if (!searchQuery.value) return []
  return allUsers.value.filter(u =>
    u.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    u.full_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})
function isOwnProfileUser(user: any) {
  return authStore.user && authStore.user.username === user.username
}
function isFriendUser(user: any) {
  return friends.value.some(f => f.username === user.username)
}

function acceptInvite(username: string) {
  invitations.value = invitations.value.filter(i => i.username !== username)
  // Tu dodaj logikę akceptacji zaproszenia (API)
}
function declineInvite(username: string) {
  invitations.value = invitations.value.filter(i => i.username !== username)
  // Tu dodaj logikę odrzucenia zaproszenia (API)
}

function sendFriendRequest(username: string) {
  // Tu dodaj logikę wysyłania zaproszenia do znajomych (API)
  console.log(`Wysyłanie zaproszenia do ${username}`)
  // Przykład: friends.value.push({ username: username, full_name: 'Nieznany' }) // Mockowanie dodania
}

onMounted(async () => {
  const config = useRuntimeConfig()
  // Pobierz profil użytkownika
  userProfile.value = await $fetch(`${config.public.apiBase}/api/v1/users/${username.value}/`, {
    headers: authStore.token ? { 'Authorization': `Token ${authStore.token}` } : {}
  })
  // Pobierz znajomych
  friends.value = await $fetch(`${config.public.apiBase}/api/v1/users/${username.value}/friends/`, {
    headers: authStore.token ? { 'Authorization': `Token ${authStore.token}` } : {}
  })
  // TODO: pobierz invitations i allUsers jeśli będą endpointy
})
</script>