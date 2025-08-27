import api from './api'

export const employeeAuthService = {
  /**
   * Solicitar recuperación de contraseña para un empleado
   * @param {string} email - Email del empleado
   * @returns {Promise<Object>} - Resultado de la operación
   */
  async requestPasswordReset(email) {
    try {
      console.log('🔑 Employee Auth Service - Solicitando recuperación de contraseña para:', email)
      
      const response = await api.post('/employees/password-reset/request_reset/', { email })
      
      console.log('🎉 Employee Auth Service - Respuesta de recuperación:', response.data)
      return { success: true, message: response.data.message }
    } catch (error) {
      console.error('💥 Employee Auth Service - Error en recuperación de contraseña:', error)
      
      if (error.response?.data?.error) {
        return { success: false, error: error.response.data.error }
      }
      
      return { 
        success: false, 
        error: 'Ocurrió un error al solicitar la recuperación. Por favor intenta de nuevo.' 
      }
    }
  },

  /**
   * Validar token de recuperación de contraseña para empleados
   * @param {string} token - Token de recuperación
   * @returns {Promise<Object>} - Resultado de la validación
   */
  async validateResetToken(token) {
    try {
      console.log('🔑 Employee Auth Service - Validando token de recuperación:', token)
      
      const response = await api.get(`/employees/password-reset/validate_token/?token=${token}`)
      
      console.log('🎉 Employee Auth Service - Token válido:', response.data)
      return { 
        valid: true, 
        user_email: response.data.user_email,
        expires_at: response.data.expires_at
      }
    } catch (error) {
      console.error('💥 Employee Auth Service - Error validando token:', error)
      
      if (error.response?.data?.error) {
        return { valid: false, error: error.response.data.error }
      }
      
      return { valid: false, error: 'Token inválido o expirado' }
    }
  },

  /**
   * Confirmar cambio de contraseña para empleados
   * @param {string} token - Token de recuperación
   * @param {string} newPassword - Nueva contraseña
   * @returns {Promise<Object>} - Resultado de la operación
   */
  async confirmPasswordReset(token, newPassword) {
    try {
      console.log('🔑 Employee Auth Service - Confirmando cambio de contraseña')
      
      const response = await api.post('/employees/password-reset/confirm_reset/', {
        token,
        new_password: newPassword,
        confirm_password: newPassword
      })
      
      console.log('🎉 Employee Auth Service - Contraseña cambiada exitosamente:', response.data)
      return { success: true, message: response.data.message }
    } catch (error) {
      console.error('💥 Employee Auth Service - Error cambiando contraseña:', error)
      
      if (error.response?.data?.error) {
        return { success: false, error: error.response.data.error }
      }
      
      return { 
        success: false, 
        error: 'Ocurrió un error al cambiar la contraseña. Por favor intenta de nuevo.' 
      }
    }
  },

  /**
   * Verificar si un email pertenece a un empleado
   * @param {string} email - Email a verificar
   * @returns {Promise<Object>} - Resultado de la verificación
   */
  async verifyEmployeeEmail(email) {
    try {
      console.log('🔍 Employee Auth Service - Verificando email de empleado:', email)
      
      const response = await api.post('/employees/password-reset/verify_email/', { email })
      
      console.log('✅ Employee Auth Service - Email verificado:', response.data)
      return { success: true, isEmployee: response.data.is_employee }
    } catch (error) {
      console.error('❌ Employee Auth Service - Error verificando email:', error)
      
      if (error.response?.data?.error) {
        return { success: false, error: error.response.data.error }
      }
      
      return { 
        success: false, 
        error: 'Error verificando el email. Por favor intenta de nuevo.' 
      }
    }
  }
}
