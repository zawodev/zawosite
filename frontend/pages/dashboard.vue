<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Welcome Section -->
    <div class="card p-6">
      <div class="flex items-center space-x-4">
        <div class="flex-shrink-0">
          <img
              v-if="authStore.user?.avatar_url"
              :src="authStore.user.avatar_url"
              :alt="authStore.user.full_name"
              class="h-16 w-16 rounded-full object-cover ring-4 ring-white shadow-lg"
          >
          <div
              v-else
              class="h-16 w-16 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-2xl shadow-lg"
          >
            {{ authStore.user?.full_name?.charAt(0).toUpperCase() }}
          </div>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            Witaj, {{ authStore.user?.full_name }}! 👋
          </h1>
          <p class="text-gray-600 mt-1">
            Jesteś zalogowany jako <span class="font-semibold">{{ authStore.user?.role }}</span>
            przez <span class="font-semibold capitalize">{{ authStore.user?.provider }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card p-6 text-center animate-bounce-in" style="animation-delay: 100ms">
        <div class="text-3xl font-bold text-blue-600">{{ authStore.users.length }}</div>
        <div class="text-gray-600 mt-2">Użytkowników w systemie</div>
      </div>

      <div class="card p-6 text-center animate-bounce-in" style="animation-delay: 200ms">
        <div class="text-3xl font-bold text-green-600">
          {{ authStore.users.filter(u => u.is_active).length }}
        </div>
        <div class="text-gray-600 mt-2">Aktywnych użytkowników</div>
      </div>

      <div class="card p-6 text-center animate-bounce-in" style="animation-delay: 300ms">
        <div class="text-3xl font-bold text-purple-600">
          {{ authStore.users.filter(u => u.role === 'admin').length }}
        </div>
        <div class="text-gray-600 mt-2">Administratorów</div>
      </div>
    </div>

    <!-- User List -->
    <UserList />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const authStore = useAuthStore()
</script>