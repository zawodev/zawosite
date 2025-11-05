<template>
  <div class="flex items-center space-x-2" :title="statusText">
    <div class="relative">
      <!-- Status dot -->
      <div 
        class="w-3 h-3 rounded-full transition-all duration-300"
        :class="statusColor"
      />
      <!-- Pulse animation when online -->
      <div 
        v-if="isOnline"
        class="absolute inset-0 w-3 h-3 rounded-full bg-green-400 animate-ping opacity-75"
      />
    </div>
    <span class="text-xs text-gray-600 dark:text-gray-300 hidden sm:inline">
      {{ statusText }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const isOnline = ref<boolean | null>(null)
const isChecking = ref(false)
let checkInterval: NodeJS.Timeout | null = null

const statusColor = computed(() => {
  if (isOnline.value === null) return 'bg-gray-400' // Loading
  return isOnline.value ? 'bg-green-500' : 'bg-red-500'
})

const statusText = computed(() => {
  if (isOnline.value === null) return 'sprawdzam...'
  return isOnline.value ? 'online' : 'offline'
})

const checkBackendStatus = async () => {
  if (isChecking.value) return
  
  isChecking.value = true
  try {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBase || 'http://localhost:8000'
    
    // Try to fetch health check endpoint
    const response = await fetch(`${baseURL}/health/`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000), // 5 second timeout
    })
    
    isOnline.value = response.ok
  } catch (error) {
    console.warn('Backend health check failed:', error)
    isOnline.value = false
  } finally {
    isChecking.value = false
  }
}

onMounted(() => {
  // Check immediately
  checkBackendStatus()
  
  // Check every 20 seconds
  checkInterval = setInterval(checkBackendStatus, 20000)
})

onUnmounted(() => {
  if (checkInterval) {
    clearInterval(checkInterval)
  }
})
</script>
