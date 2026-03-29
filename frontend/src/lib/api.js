import axios from 'axios'

const api = axios.create({
  // Pastikan VITE_API_URL tidak diakhiri dengan /api
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const authStorage = localStorage.getItem('sakti-auth')
    if (authStorage) {
      const authData = JSON.parse(authStorage)
      const token = authData.state?.token
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
        // Cek di console browser: "Request ke /tenants/current pakai token"
        console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, "Auth: Yes");
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Jangan langsung redirect jika error terjadi pada request tenant/auth awal
    // agar tidak terjadi infinite loop redirect
    const isAuthRequest = error.config.url.includes('tenants/current') || error.config.url.includes('login');

    if (error.response?.status === 401 && !isAuthRequest) {
      localStorage.removeItem('sakti-auth')
      // Gunakan ini hanya jika benar-benar ingin paksa logout
      // window.location.href = '/login' 
    }
    return Promise.reject(error)
  }
)

export default api