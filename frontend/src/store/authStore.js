import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../lib/api'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (credentials) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post('auth/login/', credentials)
          const { access, user } = response.data
          
          set({
            token: access,
            user: user,
            isAuthenticated: true,
            isLoading: false,
          })
          
          return { success: true }
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Login failed'
          set({
            error: errorMessage,
            isLoading: false,
          })
          return { success: false, error: errorMessage }
        }
      },
      register : async (data) => {
        set({ isLoading: true, error: null })
        try {
          await api.post('auth/register/', data)
          set({ isLoading: false })
          return { success: true }
        } catch (error) {
          const errorMessage = error.response?.data || 'Registration failed'
          set({
            error: errorMessage,
            isLoading: false,
          })
          return { success: false, error: errorMessage }
        }
      }, 
      
      logout: async () => {
        try {
          // Logout tidak memerlukan endpoint khusus, cukup hapus token dari localStorage
          // Jika backend mau menyediakan endpoint logout, bisa ditambah di masa depan
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            error: null,
          })
        }
      },
      
      checkAuth: async () => {
        const { token } = get()
        if (!token) {
          set({ isAuthenticated: false })
          return
        }
        
        set({ isLoading: true })
        try {
          const response = await api.get('/auth/me/')
          set({
            user: response.data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          })
        }
      },
      
      updateUser: (userData) => {
        set({ user: { ...get().user, ...userData } })
      },
      
      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'sakti-auth',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)