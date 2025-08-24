<template>
  <v-app>
    <!-- ❌ NO AUTENTICADO (solo si ya se inicializó pero no hay usuario) -->
    <div v-if="authStore.isInitialized && !isAuthenticated" class="d-flex flex-column justify-center align-center" style="height: 100vh;">
      <v-icon color="red-400" size="64" class="mb-4">mdi-lock-alert</v-icon>
      <h3 class="text-white mb-2">Acceso denegado</h3>
      <p class="text-grey-300 text-center">Redirigiendo al login...</p>
      <v-progress-circular indeterminate color="red-400" size="32" class="mt-4"></v-progress-circular>
    </div>
    
    <!-- ✅ AUTENTICADO Y LISTO -->
    <template v-else>
      <AppBar 
        :drawer="drawer" 
        @update:drawer="handleDrawerUpdate" 
      />
      <SideNav 
        :model-value="drawer"
        :menu-items="menuItems"
        @update:model-value="handleDrawerUpdate"
      />
      <v-main class="bg-dark-background" :class="{ 'dashboard-main': $route.name === 'Dashboard' }">
        <v-container fluid :class="{ 'pa-6': !['Dashboard', 'Employees', 'Areas'].includes($route.name), 'dashboard-container': $route.name === 'Dashboard', 'no-top-padding': ['Employees', 'Areas'].includes($route.name) }">
          <router-view />
        </v-container>
      </v-main>
    </template>
  </v-app>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useDisplay } from 'vuetify'
import AppBar from '../components/AppBar.vue'
import SideNav from '../components/SideNav.vue'

export default {
  name: 'AppLayout',
  components: {
    AppBar,
    SideNav
  },
  setup() {
    const authStore = useAuthStore()
    const { lgAndUp, mdAndDown } = useDisplay()
    
    // Configurar el drawer basado en el tamaño de pantalla
    // En móviles/tablets inicia cerrado, en desktop abierto
    const drawer = ref(lgAndUp.value)
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    // Configurar drawer al montar el componente
    onMounted(() => {
      console.log('🚀 Layout - Componente montado')
      console.log(`   - Estado de autenticación: isInitialized=${authStore.isInitialized}, isAuthenticated=${authStore.isAuthenticated}`)
      
      // Configurar drawer
      drawer.value = lgAndUp.value
    })
    
    // Cerrar drawer automáticamente cuando se cambia a móvil
    watch(mdAndDown, (isMobile) => {
      if (isMobile) {
        drawer.value = false
      }
    })
    
    // Función para manejar actualizaciones del drawer
    const handleDrawerUpdate = (newValue) => {
      console.log('Layout (views): handleDrawerUpdate called with:', newValue)
      drawer.value = newValue
    }
    
    // 🔍 WATCHER PARA DEBUGGING
    watch(() => authStore.isInitialized, (newVal) => {
      console.log(`🔄 Layout - isInitialized cambió a: ${newVal}`)
    })
    
    watch(() => authStore.isAuthenticated, (newVal) => {
      console.log(`🔄 Layout - isAuthenticated cambió a: ${newVal}`)
      if (newVal && authStore.user) {
        console.log(`👤 Layout - Usuario autenticado: ${authStore.user.username}`)
      }
    })
    
    const menuItems = ref([
      {
        title: 'Dashboard',
        icon: 'mdi-view-dashboard',
        to: '/app/dashboard'
      },
      {
        title: 'Empleados',
        icon: 'mdi-account-group',
        to: '/app/employees'
      },
      {
        title: 'Áreas',
        icon: 'mdi-map-marker',
        to: '/app/areas'
      },
      {
        title: 'Reportes',
        icon: 'mdi-chart-bar',
        to: '/app/reports'
      }
    ])

    return {
      drawer,
      menuItems,
      isAuthenticated,
      authStore,
      handleDrawerUpdate
    }
  }
}
</script>

<style scoped>
.bg-dark-background {
  background-color: #0f172a;
}

/* Estilos específicos para el dashboard */
.dashboard-main {
  overflow: hidden !important;
  height: 100vh !important;
  max-height: 100vh !important;
  transition: all 0.2s ease !important;
}

.dashboard-container {
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
  height: 100vh !important;
  max-height: 100vh !important;
  transition: all 0.2s ease !important;
}

/* Permitir scroll en responsive para el dashboard */
@media (max-width: 960px) {
  .dashboard-main {
    overflow-y: auto !important;
    height: auto !important;
    max-height: none !important;
    transition: all 0.2s ease !important;
  }
  
  .dashboard-container {
    overflow-y: auto !important;
    height: auto !important;
    max-height: none !important;
    transition: all 0.2s ease !important;
  }
}

.no-top-padding {
  padding-top: 0 !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  padding-bottom: 1.5rem !important;
}
</style>
