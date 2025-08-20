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
          variant="tonal"
          :closable="notification.closable"
          @click:close="removeNotification(notification.id)"
          :max-width="notification.maxWidth || 400"
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
    
    return {
      notifications,
      removeNotification,
      clearAllNotifications
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
  background: rgba(0, 0, 0, 0.7) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  transition: all 0.3s ease !important;
}

.clear-btn:hover {
  background: rgba(0, 0, 0, 0.9) !important;
  transform: scale(1.1) !important;
}

.floating-notification {
  pointer-events: auto; /* Restaura los clics en la notificación */
  margin-bottom: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white !important;
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

/* Estilos específicos para cada tipo de notificación */
.error-notification {
  background: #dc2626 !important; /* Rojo sólido más visible */
  border-color: #b91c1c !important;
}

.success-notification {
  background: #16a34a !important; /* Verde sólido más visible */
  border-color: #15803d !important;
}

.info-notification {
  background: #2563eb !important; /* Azul sólido más visible */
  border-color: #1d4ed8 !important;
}

.warning-notification {
  background: #d97706 !important; /* Naranja sólido más visible */
  border-color: #b45309 !important;
}

/* Asegurar que los mensajes de error específicos sean visibles */
.error-notification .v-alert__content,
.error-notification .v-alert__body {
  font-weight: 500 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
}

/* Mejorar la legibilidad del texto en todas las notificaciones */
.floating-notification .v-alert__content {
  font-weight: 500 !important;
  line-height: 1.4 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
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
</style>
