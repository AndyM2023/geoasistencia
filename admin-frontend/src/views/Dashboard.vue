<template>
  <v-container fluid class="dashboard-container pa-2">
    <v-row class="page-header dashboard-header">
      <v-col>
        <h1 class="dashboard-title">Dashboard</h1>
      </v-col>
    </v-row>
    
    <div v-if="loading && !isAuthenticated" class="text-center pa-8">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <div class="mt-4 text-grey-400">Cargando dashboard...</div>
    </div>
    
    <div v-else>
    <!-- Tarjetas de Estadísticas -->
    <v-row class="g-0 dashboard-stats-row">
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
    <v-row class="g-0 dashboard-charts-row">
      <v-col cols="12" md="8" class="pr-md-2">
        <v-card class="bg-dark-surface border border-blue-500/20 h-100">
          <v-card-title class="text-white pb-2">Asistencias por Semana</v-card-title>
          <v-card-text class="pt-0">
            <div v-if="loading" class="text-center pa-6">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <div class="mt-3 text-grey-400">Cargando datos...</div>
            </div>
            <div v-else-if="!weeklyAttendanceData || weeklyAttendanceData.length === 0" class="text-center pa-6 text-grey-400">
              <v-icon size="48" color="grey">mdi-chart-line</v-icon>
              <div class="mt-3">No hay datos de asistencia semanal</div>
            </div>
            <AttendanceLineChart v-else :data="weeklyAttendanceData" />
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4" class="pl-md-2">
        <v-card class="bg-dark-surface border border-blue-500/20 h-100">
          <v-card-title class="text-white pb-2">Actividad Reciente</v-card-title>
          <v-card-text class="pt-0">
            <div v-if="loading" class="text-center pa-6">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <div class="mt-3 text-grey-400">Cargando actividad...</div>
            </div>
            <v-list v-else density="compact" class="bg-transparent pa-0">
              <!-- Debug: Mostrar cantidad de actividades -->
              <div class="text-grey-400 text-caption pa-2 text-center">
                {{ recentActivities.length }} actividades recientes
              </div>
              <v-list-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :prepend-icon="activity.icon"
                :title="activity.title"
                :subtitle="activity.time"
                class="text-white py-2"
              >
                <template v-slot:append>
                  <v-chip
                    :color="getStatusColor(activity.status)"
                    size="small"
                    variant="tonal"
                  >
                    {{ activity.status }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    </div>
  </v-container>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
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
    // Agregar clase al body para estilos específicos
    onMounted(() => {
      document.body.classList.add('dashboard-page')
      document.documentElement.classList.add('dashboard-page')
    })
    
    onUnmounted(() => {
      document.body.classList.remove('dashboard-page')
      document.documentElement.classList.remove('dashboard-page')
    })
    const router = useRouter()
    const authStore = useAuthStore()
    const loading = ref(true)
    const stats = ref({
      totalEmployees: 0,
      todayAttendance: 0,
      activeAreas: 0,
      attendanceRate: 0
    })
    
    const recentActivities = ref([])
    const weeklyAttendanceData = ref([])
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    const loadDashboardData = async () => {
      try {
        loading.value = true
        
        // Cargar datos reales desde la API
        const statsData = await dashboardService.getStats()
        stats.value = statsData
        
        const weeklyAttendance = await dashboardService.getWeeklyAttendance()
        weeklyAttendanceData.value = weeklyAttendance.weeklyData || []
        
        const activity = await dashboardService.getRecentActivity()
        console.log('📊 Actividades recibidas del backend:', activity.activities?.length || 0, 'actividades')
        console.log('📋 Detalle de actividades:', activity.activities)
        recentActivities.value = activity.activities || []
        console.log('✅ Actividades actualizadas en el frontend:', recentActivities.value.length, 'actividades')
        
      } catch (error) {
        console.error('Error cargando datos del dashboard:', error)
        // El interceptor de Axios ya maneja los errores 401
      } finally {
        loading.value = false
      }
    }
    
    const getStatusColor = (status) => {
      switch (status) {
        case 'Entrada': return 'success'
        case 'Salida': return 'info'
        case 'Registrado': return 'warning'
        default: return 'primary'
      }
    }
    
    // Polling interno para mantener datos actualizados
    const pollingInterval = ref(null)
    const POLLING_INTERVAL_MS = 10000 // 10 segundos
    
    const startPolling = () => {
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
      }
      
      pollingInterval.value = setInterval(async () => {
        console.log('🔄 Polling automático: Actualizando datos del dashboard...')
        try {
          // Solo actualizar si no está cargando
          if (!loading.value) {
            await loadDashboardData()
          }
        } catch (error) {
          console.error('❌ Error en polling automático:', error)
        }
      }, POLLING_INTERVAL_MS)
      
      console.log('✅ Polling automático iniciado cada', POLLING_INTERVAL_MS / 1000, 'segundos')
    }
    
    const stopPolling = () => {
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
        pollingInterval.value = null
        console.log('⏹️ Polling automático detenido')
      }
    }
    
    onMounted(async () => {
      // El router guard ya maneja la autenticación
      // Solo cargar datos si llegamos aquí
      loadDashboardData()
      
      // Iniciar polling automático
      startPolling()
    })
    
    // Limpiar polling al desmontar el componente
    onUnmounted(() => {
      stopPolling()
    })
    
    return {
      loading,
      stats,
      recentActivities,
      weeklyAttendanceData,
      isAuthenticated,
      loadDashboardData,
      getStatusColor,
      // Funciones de polling
      startPolling,
      stopPolling
    }
  }
}
</script>

<style scoped>
.dashboard-stats-row {
  margin-bottom: 0 !important;
}

.dashboard-stats-row .v-col {
  padding: 0;
  margin: 0;
}

/* Eliminar espacios entre tarjetas KPI */
.dashboard-stats-row .v-col > * {
  margin: 0 !important;
  border-radius: 0 !important;
}

/* Primera tarjeta - solo bordes redondeados en esquinas superiores */
.dashboard-stats-row .v-col:first-child > * {
  border-top-left-radius: 12px !important;
  border-top-right-radius: 12px !important;
}

/* Última tarjeta - solo bordes redondeados en esquinas inferiores */
.dashboard-stats-row .v-col:last-child > * {
  border-bottom-left-radius: 12px !important;
  border-bottom-right-radius: 12px !important;
}

/* Eliminar espacios entre filas del dashboard */
.v-row.g-0 {
  margin: 0 !important;
}

.v-row.g-0 .v-col {
  padding: 0;
}

/* Eliminar espacios entre tarjetas KPI y secciones del gráfico */
.dashboard-stats-row + .v-row {
  margin-top: 0 !important;
}

/* Asegurar que las tarjetas KPI estén pegadas entre sí */
.dashboard-stats-row .v-col:not(:last-child) > * {
  border-right: none !important;
}

.dashboard-stats-row .v-col:not(:first-child) > * {
  border-left: none !important;
}

.v-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.v-card-title {
  font-size: 1.1rem;
  font-weight: 600;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.v-card-text {
  padding: 1rem;
}

.v-list-item {
  border-radius: 8px;
  margin-bottom: 0.25rem;
  transition: background-color 0.2s ease;
}

.v-list-item:hover {
  background-color: rgba(59, 130, 246, 0.1);
}

.v-chip {
  font-size: 0.75rem;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .dashboard-stats-row .v-col {
    padding: 0.25rem;
  }
  
  .v-row.g-0 .v-col {
    padding: 0;
  }
  
  .v-card-text {
    padding: 0.75rem;
  }
}

/* ===== ESTILOS ESPECÍFICOS DEL DASHBOARD ===== */
/* Los estilos de scroll están en dashboard-specific.css */
</style>
