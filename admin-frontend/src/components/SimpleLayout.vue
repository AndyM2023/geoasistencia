<template>
  <v-app>
    <!-- Barra superior -->
    <AppBar />

    <!-- Contenido principal -->
    <v-main class="bg-dark-background">
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import AppBar from './AppBar.vue'

export default {
  name: 'SimpleLayout',
  components: {
    AppBar
  }
}
</script>
