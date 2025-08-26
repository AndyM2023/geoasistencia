<template>
  <v-row class="mb-4 dashboard-stats-row">
    <v-col cols="12" sm="6" md="3">
      <v-card class="stats-card h-100" color="primary" variant="tonal">
        <v-card-text class="pa-1">
          <div class="d-flex align-center mb-1">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold mb-1 text-primary">Total de Días</div>
              <div class="text-h4 font-weight-bold text-primary">{{ stats.totalDays }}</div>
            </div>
            <div class="ml-1">
              <v-icon size="28" color="primary">mdi-calendar</v-icon>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
    
    <v-col cols="12" sm="6" md="3">
      <v-card class="stats-card h-100" color="success" variant="tonal">
        <v-card-text class="pa-1">
          <div class="d-flex align-center mb-1">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold mb-1 text-success">Tasa de Asistencia</div>
              <div class="text-h4 font-weight-bold text-success">{{ stats.attendanceRate }}%</div>
            </div>
            <div class="ml-1">
              <v-icon size="28" color="success">mdi-chart-line</v-icon>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
    
    <v-col cols="12" sm="6" md="3">
      <v-card class="stats-card h-100" color="warning" variant="tonal">
        <v-card-text class="pa-1">
          <div class="d-flex align-center mb-1">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold mb-1 text-warning">Atrasos</div>
              <div class="text-h4 font-weight-bold text-warning">{{ stats.lateCount }}</div>
            </div>
            <div class="ml-1">
              <v-icon size="28" color="warning">mdi-clock-alert</v-icon>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
    
    <v-col cols="12" sm="6" md="3">
      <v-card class="stats-card h-100" color="error" variant="tonal">
        <v-card-text class="pa-1">
          <div class="d-flex align-center mb-1">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold mb-1 text-error">Ausencias</div>
              <div class="text-h4 font-weight-bold text-error">{{ stats.absentCount }}</div>
            </div>
            <div class="ml-1">
              <v-icon size="28" color="warning">mdi-close-circle</v-icon>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'ReportStats',
  props: {
    stats: {
      type: Object,
      required: true,
      default: () => ({
        totalDays: 0,
        attendanceRate: 0,
        lateCount: 0,
        absentCount: 0
      })
    }
  }
}
</script>

<style>
@import '../../styles/reports.css';
</style>
