import axios from 'axios'

// Usar el proxy de Vite configurado
const API_BASE_URL = '/app'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  }
)

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('❌ API Error:', error.config?.method?.toUpperCase(), error.config?.url, error.response?.status)
    
    if (error.response?.status === 401) {
      // Token expirado, solo limpiar - dejar que Vue Router maneje la redirección
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      
      // Emitir evento personalizado para que el auth store lo maneje
      window.dispatchEvent(new CustomEvent('auth:logout'))
    }
    return Promise.reject(error)
  }
)

export default api
