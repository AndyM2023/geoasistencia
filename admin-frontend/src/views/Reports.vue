<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4 text-white">Reportes de Asistencia</h1>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <ReportFilters
      v-model:filters="filters"
      :employees="employees"
      :areas="areas"
      :generating="generating"
      :has-report-data="reportData.length > 0"
      @generate-report="generateReport"
      @export-report="exportReport"
    />

    <!-- Estadísticas -->
    <ReportStats :stats="stats" />

    <!-- Tabla de Reporte -->
    <ReportTable
      :report-data="reportData"
      :filtered-report-data="filteredReportData"
      :search="search"
      :loading="loading"
      :table-key="tableKey"
        :headers="headers"
    />

    <!-- Gráfico -->
    <ReportChart
      :report-data="reportData"
      :chart-data="chartData"
    />

    <!-- Mensajes de estado -->
    <ReportMessages
      :report-data="reportData"
      :filtered-report-data="filteredReportData"
      :search="search"
      :loading="loading"
      @clear-search="clearSearch"
    />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import ReportFilters from '../components/reports/ReportFilters.vue'
import ReportStats from '../components/reports/ReportStats.vue'
import ReportTable from '../components/reports/ReportTable.vue'
import ReportChart from '../components/reports/ReportChart.vue'
import ReportMessages from '../components/reports/ReportMessages.vue'
import { useReports } from '../composables/useReports'

export default {
  name: 'Reports',
  components: {
    ReportFilters,
    ReportStats,
    ReportTable,
    ReportChart,
    ReportMessages
  },
  setup() {
    // Usar el composable para toda la lógica de negocio
    const {
      // Estado reactivo
      search,
      loading,
      generating,
      tableKey,
      filters,
      employees,
      areas,
      reportData,
      stats,
      headers,
      
      // Computed properties
      filteredReportData,
      chartData,
      
      // Funciones
      generateReport,
      exportReport,
      clearSearch,
      initialize
    } = useReports()
    
    // Inicializar cuando el componente se monta
    onMounted(async () => {
      await initialize()
    })
    
    return {
      // Estado reactivo
      search,
      loading,
      generating,
      tableKey,
      filters,
      employees,
      areas,
      reportData,
      stats,
      headers,
      
      // Computed properties
      filteredReportData,
      chartData,
      
      // Funciones
      generateReport,
      exportReport,
      clearSearch
    }
  }
}
</script>

<style>
@import '../style/reports.css';
</style>
