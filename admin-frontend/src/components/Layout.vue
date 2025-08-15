<template>
  <v-app>
    <AppBar 
      :drawer="drawer" 
      @update:drawer="drawer = $event" 
    />
    <SideNav 
      :menu-items="menuItems" 
      :model-value="drawer"
      @update:model-value="drawer = $event"
    />
    <v-main class="bg-dark-background">
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { ref } from 'vue'
import AppBar from './AppBar.vue'
import SideNav from './SideNav.vue'

export default {
  name: 'AppLayout',
  components: {
    AppBar,
    SideNav
  },
  setup() {
    const drawer = ref(true)
    
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