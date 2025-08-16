import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isLoading = ref(false)
  const isInitialized = ref(false)
  const isAuthenticated = computed(() => !!token.value)

  const initAuth = async () => {
    if (isLoading.value || isInitialized.value) return isAuthenticated.value
    
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user_data')
    
    if (storedToken) {
      isLoading.value = true
      try {
        // Primero cargar datos del usuario desde localStorage
        if (storedUser) {
          user.value = JSON.parse(storedUser)
          console.log('👤 Auth Store - Usuario cargado desde localStorage:', user.value)
        }
        
        // Validar token con el backend
        const response = await authService.validateToken(storedToken)
        if (response.valid) {
          token.value = storedToken
          // Actualizar datos del usuario si vienen del backend
          if (response.user) {
            user.value = response.user
            localStorage.setItem('user_data', JSON.stringify(response.user))
          }
          isInitialized.value = true
          return true
        } else {
          // Token inválido, limpiar
          logout()
          return false
        }
      } catch (error) {
        console.error('Error validando token:', error)
        logout()
        return false
      } finally {
        isLoading.value = false
        isInitialized.value = true
      }
    }
    isInitialized.value = true
    return false
  }

  const login = async (usuario, contraseña) => {
    try {
      console.log('🔐 Auth Store - Iniciando login para:', usuario)
      
      const result = await authService.login({ usuario, contraseña })
      console.log('📥 Auth Store - Respuesta del servicio:', result)
      
      if (result.token) {
        console.log('✅ Auth Store - Login exitoso, token recibido')
        console.log('👤 Auth Store - Datos del usuario:', result.user)
        
        token.value = result.token
        user.value = result.user || { usuario }
        localStorage.setItem('token', result.token)
        
        // Guardar información del usuario en localStorage
        if (result.user) {
          localStorage.setItem('user_data', JSON.stringify(result.user))
        }
        
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
    isInitialized.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user_data')
  }

  // Escuchar eventos de logout desde el interceptor de Axios
  if (typeof window !== 'undefined') {
    window.addEventListener('auth:logout', () => {
      logout()
    })
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
    isLoading,
    isInitialized,
    isAuthenticated,
    initAuth,
    login,
    logout,
    refreshToken
  }
})
