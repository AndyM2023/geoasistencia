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
      
      // Enriquecer el error con información adicional para mejor manejo
      if (error.response?.data) {
        error.backendError = error.response.data
        error.statusCode = error.response.status
      }
      
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

  async getCurrentUserProfile() {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('No hay token disponible')
      }
      
      console.log('🔍 Llamando a /auth/me/ con token:', token ? 'SÍ' : 'NO')
      const response = await api.get('/auth/me/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      console.log('🔍 Respuesta del backend:', response.data)
      console.log('🔍 Status de la respuesta:', response.status)
      console.log('🔍 Headers de la respuesta:', response.headers)
      
      return { success: true, user: response.data }
    } catch (error) {
      console.error('Error obteniendo perfil del usuario:', error)
      console.error('Detalles del error:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      })
      return { success: false, error: 'Error obteniendo perfil del usuario' }
    }
  },

  // ✅ MÉTODOS PARA RECUPERACIÓN DE CONTRASEÑA
  async requestPasswordReset(email) {
    try {
      console.log('🔑 Auth Service - Solicitando recuperación de contraseña para:', email)
      
      const response = await api.post('/password-reset/request_reset/', { email })
      
      console.log('🎉 Auth Service - Respuesta de recuperación:', response.data)
      return { success: true, message: response.data.message }
    } catch (error) {
      console.error('💥 Auth Service - Error en recuperación de contraseña:', error)
      
      if (error.response?.data?.error) {
        return { success: false, error: error.response.data.error }
      }
      
      return { 
        success: false, 
        error: 'Ocurrió un error al solicitar la recuperación. Por favor intenta de nuevo.' 
      }
    }
  },

  async validateResetToken(token) {
    try {
      console.log('🔑 Auth Service - Validando token de recuperación:', token)
      
      const response = await api.get(`/password-reset/validate_token/?token=${token}`)
      
      console.log('🎉 Auth Service - Token válido:', response.data)
      return { 
        valid: true, 
        user_email: response.data.user_email,
        expires_at: response.data.expires_at
      }
    } catch (error) {
      console.error('💥 Auth Service - Error validando token:', error)
      
      if (error.response?.data?.error) {
        return { valid: false, error: error.response.data.error }
      }
      
      return { valid: false, error: 'Token inválido o expirado' }
    }
  },

  async confirmPasswordReset(token, newPassword) {
    try {
      console.log('🔑 Auth Service - Confirmando cambio de contraseña')
      
      const response = await api.post('/password-reset/confirm_reset/', {
        token,
        new_password: newPassword,
        confirm_password: newPassword
      })
      
      console.log('🎉 Auth Service - Contraseña cambiada exitosamente:', response.data)
      return { success: true, message: response.data.message }
    } catch (error) {
      console.error('💥 Auth Service - Error cambiando contraseña:', error)
      
      if (error.response?.data?.error) {
        return { success: false, error: error.response.data.error }
      }
      
      return { 
        success: false, 
        error: 'Ocurrió un error al cambiar la contraseña. Por favor intenta de nuevo.' 
      }
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
   },

   async changePassword(passwordData) {
     try {
       console.log('🔐 Auth Service - Iniciando cambio de contraseña REAL')
       console.log('🔍 Datos enviados:', {
         current_password: passwordData.current_password ? '***' : 'vacío',
         new_password: passwordData.new_password ? '***' : 'vacío'
       })
       
       // Validar que los datos no estén vacíos
       if (!passwordData.current_password || !passwordData.new_password) {
         throw new Error('Se requieren tanto la contraseña actual como la nueva')
       }
       
       // Validar longitud de nueva contraseña
       if (passwordData.new_password.length < 8) {
         throw new Error('La nueva contraseña debe tener al menos 8 caracteres')
       }
       
       console.log('📤 Enviando petición al backend...')
       const response = await api.post('/auth/change-password/', passwordData)
       
       console.log('✅ Auth Service - Contraseña cambiada exitosamente:', response.data)
       return { success: true, data: response.data }
     } catch (error) {
       console.error('❌ Auth Service - Error cambiando contraseña:', error)
       console.error('🔍 Detalles del error:', {
         status: error.response?.status,
         statusText: error.response?.statusText,
         data: error.response?.data,
         message: error.message,
         config: error.config
       })
       
       let errorMessage = 'Error al cambiar la contraseña'
       
       if (error.response?.data) {
         const { data } = error.response
         if (typeof data === 'string') {
           errorMessage = data
         } else if (data.detail) {
           errorMessage = data.detail
         } else if (data.error) {
           errorMessage = data.error
         } else if (data.current_password) {
           errorMessage = Array.isArray(data.current_password) 
             ? data.current_password.join(', ') 
             : 'La contraseña actual es incorrecta'
         } else if (data.new_password) {
           errorMessage = Array.isArray(data.new_password) 
             ? data.new_password.join(', ') 
             : 'La nueva contraseña no cumple con los requisitos de seguridad'
         } else if (data.non_field_errors) {
           errorMessage = data.non_field_errors.join(', ')
         }
       } else if (error.code === 'ERR_NETWORK') {
         errorMessage = 'Error de conexión. Verifica que el backend esté funcionando'
       } else if (error.response?.status === 404) {
         errorMessage = 'Endpoint no encontrado. Verifica que el backend tenga implementado /auth/change-password/'
       } else if (error.response?.status === 500) {
         errorMessage = 'Error interno del servidor'
       } else if (error.response?.status === 401) {
         errorMessage = 'No autorizado. Verifica que tu sesión sea válida'
       } else if (error.response?.status === 403) {
         errorMessage = 'Acceso denegado. No tienes permisos para cambiar la contraseña'
       }
       
       return { success: false, error: errorMessage }
     }
   },

   // ✅ MÉTODO PARA ACTUALIZAR PERFIL DEL USUARIO
   async updateUserProfile(userData) {
     try {
       console.log('📝 Auth Service - Iniciando actualización de perfil:', userData)
       
       const token = localStorage.getItem('token')
       if (!token) {
         throw new Error('No hay token disponible')
       }
       
       // Validar que los datos requeridos estén presentes
       if (!userData.first_name || !userData.last_name || !userData.email || !userData.username) {
         throw new Error('Todos los campos son requeridos')
       }
       
       // Validar formato de email
       if (!/.+@.+\..+/.test(userData.email)) {
         throw new Error('Formato de email inválido')
       }
       
       // Validar longitud del username
       if (userData.username.length < 3) {
         throw new Error('El nombre de usuario debe tener al menos 3 caracteres')
       }
       
       console.log('📤 Enviando petición de actualización al backend...')
       const response = await api.put('/auth/update_profile/', userData, {
         headers: { Authorization: `Bearer ${token}` }
       })
       
       console.log('✅ Auth Service - Perfil actualizado exitosamente:', response.data)
       
       // Actualizar datos en localStorage si la respuesta incluye información del usuario
       if (response.data.user) {
         localStorage.setItem('user_data', JSON.stringify(response.data.user))
       }
       
       return { success: true, user: response.data.user || response.data }
     } catch (error) {
       console.error('❌ Auth Service - Error actualizando perfil:', error)
       console.error('🔍 Detalles del error:', {
         status: error.response?.status,
         statusText: error.response?.statusText,
         data: error.response?.data,
         message: error.message
       })
       
       let errorMessage = 'Error al actualizar el perfil'
       
       if (error.response?.data) {
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
       } else if (error.code === 'ERR_NETWORK') {
         errorMessage = 'Error de conexión. Verifica que el backend esté funcionando'
       } else if (error.response?.status === 404) {
         errorMessage = 'Endpoint no encontrado. Verifica que el backend tenga implementado /auth/update_profile/'
       } else if (error.response?.status === 500) {
         errorMessage = 'Error interno del servidor'
       } else if (error.response?.status === 401) {
         errorMessage = 'No autorizado. Verifica que tu sesión sea válida'
       } else if (error.response?.status === 403) {
         errorMessage = 'Acceso denegado. No tienes permisos para actualizar el perfil'
       }
       
       return { success: false, error: errorMessage }
     }
   }
}
