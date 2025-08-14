<template>
  <div>
    <h1 class="text-h4 mb-6">Dashboard</h1>
    
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
        <v-card>
          <v-card-title>Asistencias por Semana</v-card-title>
          <v-card-text>
            <div class="text-center pa-8">
              <v-icon size="64" color="grey-lighten-1">mdi-chart-line</v-icon>
              <p class="text-grey-lighten-1 mt-2">Gráfico de asistencias</p>
              <small class="text-grey-lighten-1">Chart.js se implementará aquí</small>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Actividad Reciente</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :prepend-icon="activity.icon"
                :title="activity.title"
                :subtitle="activity.time"
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

export default {
  name: 'Dashboard',
  components: {
    StatsCard
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
    
    const loadStats = async () => {
      // TODO: Cargar estadísticas desde la API
      console.log('Cargando estadísticas...')
    }
    
    onMounted(() => {
      loadStats()
    })
    
    return {
      stats,
      recentActivities,
      loadStats
    }
  }
}
</script>
