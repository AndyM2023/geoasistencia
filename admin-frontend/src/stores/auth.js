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
    if (isLoading.value || isInitialized.value) {
      console.log('🔄 Auth Store - initAuth ya en progreso o completado, retornando...')
      return isAuthenticated.value
    }
    
    console.log('🚀 Auth Store - Iniciando inicialización de autenticación...')
    isLoading.value = true
    
    try {
      const storedToken = localStorage.getItem('token')
      const storedUser = localStorage.getItem('user_data')
      
      console.log('🔍 Auth Store - Estado del localStorage:')
      console.log(`   - Token presente: ${!!storedToken}`)
      console.log(`   - Usuario presente: ${!!storedUser}`)
      
      if (storedToken) {
        console.log('✅ Auth Store - Token encontrado en localStorage')
        
        // Primero cargar datos del usuario desde localStorage para UI inmediata
        if (storedUser) {
          try {
            user.value = JSON.parse(storedUser)
            console.log('👤 Auth Store - Usuario cargado desde localStorage:', user.value)
          } catch (parseError) {
            console.error('❌ Auth Store - Error parseando usuario del localStorage:', parseError)
            localStorage.removeItem('user_data') // Limpiar datos corruptos
          }
        }
        
        // Validar token con el backend
        console.log('🔐 Auth Store - Validando token con el backend...')
        try {
          const response = await authService.validateToken(storedToken)
          console.log('📥 Auth Store - Respuesta de validación:', response)
          
          if (response.valid) {
            console.log('✅ Auth Store - Token válido, autenticación exitosa')
            token.value = storedToken
            
            // Actualizar datos del usuario si vienen del backend
            if (response.user) {
              user.value = response.user
              localStorage.setItem('user_data', JSON.stringify(response.user))
              console.log('👤 Auth Store - Usuario actualizado desde backend')
            }
            
            isInitialized.value = true
            console.log('✅ Auth Store - Inicialización completada exitosamente')
            return true
          } else {
            console.log('❌ Auth Store - Token inválido según backend')
            logout()
            return false
          }
        } catch (validationError) {
          console.error('❌ Auth Store - Error validando token con backend:', validationError)
          // Si falla la validación, limpiar todo
          logout()
          return false
        }
      } else {
        console.log('ℹ️ Auth Store - No hay token en localStorage')
        // No hay token, marcar como inicializado pero no autenticado
        isInitialized.value = true
        return false
      }
    } catch (error) {
      console.error('💥 Auth Store - Error general en initAuth:', error)
      logout()
      return false
    } finally {
      isLoading.value = false
      console.log('🏁 Auth Store - initAuth completado')
    }
  }

  const login = async (usuario, contraseña) => {
    try {
      console.log('🔐 Auth Store - Iniciando login para:', usuario)
      
      const result = await authService.login({ usuario, contraseña })
      console.log('📥 Auth Store - Respuesta del servicio:', result)
      
      if (result.token) {
        console.log('✅ Auth Store - Login exitoso, token recibido')
        console.log('👤 Auth Store - Datos del usuario:', result.user)
        
        // Establecer token y usuario
        token.value = result.token
        user.value = result.user || { username: usuario }
        localStorage.setItem('token', result.token)
        
        // Guardar información del usuario en localStorage
        if (result.user) {
          localStorage.setItem('user_data', JSON.stringify(result.user))
        }
        
        if (result.refresh) {
          localStorage.setItem('refreshToken', result.refresh)
        }
        
        // Marcar como inicializado después del login exitoso
        isInitialized.value = true
        console.log('✅ Auth Store - Login completado, autenticación inicializada')
        
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
    console.log('🚪 Auth Store - Ejecutando logout...')
    console.log(`   - Estado antes: isAuthenticated=${isAuthenticated.value}, user=${user.value?.username || 'No hay usuario'}`)
    
    // Limpiar estado
    token.value = null
    user.value = null
    isInitialized.value = false
    
    // Limpiar localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user_data')
    
    console.log('✅ Auth Store - Logout completado, estado limpiado')
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
