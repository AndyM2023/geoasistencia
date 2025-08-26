<template>
  <!-- Mensaje cuando no hay datos -->
  <v-card v-if="!reportData.length && !loading" class="text-center pa-8">
    <v-icon size="64" color="grey">mdi-chart-line</v-icon>
    <div class="text-h6 mt-4">No hay datos para mostrar</div>
    <div class="text-body-2 text-grey">Selecciona los filtros y genera un reporte</div>
  </v-card>

  <!-- Mensaje cuando no hay resultados de búsqueda -->
  <v-card v-if="reportData.length > 0 && filteredReportData.length === 0 && search.trim()" class="text-center pa-8">
    <v-icon size="64" color="warning">mdi-magnify</v-icon>
    <div class="text-h6 mt-4">No se encontraron resultados</div>
    <div class="text-body-2 text-grey">
      No hay resultados para "{{ search }}". 
      <v-btn 
        text 
        color="primary" 
        @click="$emit('clear-search')"
        class="ml-2"
      >
        Limpiar búsqueda
      </v-btn>
    </div>
  </v-card>
</template>

<script>
export default {
  name: 'ReportMessages',
  props: {
    reportData: {
      type: Array,
      required: true,
      default: () => []
    },
    filteredReportData: {
      type: Array,
      required: true,
      default: () => []
    },
    search: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['clear-search']
}
</script>
