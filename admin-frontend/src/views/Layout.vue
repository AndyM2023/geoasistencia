<template>
  <v-app>
    <div v-if="!isAuthenticated" class="d-flex justify-center align-center" style="height: 100vh;">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>
    <template v-else>
      <AppBar v-model:drawer="drawer" />
      <SideNav v-model="drawer" :menu-items="menuItems" />
      <v-main class="bg-dark-background">
        <v-container fluid class="pa-6">
          <router-view />
        </v-container>
      </v-main>
    </template>
  </v-app>
</template>

<script>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
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
    const drawer = ref(true)
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
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
      isAuthenticated
    }
  }
}
</script>

<style scoped>
.bg-dark-background {
  background-color: #0f172a;
}
</style>
