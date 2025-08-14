<template>
  <v-app>
    <AppBar />
    <SideNav :menu-items="menuItems" />
    <v-main class="bg-dark-background">
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { ref } from 'vue'
import AppBar from '../components/AppBar.vue'
import SideNav from '../components/SideNav.vue'

export default {
  name: 'AppLayout',
  components: {
    AppBar,
    SideNav
  },
  setup() {
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
      menuItems
    }
  }
}
</script>

<style scoped>
.bg-dark-background {
  background-color: #0f172a;
}
</style>
