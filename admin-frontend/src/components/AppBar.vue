<template>
  <v-app-bar
    app
    elevation="0"
    class="bg-dark-surface app-bar-with-border"
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
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'AppBar',
  setup() {
    const drawer = ref(true)
    const router = useRouter()
    const authStore = useAuthStore()

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      drawer,
      logout
    }
  }
}
</script>
