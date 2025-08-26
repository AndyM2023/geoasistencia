<template>
  <v-card v-if="reportData.length > 0" class="mt-6">
    <v-card-title>Distribución de Estados de Asistencia</v-card-title>
    <v-card-text>
      <AttendancePieChart :data="chartData" />
    </v-card-text>
  </v-card>
</template>

<script>
import AttendancePieChart from '../charts/AttendancePieChart.vue'

export default {
  name: 'ReportChart',
  components: {
    AttendancePieChart
  },
  props: {
    reportData: {
      type: Array,
      required: true,
      default: () => []
    },
    chartData: {
      type: Array,
      required: true,
      default: () => []
    }
  }
}
</script>
