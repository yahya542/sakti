import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage directly since Zustand persist might have synced
    const authData = JSON.parse(localStorage.getItem('sakti-auth') || '{}')
    const token = authData.state?.token
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data on 401
      localStorage.removeItem('sakti-auth')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API Helper functions
export const apiGet = async (url, params = {}) => {
  const response = await api.get(url, { params })
  return response.data
}

export const apiPost = async (url, data = {}) => {
  const response = await api.post(url, data)
  return response.data
}

export const apiPatch = async (url, data = {}) => {
  const response = await api.patch(url, data)
  return response.data
}

export const apiDelete = async (url) => {
  const response = await api.delete(url)
  return response.data
}