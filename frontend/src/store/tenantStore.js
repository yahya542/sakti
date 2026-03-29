import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../lib/api'

export const useTenantStore = create(
  persist(
    (set, get) => ({
      tenant: null,
      isLoading: false,
      error: null,
      theme: {
        primaryColor: '#2563eb',
        secondaryColor: '#7c3aed',
        logo: null,
        appName: 'SAKTI',
      },
      
      fetchTenant: async (subdomain) => {
        set({ isLoading: true })
        try {
          const response = await api.get('tenants/current/')
          const tenant = response.data
          
          set({
            tenant,
            theme: {
              primaryColor: tenant.primary_color || '#2563eb',
              secondaryColor: tenant.secondary_color || '#7c3aed',
              logo: tenant.logo,
              appName: `SAKTI-${tenant.sub_brand_slug?.toUpperCase()}`,
            },
            isLoading: false,
          })
          
          return { success: true, tenant }
        } catch (error) {
          set({
            error: error.message,
            isLoading: false,
          })
          return { success: false, error: error.message }
        }
      },
      
      setTheme: (themeConfig) => {
        set({ theme: { ...get().theme, ...themeConfig } })
      },
      
      getCssVariables: () => {
        const { theme } = get()
        return {
          '--primary-color': theme.primaryColor,
          '--secondary-color': theme.secondaryColor,
        }
      },
      
      updateTenant: async (data) => {
        set({ isLoading: true })
        try {
          const response = await api.patch('tenants/current/', data)
          set({ tenant: response.data, isLoading: false })
          return { success: true }
        } catch (error) {
          set({ error: error.message, isLoading: false })
          return { success: false, error: error.message }
        }
      },
      
      clearTenant: () => {
        set({
          tenant: null,
          theme: {
            primaryColor: '#2563eb',
            secondaryColor: '#7c3aed',
            logo: null,
            appName: 'SAKTI',
          },
        })
      },
    }),
    {
      name: 'sakti-tenant',
      partialize: (state) => ({
        tenant: state.tenant,
        theme: state.theme,
      }),
    }
  )
)