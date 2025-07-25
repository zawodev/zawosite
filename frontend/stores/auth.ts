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
        refreshToken: null as string | null,
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
        setAuth(token: string, user: User, refreshToken?: string) {
            this.token = token
            this.user = user
            this.isGuest = false
            if (refreshToken) this.refreshToken = refreshToken
            this.saveToStorage()
        },
        setTokens(token: string, refreshToken: string) {
            this.token = token
            this.refreshToken = refreshToken
            this.saveToStorage()
        },
        setUser(user: User) {
            this.user = user
            this.isGuest = false
            this.saveToStorage()
        },
        async refreshTokenIfNeeded() {
            if (!this.refreshToken) throw new Error('Brak refresh tokena')
            const config = useRuntimeConfig()
            try {
                const { access, refresh } = await $fetch<any>('/api/v1/auth/token/refresh/', {
                    method: 'POST',
                    baseURL: config.public.apiBase,
                    body: { refresh: this.refreshToken },
                    headers: { 'Content-Type': 'application/json' }
                })
                this.token = access
                if (refresh) this.refreshToken = refresh
                this.saveToStorage()
                return access
            } catch (err: any) {
                this.logout()
                throw new Error('Sesja wygasła, zaloguj się ponownie')
            }
        },
        saveToStorage() {
            if (import.meta.client) {
                localStorage.setItem('auth_token', this.token || '')
                localStorage.setItem('auth_refresh_token', this.refreshToken || '')
                localStorage.setItem('auth_user', JSON.stringify(this.user))
                localStorage.setItem('auth_guest', JSON.stringify(this.isGuest))
            }
        },
        loadFromStorage() {
            if (import.meta.client) {
                const token = localStorage.getItem('auth_token')
                const refreshToken = localStorage.getItem('auth_refresh_token')
                const userStr = localStorage.getItem('auth_user')
                const guestStr = localStorage.getItem('auth_guest')
                if (token && userStr && userStr !== 'null') {
                    this.token = token
                    this.refreshToken = refreshToken
                    this.user = JSON.parse(userStr)
                    this.isGuest = false
                } else if (guestStr && JSON.parse(guestStr)) {
                    this.token = null
                    this.refreshToken = null
                    this.user = null
                    this.isGuest = true
                }
            }
        },
        clearStorage() {
            if (import.meta.client) {
                localStorage.removeItem('auth_token')
                localStorage.removeItem('auth_refresh_token')
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

            return await $fetch<UserProfile>(`/api/v1/users/${username}`, {
                baseURL: config.public.apiBase,
                headers
            })
        },

        async addFriend(username: string): Promise<void> {
            if (!this.isAuthenticated) {
                throw new Error('Musisz być zalogowany, aby dodać znajomego')
            }

            const config = useRuntimeConfig()

            await $fetch(`/api/v1/users/${username}/friend`, {
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

            await $fetch(`/api/v1/users/${username}/friend`, {
                method: 'DELETE',
                baseURL: config.public.apiBase,
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            })
        },

        async login(identifier: string, password: string) {
            const config = useRuntimeConfig()
            try {
                const { key, user } = await $fetch<any>('/api/v1/auth/login/', {
                    method: 'POST',
                    baseURL: config.public.apiBase,
                    body: { email: identifier, username: identifier, password },
                    headers: { 'Content-Type': 'application/json' }
                })
                this.setAuth(key, user)
                return user
            } catch (err: any) {
                throw new Error(err.data?.non_field_errors?.[0] || err.data?.detail || 'Błąd logowania')
            }
        },

        async register(email: string, username: string, password1: string, password2: string) {
            const config = useRuntimeConfig()
            try {
                const { key, user } = await $fetch<any>('/api/v1/auth/registration/', {
                    method: 'POST',
                    baseURL: config.public.apiBase,
                    body: { email, username, password1, password2 },
                    headers: { 'Content-Type': 'application/json' }
                })
                this.setAuth(key, user)
                return user
            } catch (err: any) {
                throw new Error(err.data?.non_field_errors?.[0] || err.data?.detail || 'Błąd rejestracji')
            }
        },

        async fetchUserInfo() {
            const config = useRuntimeConfig()
            if (!this.token) throw new Error('Brak tokena JWT')
            return await $fetch<User>('/api/v1/auth/user/', {
                baseURL: config.public.apiBase,
                headers: { 'Authorization': `Bearer ${this.token}` }
            })
        },
        logout() {
            this.token = null
            this.refreshToken = null
            this.user = null
            this.isGuest = false
            this.clearStorage()
            return navigateTo('/')
        }
    }
})