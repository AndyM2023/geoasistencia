import { useNotificationStore } from '../stores/notifications'

/**
 * Composable para usar el sistema de notificaciones
 * Proporciona una API simplificada para mostrar notificaciones
 */
export function useNotifications() {
  const notificationStore = useNotificationStore()

  /**
   * Mostrar notificación de éxito
   * @param {string} message - Mensaje principal
   * @param {Object} options - Opciones adicionales
   */
  const showSuccess = (message, options = {}) => {
    return notificationStore.showSuccess(message, options)
  }

  /**
   * Mostrar notificación de error
   * @param {string} message - Mensaje principal
   * @param {Object} options - Opciones adicionales
   */
  const showError = (message, options = {}) => {
    return notificationStore.showError(message, options)
  }

  /**
   * Mostrar notificación de información
   * @param {string} message - Mensaje principal
   * @param {Object} options - Opciones adicionales
   */
  const showInfo = (message, options = {}) => {
    return notificationStore.showInfo(message, options)
  }

  /**
   * Mostrar notificación de advertencia
   * @param {string} message - Mensaje principal
   * @param {Object} options - Opciones adicionales
   */
  const showWarning = (message, options = {}) => {
    return notificationStore.showWarning(message, options)
  }

  /**
   * Mostrar notificación de carga
   * @param {string} message - Mensaje principal
   * @param {Object} options - Opciones adicionales
   */
  const showLoading = (message, options = {}) => {
    return notificationStore.showLoading(message, options)
  }

  /**
   * Mostrar notificación personalizada
   * @param {string} type - Tipo de notificación
   * @param {string} message - Mensaje principal
   * @param {Object} options - Opciones adicionales
   */
  const showNotification = (type, message, options = {}) => {
    return notificationStore.showNotification(type, message, options)
  }

  /**
   * Remover notificación específica
   * @param {number} id - ID de la notificación
   */
  const removeNotification = (id) => {
    notificationStore.removeNotification(id)
  }

  /**
   * Limpiar todas las notificaciones
   */
  const clearAll = () => {
    notificationStore.clearAll()
  }

  /**
   * Limpiar notificaciones por tipo
   * @param {string} type - Tipo de notificación
   */
  const clearByType = (type) => {
    notificationStore.clearByType(type)
  }

  /**
   * Verificar si hay notificaciones activas
   */
  const hasActiveNotifications = () => {
    return notificationStore.hasActiveNotifications()
  }

  /**
   * Obtener estadísticas de notificaciones
   */
  const getStats = () => {
    return notificationStore.getStats()
  }

  /**
   * Mostrar notificación de error de ubicación
   * @param {Object} errorData - Datos del error de ubicación
   */
  const showLocationError = (errorData) => {
    const { error_type, message, distance_meters, area_radius, area_name } = errorData
    
    let title = 'Error de Ubicación'
    let details = null
    
    switch (error_type) {
      case 'location_out_of_range':
        title = '📍 Ubicación Fuera del Área'
        details = `Estás a ${distance_meters}m del centro del área '${area_name}' (máximo ${area_radius}m)`
        break
      case 'location_not_available':
        title = '📍 Ubicación No Disponible'
        details = 'No se pudo obtener tu ubicación GPS'
        break
      case 'wrong_area_assignment':
        title = '🏢 Área Incorrecta'
        details = 'No tienes permisos para esta área'
        break
      case 'area_inactive':
        title = '🏢 Área Inactiva'
        details = 'Esta área no está disponible actualmente'
        break
      case 'invalid_coordinates':
        title = '📍 Coordenadas Inválidas'
        details = 'Las coordenadas obtenidas no son válidas'
        break
      default:
        title = '📍 Error de Ubicación'
        details = message
    }
    
    return showError(message, {
      title,
      details,
      icon: 'mdi-map-marker-alert',
      duration: 12000, // 12 segundos para errores de ubicación
      closable: true
    })
  }

  /**
   * Mostrar notificación de éxito de asistencia
   * @param {Object} attendanceData - Datos de la asistencia
   * @param {Object} locationInfo - Información de ubicación
   */
  const showAttendanceSuccess = (attendanceData, locationInfo = null) => {
    const { action_type, employee_name } = attendanceData
    
    let title = '✅ Asistencia Registrada'
    let message = ''
    let icon = 'mdi-check-circle'
    
    switch (action_type) {
      case 'entrada':
        title = '✅ Entrada Registrada'
        message = `Entrada registrada exitosamente para ${employee_name}`
        icon = 'mdi-login'
        break
      case 'salida':
        title = '⏰ Salida Registrada'
        message = `Salida registrada exitosamente para ${employee_name}`
        icon = 'mdi-logout'
        break
      case 'completo':
        title = 'ℹ️ Estado Completo'
        message = `${employee_name} ya tiene entrada y salida registradas para hoy`
        icon = 'mdi-information'
        break
      default:
        title = '✅ Asistencia Registrada'
        message = `Asistencia registrada exitosamente para ${employee_name}`
    }
    
    // Agregar información de distancia si está disponible
    let details = null
    if (locationInfo?.distance_meters) {
      details = `Ubicación verificada a ${locationInfo.distance_meters}m del centro del área`
    }
    
    return showSuccess(message, {
      title,
      details,
      icon,
      duration: 8000
    })
  }

  /**
   * Mostrar notificación de progreso de cámara
   * @param {string} status - Estado de la cámara
   */
  const showCameraStatus = (status) => {
    // Limpiar notificaciones de cámara anteriores antes de mostrar una nueva
    const { clearByType } = useNotifications()
    clearByType('info') // Las notificaciones de cámara son de tipo 'info'
    
    switch (status) {
      case 'starting':
        return showLoading('🎬 Iniciando cámara...', {
          title: 'Cámara',
          icon: 'mdi-camera',
          autoHide: false,
          closable: false,
          duration: 15000 // 15 segundos máximo para evitar que se atasque
        })
      case 'active':
        return showInfo('📹 Cámara activa', {
          title: 'Cámara',
          icon: 'mdi-camera',
          duration: 3000
        })
      case 'error':
        return showError('❌ Error en la cámara', {
          title: 'Cámara',
          icon: 'mdi-camera-off',
          duration: 8000
        })
      default:
        return showInfo(status, {
          title: 'Cámara',
          icon: 'mdi-camera'
        })
    }
  }

  /**
   * Mostrar notificación de ubicación con limpieza automática
   * @param {string} status - Estado de la ubicación
   */
  const showLocationStatus = (status) => {
    // Limpiar notificaciones de ubicación anteriores
    const { clearByType } = useNotifications()
    clearByType('info')
    
    switch (status) {
      case 'getting':
        return showLoading('📍 Obteniendo tu ubicación GPS...', {
          title: 'Ubicación',
          icon: 'mdi-map-marker',
          autoHide: false,
          closable: false,
          duration: 20000 // 20 segundos máximo
        })
      case 'success':
        return showInfo('📍 Ubicación obtenida correctamente', {
          title: 'Ubicación',
          icon: 'mdi-map-marker',
          duration: 4000
        })
      case 'error':
        return showError('❌ Error obteniendo ubicación', {
          title: 'Ubicación',
          icon: 'mdi-map-marker-alert',
          duration: 8000
        })
      default:
        return showInfo(status, {
          title: 'Ubicación',
          icon: 'mdi-map-marker'
        })
    }
  }

  return {
    // Métodos principales
    showSuccess,
    showError,
    showInfo,
    showWarning,
    showLoading,
    showNotification,
    
    // Métodos de gestión
    removeNotification,
    clearAll,
    clearByType,
    hasActiveNotifications,
    getStats,
    
    // Métodos especializados
    showLocationError,
    showAttendanceSuccess,
    showCameraStatus,
    showLocationStatus
  }
}

export default useNotifications
