<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* CSS global para eliminar espacios no deseados */
* {
  box-sizing: border-box;
}

html, body {
  margin: 0 !important;
  padding: 0 !important;
  overflow-x: hidden;
}

.v-application {
  margin: 0 !important;
  padding: 0 !important;
}

.v-application__wrap {
  min-height: 100vh;
}
</style>
