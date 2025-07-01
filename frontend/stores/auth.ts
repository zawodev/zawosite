import { defineStore } from 'pinia'

export interface User {
    id: number
    email: string
    full_name: string
    username: string
    avatar_url?: string
    bio?: string
    provider: string
    role: 'user' | 'admin'
    is_active: boolean
    created_at: string
    updated_at?: string
}

export interface UserProfile extends User {
    friends: User[]
}

export interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    users: User[]
    isGuest: boolean
}

export const useAuthStore = defineStore('auth', {
    state: (): AuthState => ({
        user: null,
        token: null,
        isAuthenticated: false,
        users: [],
        isGuest: false
    }),

    getters: {
        isAdmin: (state) => state.user?.role === 'admin',
        currentUser: (state) => state.user,
        displayName: (state) => {
            if (state.user) return state.user.username
            if (state.isGuest) return 'Gość'
            return null
        }
    },

    actions: {
        continueAsGuest() {
            this.isGuest = true
        },

        setAuth(token: string, user: User) {
            this.token = token
            this.user = user
            this.isAuthenticated = true
            this.isGuest = false

            // Store in localStorage
            if (import.meta.client) {
                localStorage.setItem('auth_token', token)
                localStorage.setItem('auth_user', JSON.stringify(user))
                localStorage.removeItem('is_guest')
            }
        },

        async logout() {
            this.token = null
            this.user = null
            this.isAuthenticated = false
            this.isGuest = false
            this.users = []

            if (import.meta.client) {
                localStorage.removeItem('auth_token')
                localStorage.removeItem('auth_user')
                localStorage.removeItem('is_guest')
            }

            await navigateTo('/login')
        },

        async loadFromStorage() {
            if (import.meta.client) {
                const token = localStorage.getItem('auth_token')
                const userStr = localStorage.getItem('auth_user')
                const isGuest = localStorage.getItem('is_guest')

                if (token && userStr) {
                    try {
                        const user = JSON.parse(userStr)
                        this.setAuth(token, user)
                    } catch (error) {
                        console.error('Error loading auth from storage:', error)
                        await this.logout()
                    }
                } else if (isGuest === 'true') {
                    this.isGuest = true
                }
            }
        },

        async fetchUsers() {
            try {
                const config = useRuntimeConfig()
                const headers: Record<string, string> = {}

                if (this.token) {
                    headers['Authorization'] = `Bearer ${this.token}`
                }

                const users = await $fetch<User[]>(`${config.public.apiBase}/users`, { headers })
                this.users = users
                return users
            } catch (error) {
                console.error('Error fetching users:', error)
                throw error
            }
        },

        async fetchUserProfile(username: string): Promise<UserProfile> {
            try {
                const config = useRuntimeConfig()
                const headers: Record<string, string> = {}

                if (this.token) {
                    headers['Authorization'] = `Bearer ${this.token}`
                }

                return await $fetch<UserProfile>(`${config.public.apiBase}/users/${username}`, { headers })
            } catch (error) {
                console.error('Error fetching user profile:', error)
                throw error
            }
        },

        async addFriend(username: string) {
            try {
                const config = useRuntimeConfig()
                await $fetch(`${config.public.apiBase}/users/${username}/friend`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`
                    }
                })
            } catch (error) {
                console.error('Error adding friend:', error)
                throw error
            }
        },

        async removeFriend(username: string) {
            try {
                const config = useRuntimeConfig()
                await $fetch(`${config.public.apiBase}/users/${username}/friend`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${this.token}`
                    }
                })
            } catch (error) {
                console.error('Error removing friend:', error)
                throw error
            }
        },

        async fetchMe() {
            try {
                const config = useRuntimeConfig()
                const user = await $fetch<User>(`${config.public.apiBase}/me`, {
                    headers: {
                        'Authorization': `Bearer ${this.token}`
                    }
                })
                this.user = user
                return user
            } catch (error) {
                console.error('Error fetching current user:', error)
                throw error
            }
        }
    }
})