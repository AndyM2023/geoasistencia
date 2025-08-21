<template>
  <div class="notifications-overlay">
    <!-- Botón de limpieza manual (solo visible si hay notificaciones) -->
    <div v-if="notifications.length > 0" class="clear-all-button">
      <v-btn
        size="x-small"
        color="grey"
        variant="tonal"
        icon="mdi-broom"
        @click="clearAllNotifications"
        title="Limpiar todas las notificaciones"
        class="clear-btn"
      ></v-btn>
    </div>
    
    <transition-group name="slide-down" tag="div">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="['floating-notification', notification.type]"
      >
        <v-alert
          :type="notification.type"
          variant="text"
          :closable="notification.closable"
          @click:close="removeNotification(notification.id)"
          :max-width="notification.maxWidth || 400"
          :style="getNotificationStyle(notification.type)"
        >
          <template v-slot:prepend>
            <v-icon v-if="notification.icon">{{ notification.icon }}</v-icon>
            <v-progress-circular
              v-else-if="notification.loading"
              indeterminate
              size="16"
              color="white"
            ></v-progress-circular>
          </template>
          
          <div class="notification-content">
            <div v-if="notification.title" class="notification-title">
              {{ notification.title }}
            </div>
            <div class="notification-message">
              {{ notification.message }}
            </div>
            <div v-if="notification.details" class="notification-details">
              {{ notification.details }}
            </div>
          </div>
        </v-alert>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useNotificationStore } from '../../stores/notifications'

export default {
  name: 'ToastNotification',
  setup() {
    const notificationStore = useNotificationStore()
    
    const notifications = computed(() => notificationStore.notifications)
    
    const removeNotification = (id) => {
      notificationStore.removeNotification(id)
    }

    const clearAllNotifications = () => {
      notificationStore.clearAll()
    }

    const getNotificationStyle = (type) => {
      const baseStyle = {
        background: 'transparent !important',
        border: 'none !important',
        boxShadow: 'none !important',
        color: 'white !important',
        borderRadius: '12px',
        backdropFilter: 'blur(20px)',
        padding: '16px',
        margin: '0',
        position: 'relative'
      }

      switch (type) {
        case 'error':
          return {
            ...baseStyle,
            backgroundColor: 'rgba(220, 38, 38, 0.2) !important',
            borderColor: 'rgba(185, 28, 28, 0.4) !important',
            boxShadow: '0 8px 32px rgba(220, 38, 38, 0.1) !important'
          }
        case 'success':
          return {
            ...baseStyle,
            backgroundColor: 'rgba(22, 163, 74, 0.2) !important',
            borderColor: 'rgba(21, 128, 61, 0.4) !important',
            boxShadow: '0 8px 32px rgba(22, 163, 74, 0.1) !important'
          }
        case 'info':
          return {
            ...baseStyle,
            backgroundColor: 'rgba(37, 99, 235, 0.2) !important',
            borderColor: 'rgba(29, 78, 216, 0.4) !important',
            boxShadow: '0 8px 32px rgba(37, 99, 235, 0.1) !important'
          }
        case 'warning':
          return {
            ...baseStyle,
            backgroundColor: 'rgba(217, 119, 6, 0.2) !important',
            borderColor: 'rgba(180, 83, 9, 0.4) !important',
            boxShadow: '0 8px 32px rgba(217, 119, 6, 0.1) !important'
          }
        default:
          return baseStyle
      }
    }
    
    return {
      notifications,
      removeNotification,
      clearAllNotifications,
      getNotificationStyle
    }
  }
}
</script>

<style scoped>
/* Sistema de notificaciones flotantes */
.notifications-overlay {
  position: fixed;
  top: 80px; /* Debajo del AppBar */
  left: 50%;
  transform: translateX(-50%);
  z-index: 1001;
  pointer-events: none; /* Permite que los clics pasen a través del overlay */
}

/* Botón de limpieza manual */
.clear-all-button {
  position: absolute;
  top: -40px;
  right: 0;
  pointer-events: auto;
}

.clear-btn {
  background: rgba(0, 0, 0, 0.6) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  backdrop-filter: blur(10px) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

.clear-btn:hover {
  background: rgba(0, 0, 0, 0.8) !important;
  transform: scale(1.1) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
}

.floating-notification {
  pointer-events: auto; /* Restaura los clics en la notificación */
  margin-bottom: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-radius: 12px; /* Bordes más redondeados */
  backdrop-filter: blur(20px) !important; /* Desenfoque general más intenso */
  border: 1px solid rgba(255, 255, 255, 0.15) !important; /* Borde sutil */
  color: white !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; /* Transición suave */
}

.floating-notification:hover {
  transform: translateY(-2px) !important; /* Efecto hover sutil */
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
}

.floating-notification * {
  color: white !important;
}

.floating-notification .v-alert__content,
.floating-notification .v-alert__title,
.floating-notification .v-alert__body {
  color: white !important;
}

.floating-notification .v-icon,
.floating-notification .v-btn__content .v-icon {
  color: white !important;
}

.floating-notification .v-progress-circular {
  color: white !important;
}

/* Asegurar que los botones de cerrar sean visibles */
.floating-notification .v-btn--icon {
  color: white !important;
}

.floating-notification .v-btn--icon:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

/* Estilos específicos para cada tipo de notificación - FORZADOS */
.floating-notification.error-notification {
  background: rgba(220, 38, 38, 0.2) !important; /* Rojo MUY transparente */
  border-color: rgba(185, 28, 28, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(220, 38, 38, 0.1) !important;
}

.floating-notification.success-notification {
  background: rgba(22, 163, 74, 0.2) !important; /* Verde MUY transparente */
  border-color: rgba(21, 128, 61, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(22, 163, 74, 0.1) !important;
}

.floating-notification.info-notification {
  background: rgba(37, 99, 235, 0.2) !important; /* Azul MUY transparente */
  border-color: rgba(29, 78, 216, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(37, 99, 235, 0.1) !important;
}

.floating-notification.warning-notification {
  background: rgba(217, 119, 6, 0.2) !important; /* Naranja MUY transparente */
  border-color: rgba(180, 83, 9, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(217, 119, 6, 0.1) !important;
}

/* Asegurar que los mensajes de error específicos sean visibles */
.error-notification .v-alert__content,
.error-notification .v-alert__body {
  font-weight: 600 !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6) !important; /* Sombra más intensa para errores */
}

/* Mejorar la legibilidad del texto en todas las notificaciones */
.floating-notification .v-alert__content {
  font-weight: 600 !important; /* Texto más grueso */
  line-height: 1.5 !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important; /* Sombra más pronunciada */
  letter-spacing: 0.02em !important; /* Espaciado de letras mejorado */
}

/* Estilos para el contenido de la notificación */
.notification-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notification-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.notification-message {
  font-size: 0.9rem;
}

.notification-details {
  font-size: 0.8rem;
  opacity: 0.9;
  font-style: italic;
}

/* Animaciones de entrada y salida */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* Responsive para notificaciones */
@media (max-width: 600px) {
  .notifications-overlay {
    top: 70px;
    left: 20px;
    right: 20px;
    transform: none;
  }
  
  .floating-notification {
    max-width: none !important;
    width: 100%;
  }
  
  .slide-down-enter-from,
  .slide-down-leave-to {
    transform: translateY(-20px);
  }
  
  .slide-down-enter-to,
  .slide-down-leave-from {
    transform: translateY(0);
  }
}

/* Efectos de brillo sutiles para cada tipo */
.error-notification::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  border-radius: 12px 12px 0 0;
}

.success-notification::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  border-radius: 12px 12px 0 0;
}

.info-notification::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  border-radius: 12px 12px 0 0;
}

.warning-notification::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  border-radius: 12px 12px 0 0;
}

/* SOBRESCRIBIR COMPLETAMENTE VUETIFY - MÁXIMA ESPECIFICIDAD */
:deep(.floating-notification .v-alert) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: white !important;
}

:deep(.floating-notification .v-alert__wrapper) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(.floating-notification .v-alert__content) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(.floating-notification .v-alert__body) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* FORZAR COLORES DE FONDO EN TODOS LOS ELEMENTOS */
:deep(.floating-notification.error-notification .v-alert),
:deep(.floating-notification.error-notification .v-alert__wrapper),
:deep(.floating-notification.error-notification .v-alert__content),
:deep(.floating-notification.error-notification .v-alert__body),
:deep(.floating-notification.error-notification .v-alert *) {
  background: rgba(220, 38, 38, 0.2) !important;
}

:deep(.floating-notification.success-notification .v-alert),
:deep(.floating-notification.success-notification .v-alert__wrapper),
:deep(.floating-notification.success-notification .v-alert__content),
:deep(.floating-notification.success-notification .v-alert__body),
:deep(.floating-notification.success-notification .v-alert *) {
  background: rgba(22, 163, 74, 0.2) !important;
}

:deep(.floating-notification.info-notification .v-alert),
:deep(.floating-notification.info-notification .v-alert__wrapper),
:deep(.floating-notification.info-notification .v-alert__content),
:deep(.floating-notification.info-notification .v-alert__body),
:deep(.floating-notification.info-notification .v-alert *) {
  background: rgba(37, 99, 235, 0.2) !important;
}

:deep(.floating-notification.warning-notification .v-alert),
:deep(.floating-notification.warning-notification .v-alert__wrapper),
:deep(.floating-notification.warning-notification .v-alert__content),
:deep(.floating-notification.warning-notification .v-alert__body),
:deep(.floating-notification.warning-notification .v-alert *) {
  background: rgba(217, 119, 6, 0.2) !important;
}

/* SOBRESCRIBIR VARIABLES CSS DE VUETIFY */
:deep(.floating-notification .v-alert) {
  --v-theme-error: transparent !important;
  --v-theme-success: transparent !important;
  --v-theme-info: transparent !important;
  --v-theme-warning: transparent !important;
}

/* SOBRESCRIBIR ESTILOS DE TIPO DE VUETIFY */
:deep(.floating-notification .v-alert--type-error) {
  background: transparent !important;
  border-color: transparent !important;
  color: white !important;
}

:deep(.floating-notification .v-alert--type-success) {
  background: transparent !important;
  border-color: transparent !important;
  color: white !important;
}

:deep(.floating-notification .v-alert--type-info) {
  background: transparent !important;
  border-color: transparent !important;
  color: white !important;
}

:deep(.floating-notification .v-alert--type-warning) {
  background: transparent !important;
  border-color: transparent !important;
  color: white !important;
}

/* SOBRESCRIBIR VARIANT TEXT DE VUETIFY */
:deep(.floating-notification .v-alert--variant-text) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* FORZAR ESTILOS EN EL ELEMENTO RAÍZ */
.floating-notification.error-notification {
  background: rgba(220, 38, 38, 0.2) !important;
  border-color: rgba(185, 28, 28, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(220, 38, 38, 0.1) !important;
}

.floating-notification.success-notification {
  background: rgba(22, 163, 74, 0.2) !important;
  border-color: rgba(21, 128, 61, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(22, 163, 74, 0.1) !important;
}

.floating-notification.info-notification {
  background: rgba(37, 99, 235, 0.2) !important;
  border-color: rgba(29, 78, 216, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(37, 99, 235, 0.1) !important;
}

.floating-notification.warning-notification {
  background: rgba(217, 119, 6, 0.2) !important;
  border-color: rgba(180, 83, 9, 0.4) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 8px 32px rgba(217, 119, 6, 0.1) !important;
}

/* ESTILOS DE MÁXIMA ESPECIFICIDAD PARA SOBRESCRIBIR VUETIFY */
.floating-notification.error-notification .v-alert,
.floating-notification.error-notification .v-alert * {
  background: rgba(220, 38, 38, 0.2) !important;
}

.floating-notification.success-notification .v-alert,
.floating-notification.success-notification .v-alert * {
  background: rgba(22, 163, 74, 0.2) !important;
}

.floating-notification.info-notification .v-alert,
.floating-notification.info-notification .v-alert * {
  background: rgba(37, 99, 235, 0.2) !important;
}

.floating-notification.warning-notification .v-alert,
.floating-notification.warning-notification .v-alert * {
  background: rgba(217, 119, 6, 0.2) !important;
}

/* SOBRESCRIBIR COMPLETAMENTE CON SELECTORES MÁS ESPECÍFICOS */
div.floating-notification.error-notification div.v-alert,
div.floating-notification.error-notification div.v-alert * {
  background: rgba(220, 38, 38, 0.2) !important;
}

div.floating-notification.success-notification div.v-alert,
div.floating-notification.success-notification div.v-alert * {
  background: rgba(22, 163, 74, 0.2) !important;
}

div.floating-notification.info-notification div.v-alert,
div.floating-notification.info-notification div.v-alert * {
  background: rgba(37, 99, 235, 0.2) !important;
}

div.floating-notification.warning-notification div.v-alert,
div.floating-notification.warning-notification div.v-alert * {
  background: rgba(217, 119, 6, 0.2) !important;
}

/* FORZAR ESTILOS EN TODOS LOS ELEMENTOS POSIBLES */
.floating-notification.error-notification .v-alert__wrapper,
.floating-notification.error-notification .v-alert__content,
.floating-notification.error-notification .v-alert__body,
.floating-notification.error-notification .v-alert__title {
  background: rgba(220, 38, 38, 0.2) !important;
}

.floating-notification.success-notification .v-alert__wrapper,
.floating-notification.success-notification .v-alert__content,
.floating-notification.success-notification .v-alert__body,
.floating-notification.success-notification .v-alert__title {
  background: rgba(22, 163, 74, 0.2) !important;
}

.floating-notification.info-notification .v-alert__wrapper,
.floating-notification.info-notification .v-alert__content,
.floating-notification.info-notification .v-alert__body,
.floating-notification.info-notification .v-alert__title {
  background: rgba(37, 99, 235, 0.2) !important;
}

.floating-notification.warning-notification .v-alert__wrapper,
.floating-notification.warning-notification .v-alert__content,
.floating-notification.warning-notification .v-alert__body,
.floating-notification.warning-notification .v-alert__title {
  background: rgba(217, 119, 6, 0.2) !important;
}
</style>
