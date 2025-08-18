import axios from 'axios'

// URL del backend Django - CORREGIDO para apuntar al backend
const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutos para procesar 50 fotos con embeddings
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    console.log('🔍 API Interceptor - Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: config.baseURL + config.url,
      hasToken: !!token,
      tokenPreview: token ? `${token.substring(0, 20)}...` : 'NO'
    })
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('✅ Token agregado a headers:', config.headers.Authorization.substring(0, 30) + '...')
      console.log('🔍 Headers completos que se enviarán:', config.headers)
    } else {
      console.log('⚠️ No hay token disponible para la petición')
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
