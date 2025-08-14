<template>
  <div>
    <h1 class="text-h4 mb-6 text-white">Acerca de GeoAsistencia</h1>
    
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white">Información del Sistema</v-card-title>
      <v-card-text class="text-grey-300">
        <p class="mb-4">
          GeoAsistencia es un sistema moderno de control de asistencia basado en geolocalización 
          que permite a las empresas gestionar eficientemente la asistencia de sus empleados.
        </p>
        
        <h3 class="text-h6 text-white mb-3">Características Principales:</h3>
        <ul class="mb-4">
          <li>Control de asistencia por geolocalización</li>
          <li>Gestión de empleados y áreas de trabajo</li>
          <li>Reportes detallados de asistencia</li>
          <li>Interfaz moderna y responsiva</li>
          <li>Sistema de autenticación seguro</li>
        </ul>
        
        <h3 class="text-h6 text-white mb-3">Tecnologías Utilizadas:</h3>
        <ul>
          <li>Frontend: Vue.js 3 + Vuetify 3</li>
          <li>Backend: Django + Django REST Framework</li>
          <li>Base de datos: SQLite (desarrollo)</li>
          <li>Autenticación: JWT</li>
        </ul>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>
