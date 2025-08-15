import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isAuthenticated = computed(() => !!token.value)

  const initAuth = () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      token.value = storedToken
      // Aquí podrías validar el token con el backend
    }
  }

  const login = async (usuario, contraseña) => {
    try {
      console.log('🔐 Auth Store - Iniciando login para:', usuario)
      
      const result = await authService.login({ usuario, contraseña })
      console.log('📥 Auth Store - Respuesta del servicio:', result)
      
      if (result.token) {
        console.log('✅ Auth Store - Login exitoso, token recibido')
        token.value = result.token
        user.value = result.user || { usuario }
        localStorage.setItem('token', result.token)
        
        if (result.refresh) {
          localStorage.setItem('refreshToken', result.refresh)
        }
        
        return { success: true }
      } else {
        console.log('❌ Auth Store - Login falló, no hay token')
        return { success: false, error: 'Credenciales inválidas' }
      }
    } catch (error) {
      console.error('💥 Auth Store - Error en login:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error de conexión' 
      }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      const response = await authService.refreshToken(refreshToken)
      if (response.token) {
        token.value = response.token
        localStorage.setItem('token', response.token)
        return true
      }
    } catch (error) {
      console.error('Error refreshing token:', error)
      logout()
      return false
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    initAuth,
    login,
    logout,
    refreshToken
  }
})
