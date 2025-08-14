<template>
  <div id="app">
    <!-- Mostrar login si no está autenticado -->
    <router-view v-if="!authStore.isAuthenticated" />
    
    <!-- Mostrar dashboard si está autenticado -->
    <v-app v-else>
      <v-navigation-drawer
        v-model="drawer"
        :rail="rail"
        permanent
        @click="rail = false"
      >
        <!-- Información del Usuario -->
        <v-list-item
          prepend-avatar="https://randomuser.me/api/portraits/men/85.jpg"
          :title="authStore.currentUser?.name || 'Administrador'"
          :subtitle="authStore.currentUser?.email || 'admin@geoasistencia.com'"
        >
          <template v-slot:append>
            <v-btn
              variant="text"
              icon="mdi-chevron-left"
              @click.stop="rail = !rail"
            ></v-btn>
          </template>
        </v-list-item>

        <v-divider></v-divider>

        <!-- Navegación Principal -->
        <v-list density="compact" nav>
          <v-list-item
            prepend-icon="mdi-view-dashboard"
            title="Dashboard"
            value="dashboard"
            to="/"
          ></v-list-item>

          <v-list-item
            prepend-icon="mdi-account-group"
            title="Empleados"
            value="employees"
            to="/employees"
          ></v-list-item>

          <v-list-item
            prepend-icon="mdi-map-marker"
            title="Áreas"
            value="areas"
            to="/areas"
          ></v-list-item>

          <v-list-item
            prepend-icon="mdi-chart-line"
            title="Reportes"
            value="reports"
            to="/reports"
          ></v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-app-bar>
        <v-app-bar-title>GEOASISTENCIA - Admin</v-app-bar-title>
        <v-spacer></v-spacer>
        
        <!-- Botón de logout visible -->
        <v-btn
          color="error"
          variant="outlined"
          prepend-icon="mdi-logout"
          @click="handleLogout"
          class="mr-2"
        >
          Cerrar Sesión
        </v-btn>
        
        <!-- Información del Usuario en la Barra -->
        <v-menu v-model="showUserMenu" :close-on-content-click="false" location="bottom end">
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-account"
              v-bind="props"
              @click="toggleUserMenu"
              color="primary"
              variant="tonal"
            ></v-btn>
          </template>
          
          <v-card min-width="300" class="user-menu-card">
            <v-list>
              <v-list-item>
                <v-list-item-title class="font-weight-bold">
                  {{ authStore.currentUser?.name || 'Administrador' }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ authStore.currentUser?.email || 'admin@geoasistencia.com' }}
                </v-list-item-subtitle>
                <v-list-item-subtitle class="text-caption">
                  Rol: {{ authStore.currentUser?.role || 'Administrador' }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-divider></v-divider>
              <v-list-item 
                @click="handleLogout"
                class="logout-item"
                :ripple="true"
              >
                <template v-slot:prepend>
                  <v-icon color="error" size="small">mdi-logout</v-icon>
                </template>
                <v-list-item-title class="text-error font-weight-medium">
                  Cerrar Sesión
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card>
        </v-menu>
      </v-app-bar>

      <v-main>
        <v-container fluid>
          <router-view />
        </v-container>
      </v-main>
    </v-app>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const drawer = ref(true)
    const rail = ref(false)
    const showUserMenu = ref(false)
    
    const toggleUserMenu = () => {
      showUserMenu.value = !showUserMenu.value
      console.log('User menu toggled:', showUserMenu.value)
    }
    
    const handleLogout = () => {
      console.log('Logout clicked!')
      authStore.logout()
      showUserMenu.value = false
      router.push('/login')
    }
    
    onMounted(() => {
      // Inicializar autenticación al cargar la app
      authStore.initAuth()
      console.log('App mounted, auth state:', authStore.isAuthenticated)
    })
    
    return {
      authStore,
      drawer,
      rail,
      showUserMenu,
      toggleUserMenu,
      handleLogout
    }
  }
}
</script>

<style scoped>
.user-menu-card {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
}

.logout-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-item:hover {
  background-color: #ffebee;
}

.logout-item:active {
  background-color: #ffcdd2;
}
</style>
