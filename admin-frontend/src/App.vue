<template>
  <v-app>
    <!-- 🔐 INICIALIZADOR DE AUTENTICACIÓN GLOBAL -->
    <AuthInitializer />
    
    <!-- 🔔 SISTEMA DE NOTIFICACIONES GLOBAL -->
    <ToastNotification />
    
    <!-- 🚀 CONTENIDO PRINCIPAL -->
    <router-view />
  </v-app>
</template>

<script>
import AuthInitializer from './components/AuthInitializer.vue'
import ToastNotification from './components/notifications/ToastNotification.vue'

export default {
  name: 'App',
  components: {
    AuthInitializer,
    ToastNotification
  }
}
</script>

<style>
/* CSS global para eliminar espacios no deseados */
* {
  box-sizing: border-box;
}

html, body {
  margin: 0 !important;
  padding: 0 !important;
  overflow-x: hidden;
}

.v-application {
  margin: 0 !important;
  padding: 0 !important;
}

.v-application__wrap {
  min-height: 100vh;
}
</style>
