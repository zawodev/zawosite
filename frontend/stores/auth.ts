import { defineStore } from 'pinia'

export interface User {
    id: number
    email: string
    full_name: string
    avatar_url?: string
    provider: string
    role: 'user' | 'admin'
    is_active: boolean
    created_at: string
    updated_at?: string
}

export interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    users: User[]
}

export const useAuthStore = defineStore('auth', {
    state: (): AuthState => ({
        user: null,
        token: null,
        isAuthenticated: false,
        users: []
    }),

    getters: {
        isAdmin: (state) => state.user?.role === 'admin',
        currentUser: (state) => state.user
    },

    actions: {
        async loginWithGoogle(credential: string) {
            try {
                const config = useRuntimeConfig()
                const response = await $fetch<{ access_token: string; user: User }>(`${config.public.apiBase}/auth/google`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ access_token: credential })
                })

                this.setAuth(response.access_token, response.user)
                await navigateTo('/dashboard')
                return response
            } catch (error) {
                console.error('Google login error:', error)
                throw error
            }
        },

        async loginWithFacebook(accessToken: string) {
            try {
                const config = useRuntimeConfig()
                const response = await $fetch<{ access_token: string; user: User }>(`${config.public.apiBase}/auth/facebook`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ access_token: accessToken })
                })

                this.setAuth(response.access_token, response.user)
                await navigateTo('/dashboard')
                return response
            } catch (error) {
                console.error('Facebook login error:', error)
                throw error
            }
        },

        setAuth(token: string, user: User) {
            this.token = token
            this.user = user
            this.isAuthenticated = true

            // Store in localStorage
            if (import.meta.client) {
                localStorage.setItem('auth_token', token)
                localStorage.setItem('auth_user', JSON.stringify(user))
            }
        },

        async logout() {
            this.token = null
            this.user = null
            this.isAuthenticated = false
            this.users = []

            if (import.meta.client) {
                localStorage.removeItem('auth_token')
                localStorage.removeItem('auth_user')
            }

            await navigateTo('/login')
        },

        async loadFromStorage() {
            if (import.meta.client) {
                const token = localStorage.getItem('auth_token')
                const userStr = localStorage.getItem('auth_user')

                if (token && userStr) {
                    try {
                        const user = JSON.parse(userStr)
                        this.setAuth(token, user)
                    } catch (error) {
                        console.error('Error loading auth from storage:', error)
                        await this.logout()
                    }
                }
            }
        },

        async fetchUsers() {
            try {
                const config = useRuntimeConfig()
                const users = await $fetch<User[]>(`${config.public.apiBase}/users`, {
                    headers: {
                        'Authorization': `Bearer ${this.token}`
                    }
                })
                this.users = users
                return users
            } catch (error) {
                console.error('Error fetching users:', error)
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