import { create } from 'zustand'
import api from '../lib/api' // sesuaikan dengan path api axios Anda

export const useDashboardStore = create((set) => ({
  stats: null,
  isLoading: false,
  error: null,

  fetchStats: async () => {
    set({ isLoading: true })
    try {
      const response = await api.get('/dashboard/stats/') // ganti dengan endpoint API asli Anda
      set({ stats: response.data, isLoading: false })
    } catch (error) {
      set({ error: 'Gagal mengambil data statistik', isLoading: false })
    }
  }
}))
