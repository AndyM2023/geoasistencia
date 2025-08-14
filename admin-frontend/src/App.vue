<template>
  <div>
    <!-- Mostrar Layout con menú lateral para rutas autenticadas -->
    <Layout v-if="isAuthenticated && !isLoginRoute" />
    
    <!-- Mostrar solo el contenido para login -->
    <router-view v-else />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import Layout from './components/Layout.vue'

export default {
  name: 'App',
  components: {
    Layout
  },
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()

    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const isLoginRoute = computed(() => route.path === '/login')

    return {
      isAuthenticated,
      isLoginRoute
    }
  }
}
</script>

<style>
/* Estilos globales para modo oscuro */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Roboto', sans-serif;
  background: #0a0a0f;
  color: #ffffff;
}

/* Personalización de scrollbar para modo oscuro */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1a2e;
}

::-webkit-scrollbar-thumb {
  background: #3b82f6;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #00d4ff;
}

/* Efectos de hover mejorados */
.v-btn:hover {
  transform: translateY(-1px);
  transition: transform 0.2s ease;
}

/* Animaciones suaves */
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.15) !important;
}

/* Efectos de focus mejorados */
.v-field--focused {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Gradientes de fondo */
.v-application {
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%) !important;
}

/* Efectos de neón para elementos importantes */
.neon-glow {
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.neon-border {
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}
</style>
