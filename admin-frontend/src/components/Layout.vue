<template>
  <v-app>
    <!-- Barra superior -->
    <AppBar />

    <!-- Menú lateral -->
  

    <!-- Contenido principal -->
    <v-main :class="$route.path === '/login' ? 'login-main' : 'bg-dark-background'">
      <v-container fluid :class="$route.path === '/login' ? 'pa-0' : 'pa-6'">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppBar from './AppBar.vue'
import SideNav from './SideNav.vue'

export default {
  name: 'Layout',
  components: {
    AppBar,
    SideNav
  },
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
      },
      {
        title: 'Acerca de',
        icon: 'mdi-information',
        to: '/about'
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
