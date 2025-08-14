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
