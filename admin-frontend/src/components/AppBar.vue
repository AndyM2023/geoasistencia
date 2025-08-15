<template>
  <v-app-bar
    app
    elevation="0"
    class="bg-dark-surface app-bar-with-border"
    height="70"
  >
    <div class="d-flex align-center">
      <!-- Botón del menú (solo mostrar en rutas /app/*) -->
      <v-btn
        v-if="showMenuButton"
        icon
        @click="toggleDrawer"
        class="mr-4"
        color="blue-400"
      >
        <v-icon>mdi-menu</v-icon>
      </v-btn>
      
      <!-- Logo y título -->
      <div class="d-flex align-center">
        <v-icon
          size="32"
          color="blue-400"
          class="mr-3"
        >
          mdi-fingerprint
        </v-icon>
        <span class="text-h6 font-weight-bold text-white neon-glow">
          GeoAsistencia
        </span>
      </div>
    </div>

    <v-spacer></v-spacer>

    <!-- Acciones de usuario -->
    <div class="d-flex align-center">
      <!-- Botón de notificaciones (solo en rutas /app/*) -->
      <v-btn
        v-if="showMenuButton"
        icon
        color="blue-400"
        class="mr-2"
      >
        <v-icon>mdi-bell</v-icon>
      </v-btn>
      
      <!-- Botón dinámico según la ruta -->
      <template v-if="!showMenuButton">
        <!-- En página de reconocimiento (/): Botón ADMIN -->
        <v-btn
          v-if="isRecognitionPage"
          variant="text"
          class="text-white"
          @click="goToLogin"
        >
          <v-avatar size="32" class="mr-2">
            <v-icon>mdi-account-cog</v-icon>
          </v-avatar>
          ADMIN
          <v-icon right>mdi-arrow-right</v-icon>
        </v-btn>
        
        <!-- En página de login (/login): Botón EMPLOYEE -->
        <v-btn
          v-if="isLoginPage"
          variant="text"
          class="text-white"
          @click="goToRecognition"
        >
          <v-avatar size="32" class="mr-2">
            <v-icon>mdi-account</v-icon>
          </v-avatar>
          EMPLEADO
          <v-icon right>mdi-arrow-left</v-icon>
        </v-btn>
      </template>
      
      <!-- Menú desplegable para rutas autenticadas (/app/*) -->
      <v-menu v-if="showMenuButton" offset-y>
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            variant="text"
            class="text-white"
          >
            <v-avatar size="32" class="mr-2">
              <v-icon>mdi-account</v-icon>
            </v-avatar>
            ADMIN
            <v-icon right>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        
        <v-list class="bg-dark-surface">
          <v-list-item @click="logout">
            <v-list-item-title class="text-white">
              <v-icon left color="red-400">mdi-logout</v-icon>
              Cerrar Sesión
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
  </v-app-bar>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'AppBar',
  props: {
    drawer: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:drawer'],
  setup(props, { emit }) {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()

    // Computed properties para determinar qué mostrar
    const isRecognitionPage = computed(() => route.path === '/')
    const isLoginPage = computed(() => route.path === '/login')
    const isAppRoute = computed(() => route.path.startsWith('/app'))
    
    // Mostrar botón de menú solo en rutas /app/*
    const showMenuButton = computed(() => isAppRoute.value)

    const toggleDrawer = () => {
      console.log('toggleDrawer clicked, current drawer:', props.drawer)
      emit('update:drawer', !props.drawer)
    }

    const logout = () => {
      authStore.logout()
      router.push('/')
    }

    const goToLogin = () => {
      router.push('/login')
    }

    const goToRecognition = () => {
      router.push('/')
    }

    return {
      toggleDrawer,
      logout,
      goToLogin,
      goToRecognition,
      isRecognitionPage,
      isLoginPage,
      showMenuButton
    }
  }
}
</script>