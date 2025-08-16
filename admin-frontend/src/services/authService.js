import api from './api'

export const authService = {
  async login(credentials) {
    try {
      console.log('🔑 Auth Service - Credenciales recibidas:', credentials)
      
      const payload = {
        username: credentials.usuario,
        password: credentials.contraseña
      }
      
      console.log('📤 Auth Service - Payload enviado al backend:', payload)
      
      const response = await api.post('/auth/login/', payload)
      
      console.log('🎉 Auth Service - Respuesta del backend:', response.data)
      return response.data
    } catch (error) {
      console.error('💥 Auth Service - Error en login:', error)
      console.error('💥 Auth Service - Detalles del error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      throw error
    }
  },

  async refreshToken(refreshToken) {
    try {
      const response = await api.post('/auth/refresh/', {
        refresh: refreshToken
      })
      return response.data
    } catch (error) {
      console.error('Error refreshing token:', error)
      throw error
    }
  },

  async logout() {
    try {
      const token = localStorage.getItem('token')
      if (token) {
        await api.post('/auth/logout/', {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
      }
    } catch (error) {
      console.error('Error en logout:', error)
    }
  },

  isAuthenticated() {
    return !!localStorage.getItem('token')
  },

  getToken() {
    return localStorage.getItem('token')
  },

  getCurrentUser() {
    const userData = localStorage.getItem('user_data')
    return userData ? JSON.parse(userData) : null
  },

  async validateToken(token) {
    try {
      const response = await api.get('/auth/me/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      return { valid: true, user: response.data }
    } catch (error) {
      console.error('Error validando token:', error)
      return { valid: false, user: null }
    }
  },

  async register(userData) {
    try {
      console.log('📝 Auth Service - Iniciando registro:', userData)
      
      const response = await api.post('/auth/register/', userData)
      
      console.log('✅ Auth Service - Registro exitoso:', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('❌ Auth Service - Error en registro:', error)
      
      let errorMessage = 'Error durante el registro'
      
      if (error.response?.data) {
        // Manejar errores específicos del backend
        const { data } = error.response
        if (typeof data === 'string') {
          errorMessage = data
        } else if (data.detail) {
          errorMessage = data.detail
        } else if (data.error) {
          errorMessage = data.error
        } else if (data.non_field_errors) {
          errorMessage = data.non_field_errors.join(', ')
        } else {
          // Manejar errores de validación por campo
          const fieldErrors = []
          Object.keys(data).forEach(field => {
            if (Array.isArray(data[field])) {
              fieldErrors.push(`${field}: ${data[field].join(', ')}`)
            }
          })
          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors.join('\n')
          }
        }
      }
      
      return { success: false, error: errorMessage }
    }
  }
}
