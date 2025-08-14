<template>
  <div>
    <h1 class="text-h4 mb-6 text-white">Dashboard</h1>
    
    <!-- Tarjetas de Estadísticas -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Total Empleados"
          :value="stats.totalEmployees"
          subtitle="Activos en el sistema"
          icon="mdi-account-group"
          color="primary"
          :change="12"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Asistencias Hoy"
          :value="stats.todayAttendance"
          subtitle="Registradas hoy"
          icon="mdi-calendar-check"
          color="success"
          :change="5"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Áreas Activas"
          :value="stats.activeAreas"
          subtitle="Ubicaciones registradas"
          icon="mdi-map-marker"
          color="info"
          :change="0"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          title="Tasa de Asistencia"
          :value="stats.attendanceRate + '%'"
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
            <AttendanceLineChart :data="weeklyAttendanceData" />
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card class="bg-dark-surface border border-blue-500/20">
          <v-card-title class="text-white">Actividad Reciente</v-card-title>
          <v-card-text>
            <v-list density="compact" class="bg-transparent">
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
    const stats = ref({
      totalEmployees: 25,
      todayAttendance: 18,
      activeAreas: 3,
      attendanceRate: 92
    })
    
    const recentActivities = ref([
      {
        id: 1,
        title: 'Juan Pérez marcó asistencia',
        time: 'Hace 5 minutos',
        icon: 'mdi-account-check',
        status: 'success'
      },
      {
        id: 2,
        title: 'María García llegó tarde',
        time: 'Hace 15 minutos',
        icon: 'mdi-clock-alert',
        status: 'warning'
      },
      {
        id: 3,
        title: 'Nueva área registrada',
        time: 'Hace 1 hora',
        icon: 'mdi-map-marker-plus',
        status: 'success'
      },
      {
        id: 4,
        title: 'Reporte mensual generado',
        time: 'Hace 2 horas',
        icon: 'mdi-file-chart',
        status: 'success'
      }
    ])
    
    const weeklyAttendanceData = ref([
      { date: 'Lun', count: 22 },
      { date: 'Mar', count: 24 },
      { date: 'Mié', count: 23 },
      { date: 'Jue', count: 25 },
      { date: 'Vie', count: 20 },
      { date: 'Sáb', count: 8 },
      { date: 'Dom', count: 0 }
    ])
    
    const loadDashboardData = async () => {
      try {
        // CARGAR DESDE API REAL
        const statsData = await dashboardService.getStats()
        stats.value = statsData
        
        const weeklyAttendance = await dashboardService.getWeeklyAttendance()
        weeklyAttendanceData.value = weeklyAttendance
        
        const activity = await dashboardService.getRecentActivity()
        recentActivities.value = activity
        
      } catch (error) {
        console.error('Error cargando datos del dashboard:', error)
      }
    }
    
    onMounted(() => {
      loadDashboardData()
    })
    
    return {
      stats,
      recentActivities,
      weeklyAttendanceData,
      loadDashboardData
    }
  }
}
</script>
