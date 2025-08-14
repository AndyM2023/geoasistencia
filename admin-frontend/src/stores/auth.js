import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  // Estado
  const isAuthenticated = ref(false)
  const user = ref(null)
  const token = ref(null)

  // Getters
  const isLoggedIn = computed(() => isAuthenticated.value)
  const currentUser = computed(() => user.value)

  // Acciones
  const login = async (username, password) => {
    console.log('🔑 Auth Store - Iniciando login para:', username)
    
    try {
      // USAR API REAL
      const response = await authService.login({ username, password })
      
      console.log('🎉 Auth Store - Login exitoso, datos recibidos:', response)
      
      // Guardar datos de autenticación
      isAuthenticated.value = true
      user.value = response.user
      token.value = response.token
      
      return { success: true, user: response.user }
    } catch (error) {
      console.error('💥 Auth Store - Error en login:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 
               error.response?.data?.message || 
               error.message || 
               'Error desconocido en login'
      }
    }
  }

  const logout = async () => {
    try {
      // USAR API REAL
      await authService.logout()
    } catch (error) {
      console.error('Error en logout:', error)
    } finally {
      // Limpiar estado
      isAuthenticated.value = false
      user.value = null
      token.value = null
    }
  }

  const checkAuth = () => {
    // USAR SERVICIO REAL
    if (authService.isAuthenticated()) {
      const storedUser = authService.getCurrentUser()
      const storedToken = authService.getToken()
      
      if (storedUser && storedToken) {
        isAuthenticated.value = true
        user.value = storedUser
        token.value = storedToken
        return true
      }
    }
    
    return false
  }

  const updateUser = (userData) => {
    user.value = { ...user.value, ...userData }
    
    // Actualizar localStorage
    if (isAuthenticated.value) {
      localStorage.setItem('user_data', JSON.stringify(user.value))
    }
  }

  // Inicializar autenticación al cargar
  const initAuth = () => {
    checkAuth()
  }

  return {
    // Estado
    isAuthenticated,
    user,
    token,
    
    // Getters
    isLoggedIn,
    currentUser,
    
    // Acciones
    login,
    logout,
    checkAuth,
    updateUser,
    initAuth
  }
})
