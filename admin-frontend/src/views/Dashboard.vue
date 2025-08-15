<template>
  <div>
    <h1 class="text-h4 mb-6 text-white">Dashboard</h1>
    
    <!-- Tarjetas de Estadísticas -->
    <v-row class="mb-6 dashboard-stats-row">
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Total Empleados"
          :value="loading ? '...' : stats.totalEmployees"
          subtitle="Activos en el sistema"
          icon="mdi-account-group"
          color="primary"
          :change="12"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Asistencias Hoy"
          :value="loading ? '...' : stats.todayAttendance"
          subtitle="Registradas hoy"
          icon="mdi-calendar-check"
          color="success"
          :change="5"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Áreas Activas"
          :value="loading ? '...' : stats.activeAreas"
          subtitle="Ubicaciones registradas"
          icon="mdi-map-marker"
          color="info"
          :change="0"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Tasa de Asistencia"
          :value="loading ? '...' : (stats.attendanceRate ? stats.attendanceRate + '%' : '0%')"
          subtitle="Promedio mensual"
          icon="mdi-chart-line"
          color="warning"
          :change="-2"
        />
      </v-col>
    </v-row>

    <!-- Gráficos y Actividad Reciente -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card class="bg-dark-surface border border-blue-500/20">
          <v-card-title class="text-white">Asistencias por Semana</v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center pa-8">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <div class="mt-4 text-grey-400">Cargando datos...</div>
            </div>
            <AttendanceLineChart v-else :data="weeklyAttendanceData" />
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card class="bg-dark-surface border border-blue-500/20">
          <v-card-title class="text-white">Actividad Reciente</v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center pa-8">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <div class="mt-4 text-grey-400">Cargando actividad...</div>
            </div>
            <v-list v-else density="compact" class="bg-transparent">
              <v-list-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :prepend-icon="activity.icon"
                :title="activity.title"
                :subtitle="activity.time"
                class="text-white"
              >
                <template v-slot:append>
                  <v-chip
                    :color="activity.status === 'success' ? 'success' : 'warning'"
                    size="small"
                    variant="tonal"
                  >
                    {{ activity.status === 'success' ? 'Completado' : 'Pendiente' }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import StatsCard from '../components/StatsCard.vue'
import AttendanceLineChart from '../components/charts/AttendanceLineChart.vue'
import { dashboardService } from '../services/dashboardService'

export default {
  name: 'Dashboard',
  components: {
    StatsCard,
    AttendanceLineChart
  },
  setup() {
    const loading = ref(true)
    const stats = ref({
      totalEmployees: 0,
      todayAttendance: 0,
      activeAreas: 0,
      attendanceRate: 0
    })
    
    const recentActivities = ref([])
    const weeklyAttendanceData = ref([])
    
    const loadDashboardData = async () => {
      try {
        loading.value = true
        
        // Cargar datos reales desde la API
        const statsData = await dashboardService.getStats()
        stats.value = statsData
        
        const weeklyAttendance = await dashboardService.getWeeklyAttendance()
        weeklyAttendanceData.value = weeklyAttendance
        
        const activity = await dashboardService.getRecentActivity()
        recentActivities.value = activity
        
      } catch (error) {
        console.error('Error cargando datos del dashboard:', error)
        // En caso de error, mantener valores en 0
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadDashboardData()
    })
    
    return {
      loading,
      stats,
      recentActivities,
      weeklyAttendanceData,
      loadDashboardData
    }
  }
}
</script>
