import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  // Estado reactivo
  const notifications = ref([])
  const nextId = ref(1)

  // Tipos de notificación disponibles
  const NOTIFICATION_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    INFO: 'info',
    WARNING: 'warning'
  }

  // Iconos por defecto para cada tipo
  const DEFAULT_ICONS = {
    [NOTIFICATION_TYPES.SUCCESS]: 'mdi-check-circle',
    [NOTIFICATION_TYPES.ERROR]: 'mdi-alert-circle',
    [NOTIFICATION_TYPES.INFO]: 'mdi-information',
    [NOTIFICATION_TYPES.WARNING]: 'mdi-alert'
  }

  // Duración por defecto para cada tipo
  const DEFAULT_DURATIONS = {
    [NOTIFICATION_TYPES.SUCCESS]: 8000,
    [NOTIFICATION_TYPES.ERROR]: 10000,
    [NOTIFICATION_TYPES.INFO]: 6000,
    [NOTIFICATION_TYPES.WARNING]: 7000
  }

  /**
   * Mostrar una notificación
   * @param {string} type - Tipo de notificación (success, error, info, warning)
   * @param {string} message - Mensaje principal
   * @param {Object} options - Opciones adicionales
   */
  const showNotification = (type, message, options = {}) => {
    // Prevenir duplicados: verificar si ya existe una notificación similar
    const existingNotification = notifications.value.find(n => 
      n.type === type && 
      n.message === message && 
      n.title === (options.title || null)
    )
    
    if (existingNotification) {
      console.log(`🔄 Notificación duplicada detectada, saltando:`, {
        type,
        message,
        existingId: existingNotification.id
      })
      return existingNotification.id
    }
    
    // Limpiar notificaciones del mismo tipo si hay demasiadas
    const maxNotificationsPerType = 2
    const notificationsOfType = notifications.value.filter(n => n.type === type)
    if (notificationsOfType.length >= maxNotificationsPerType) {
      // Remover la más antigua
      const oldestNotification = notificationsOfType[0]
      removeNotification(oldestNotification.id)
      console.log(`🧹 Notificación antigua removida para evitar spam:`, {
        type,
        id: oldestNotification.id
      })
    }
    
    const id = nextId.value++
    
    const notification = {
      id,
      type,
      message,
      title: options.title || null,
      details: options.details || null,
      icon: options.icon || DEFAULT_ICONS[type],
      loading: options.loading || false,
      closable: options.closable !== false, // Por defecto true
      autoHide: options.autoHide !== false, // Por defecto true
      duration: options.duration || DEFAULT_DURATIONS[type],
      maxWidth: options.maxWidth || 400,
      timestamp: Date.now()
    }

    // Agregar la notificación al array
    notifications.value.push(notification)

    // Auto-ocultar si está habilitado
    if (notification.autoHide) {
      setTimeout(() => {
        removeNotification(id)
      }, notification.duration)
    }

    // Log para debugging
    console.log(`🔔 Notificación mostrada:`, {
      id,
      type,
      message,
      duration: notification.duration,
      totalNotifications: notifications.value.length
    })

    return id
  }

  /**
   * Mostrar notificación de éxito
   */
  const showSuccess = (message, options = {}) => {
    return showNotification(NOTIFICATION_TYPES.SUCCESS, message, options)
  }

  /**
   * Mostrar notificación de error
   */
  const showError = (message, options = {}) => {
    return showNotification(NOTIFICATION_TYPES.ERROR, message, options)
  }

  /**
   * Mostrar notificación de información
   */
  const showInfo = (message, options = {}) => {
    return showNotification(NOTIFICATION_TYPES.INFO, message, options)
  }

  /**
   * Mostrar notificación de advertencia
   */
  const showWarning = (message, options = {}) => {
    return showNotification(NOTIFICATION_TYPES.WARNING, message, options)
  }

  /**
   * Mostrar notificación de carga
   */
  const showLoading = (message, options = {}) => {
    return showNotification(NOTIFICATION_TYPES.INFO, message, {
      ...options,
      loading: true,
      autoHide: false,
      closable: false
    })
  }

  /**
   * Remover una notificación específica
   */
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      const removed = notifications.value.splice(index, 1)[0]
      console.log(`🗑️ Notificación removida:`, {
        id,
        type: removed.type,
        message: removed.message,
        remainingNotifications: notifications.value.length
      })
    } else {
      console.log(`⚠️ Intento de remover notificación inexistente:`, id)
    }
  }

  /**
   * Limpiar todas las notificaciones
   */
  const clearAll = () => {
    const count = notifications.value.length
    notifications.value = []
    console.log(`🧹 ${count} notificaciones removidas`)
  }

  /**
   * Limpiar notificaciones por tipo
   */
  const clearByType = (type) => {
    const initialCount = notifications.value.length
    notifications.value = notifications.value.filter(n => n.type !== type)
    const removedCount = initialCount - notifications.value.length
    console.log(`🧹 ${removedCount} notificaciones de tipo '${type}' removidas`)
  }

  /**
   * Limpiar notificaciones antiguas (más de 30 segundos)
   */
  const clearOldNotifications = () => {
    const now = Date.now()
    const thirtySecondsAgo = now - 30000
    
    const initialCount = notifications.value.length
    notifications.value = notifications.value.filter(n => n.timestamp > thirtySecondsAgo)
    const removedCount = initialCount - notifications.value.length
    
    if (removedCount > 0) {
      console.log(`🧹 ${removedCount} notificaciones antiguas removidas automáticamente`)
    }
  }

  /**
   * Limpiar notificaciones de carga que no se cerraron
   */
  const clearStuckLoadingNotifications = () => {
    const initialCount = notifications.value.length
    notifications.value = notifications.value.filter(n => !(n.loading && n.autoHide === false))
    const removedCount = initialCount - notifications.value.length
    
    if (removedCount > 0) {
      console.log(`🧹 ${removedCount} notificaciones de carga atascadas removidas`)
    }
  }

  /**
   * Obtener notificaciones por tipo
   */
  const getByType = (type) => {
    return notifications.value.filter(n => n.type === type)
  }

  /**
   * Verificar si hay notificaciones activas
   */
  const hasActiveNotifications = () => {
    return notifications.value.length > 0
  }

  /**
   * Obtener estadísticas de notificaciones
   */
  const getStats = () => {
    const stats = {
      total: notifications.value.length,
      byType: {}
    }

    Object.values(NOTIFICATION_TYPES).forEach(type => {
      stats.byType[type] = getByType(type).length
    })

    return stats
  }

  /**
   * Inicializar limpieza automática
   */
  const initAutoCleanup = () => {
    // Limpiar notificaciones antiguas cada 30 segundos
    setInterval(() => {
      clearOldNotifications()
    }, 30000)
    
    // Limpiar notificaciones de carga atascadas cada 10 segundos
    setInterval(() => {
      clearStuckLoadingNotifications()
    }, 10000)
    
    console.log('🧹 Sistema de limpieza automática iniciado')
  }

  // Iniciar limpieza automática
  initAutoCleanup()

  return {
    // Estado
    notifications,
    NOTIFICATION_TYPES,
    
    // Métodos principales
    showNotification,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    showLoading,
    
    // Métodos de gestión
    removeNotification,
    clearAll,
    clearByType,
    clearOldNotifications,
    clearStuckLoadingNotifications,
    getByType,
    hasActiveNotifications,
    getStats
  }
})
