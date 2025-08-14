<template>
  <v-app>
    <!-- Barra superior -->
    <v-app-bar
      app
      elevation="0"
      class="bg-dark-surface border-b border-blue-500/20"
      height="70"
    >
      <div class="d-flex align-center">
        <!-- Botón del menú -->
        <v-btn
          icon
          @click="drawer = !drawer"
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
        <v-btn
          icon
          color="blue-400"
          class="mr-2"
        >
          <v-icon>mdi-bell</v-icon>
        </v-btn>
        
        <v-menu offset-y>
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              variant="text"
              class="text-white"
            >
              <v-avatar size="32" class="mr-2">
                <v-icon>mdi-account</v-icon>
              </v-avatar>
              Admin
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

    <!-- Menú lateral -->
    <v-navigation-drawer
      v-model="drawer"
      app
      class="bg-dark-surface border-r border-blue-500/20"
      width="280"
    >
      <!-- Logo en el drawer -->
      <div class="pa-4 border-b border-blue-500/20">
        <div class="d-flex align-center">
          <v-icon
            size="28"
            color="blue-400"
            class="mr-3"
          >
            mdi-fingerprint
          </v-icon>
          <span class="text-h6 font-weight-bold text-white">
            GeoAsistencia
          </span>
        </div>
      </div>

      <!-- Menú de navegación -->
      <v-list class="pa-2">
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          class="mb-1 rounded-lg"
          :class="{ 'bg-blue-500/20': $route.path === item.to }"
          color="blue-400"
          variant="text"
        >
          <template v-slot:prepend>
            <v-icon
              :color="$route.path === item.to ? 'blue-400' : 'grey-400'"
              size="20"
            >
              {{ item.icon }}
            </v-icon>
          </template>
          
          <v-list-item-title
            :class="$route.path === item.to ? 'text-blue-400 font-weight-medium' : 'text-grey-300'"
          >
            {{ item.title }}
          </v-list-item-title>
        </v-list-item>
      </v-list>

      <!-- Información del sistema -->
      <template v-slot:append>
        <div class="pa-4 border-t border-blue-500/20">
          <div class="text-center">
            <v-chip
              color="green-500"
              size="small"
              variant="tonal"
              class="mb-2"
            >
              <v-icon left size="16">mdi-circle</v-icon>
              Sistema Activo
            </v-chip>
            <p class="text-caption text-grey-400 mb-0">
              v1.0.0
            </p>
          </div>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- Contenido principal -->
    <v-main class="bg-dark-background">
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Layout',
  setup() {
    const drawer = ref(true)
    const router = useRouter()
    const authStore = useAuthStore()

    const menuItems = [
      {
        title: 'Dashboard',
        icon: 'mdi-view-dashboard',
        to: '/'
      },
      {
        title: 'Empleados',
        icon: 'mdi-account-group',
        to: '/employees'
      },
      {
        title: 'Áreas',
        icon: 'mdi-map-marker',
        to: '/areas'
      },
      {
        title: 'Reportes',
        icon: 'mdi-chart-box',
        to: '/reports'
      }
    ]

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      drawer,
      menuItems,
      logout
    }
  }
}
</script>
