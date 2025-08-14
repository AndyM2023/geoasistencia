import api from './api'

export const authService = {
  async login(credentials) {
    const loginData = {
      username: credentials.username,
      password: credentials.password
    }
    
    console.log('🔐 Enviando login:', { username: loginData.username, password: '***' })
    
    try {
      const response = await api.post('/auth/login/', loginData)
      console.log('✅ Login exitoso:', response.data)
      
      // Guardar token en localStorage
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token)
        if (response.data.refresh) {
          localStorage.setItem('refresh_token', response.data.refresh)
        }
        localStorage.setItem('user_data', JSON.stringify(response.data.user))
      }
      
      return response.data
    } catch (error) {
      console.error('❌ Error en login:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      throw error
    }
  },
  
  async logout() {
    // Limpiar localStorage
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
    
    return { success: true }
  },
  
  async me() {
    const response = await api.get('/auth/me/')
    return response.data
  },
  
  getCurrentUser() {
    const user = localStorage.getItem('user_data')
    return user ? JSON.parse(user) : null
  },
  
  getToken() {
    return localStorage.getItem('auth_token')
  },
  
  isAuthenticated() {
    return !!this.getToken()
  }
}
