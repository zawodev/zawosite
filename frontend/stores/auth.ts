import { defineStore } from 'pinia'

export interface User {
    id: number
    email: string
    full_name: string
    username: string
    avatar_url?: string
    provider: string
    role: 'user' | 'admin'
    bio?: string
    friends: User[]
}

export interface UserProfile extends User {
    friends: User[]
}

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: null as string | null,
        user: null as User | null,
        isGuest: false
    }),

    getters: {
        isAuthenticated: (state) => !!state.token && !!state.user,
        displayName: (state) => {
            if (state.user) return state.user.full_name
            if (state.isGuest) return 'Gość'
            return 'Niezalogowany'
        }
    },

    actions: {
        setAuth(token: string, user: User) {
            this.token = token
            this.user = user
            this.isGuest = false
            this.saveToStorage()
        },

        setGuestMode() {
            this.token = null
            this.user = null
            this.isGuest = true
            this.saveToStorage()
        },

        logout() {
            this.token = null
            this.user = null
            this.isGuest = false
            this.clearStorage()
            return navigateTo('/login')
        },

        saveToStorage() {
            if (process.client) {
                localStorage.setItem('auth_token', this.token || '')
                localStorage.setItem('auth_user', JSON.stringify(this.user))
                localStorage.setItem('auth_guest', JSON.stringify(this.isGuest))
            }
        },

        loadFromStorage() {
            if (process.client) {
                const token = localStorage.getItem('auth_token')
                const userStr = localStorage.getItem('auth_user')
                const guestStr = localStorage.getItem('auth_guest')

                if (token && userStr && userStr !== 'null') {
                    this.token = token
                    this.user = JSON.parse(userStr)
                    this.isGuest = false
                } else if (guestStr && JSON.parse(guestStr)) {
                    this.token = null
                    this.user = null
                    this.isGuest = true
                }
            }
        },

        clearStorage() {
            if (process.client) {
                localStorage.removeItem('auth_token')
                localStorage.removeItem('auth_user')
                localStorage.removeItem('auth_guest')
            }
        },

        async fetchUsers(): Promise<User[]> {
            const config = useRuntimeConfig()

            const headers: Record<string, string> = {
                'Content-Type': 'application/json'
            }

            if (this.token) {
                headers['Authorization'] = `Bearer ${this.token}`
            }

            const { data } = await $fetch<{ data: User[] }>('/users', {
                baseURL: config.public.apiBase,
                headers
            })

            return data
        },

        async fetchUserProfile(username: string): Promise<UserProfile> {
            const config = useRuntimeConfig()

            const headers: Record<string, string> = {
                'Content-Type': 'application/json'
            }

            if (this.token) {
                headers['Authorization'] = `Bearer ${this.token}`
            }

            return await $fetch<UserProfile>(`/users/${username}`, {
                baseURL: config.public.apiBase,
                headers
            })
        },

        async addFriend(username: string): Promise<void> {
            if (!this.isAuthenticated) {
                throw new Error('Musisz być zalogowany, aby dodać znajomego')
            }

            const config = useRuntimeConfig()

            await $fetch(`/users/${username}/friend`, {
                method: 'POST',
                baseURL: config.public.apiBase,
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            })
        },

        async removeFriend(username: string): Promise<void> {
            if (!this.isAuthenticated) {
                throw new Error('Musisz być zalogowany, aby usunąć znajomego')
            }

            const config = useRuntimeConfig()

            await $fetch(`/users/${username}/friend`, {
                method: 'DELETE',
                baseURL: config.public.apiBase,
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            })
        }
    }
})