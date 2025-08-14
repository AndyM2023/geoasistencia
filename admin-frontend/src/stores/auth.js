import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // Estado
  const isAuthenticated = ref(false)
  const user = ref(null)
  const token = ref(null)

  // Getters
  const isLoggedIn = computed(() => isAuthenticated.value)
  const currentUser = computed(() => user.value)

  // Acciones
  const login = async (email, password) => {
    try {
      // Simular llamada a API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Validar credenciales (ejemplo)
      if (email === 'admin@geoasistencia.com' && password === 'admin123') {
        const userData = {
          id: 1,
          email: email,
          name: 'Administrador',
          role: 'admin'
        }
        
        // Guardar datos de autenticación
        isAuthenticated.value = true
        user.value = userData
        token.value = 'fake-jwt-token-' + Date.now()
        
        // Guardar en localStorage
        localStorage.setItem('auth_token', token.value)
        localStorage.setItem('user_data', JSON.stringify(userData))
        
        return { success: true, user: userData }
      } else {
        throw new Error('Credenciales inválidas')
      }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    // Limpiar estado
    isAuthenticated.value = false
    user.value = null
    token.value = null
    
    // Limpiar localStorage
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    sessionStorage.removeItem('isAuthenticated')
    sessionStorage.removeItem('userEmail')
  }

  const checkAuth = () => {
    // Verificar si hay token en localStorage
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('user_data')
    
    if (storedToken && storedUser) {
      try {
        isAuthenticated.value = true
        user.value = JSON.parse(storedUser)
        token.value = storedToken
        return true
      } catch (error) {
        console.error('Error parsing stored user data:', error)
        logout()
        return false
      }
    }
    
    // Verificar sessionStorage como fallback
    const sessionAuth = sessionStorage.getItem('isAuthenticated')
    const sessionEmail = sessionStorage.getItem('userEmail')
    
    if (sessionAuth === 'true' && sessionEmail) {
      isAuthenticated.value = true
      user.value = {
        id: 1,
        email: sessionEmail,
        name: 'Administrador',
        role: 'admin'
      }
      return true
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
