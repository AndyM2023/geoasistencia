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
  }
}
