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
    
    // Mostrar detalles del error para debugging
    if (error.response) {
      console.error('📊 Error Response Details:')
      console.error('   - Status:', error.response.status)
      console.error('   - Status Text:', error.response.statusText)
      console.error('   - Headers:', error.response.headers)
      console.error('   - Data:', error.response.data)
      
      // Si es un error 400, mostrar más detalles
      if (error.response.status === 400) {
        console.error('🔍 400 Bad Request Details:')
        console.error('   - Request URL:', error.config?.url)
        console.error('   - Request Method:', error.config?.method)
        console.error('   - Request Data:', error.config?.data)
        console.error('   - Request Headers:', error.config?.headers)
        
        // Intentar parsear el error como JSON
        if (error.response.data) {
          try {
            const errorData = typeof error.response.data === 'string' ? JSON.parse(error.response.data) : error.response.data
            console.error('   - Parsed Error Data:', errorData)
            
            // Si hay errores de validación específicos, mostrarlos
            if (errorData && typeof errorData === 'object') {
              Object.keys(errorData).forEach(key => {
                console.error(`   - Field Error [${key}]:`, errorData[key])
              })
            }
          } catch (e) {
            console.error('   - Raw Error Data (could not parse):', error.response.data)
          }
        }
      }
    }
    
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
