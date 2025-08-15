<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4 text-white">Reportes de Asistencia</h1>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-card class="mb-6">
      <v-card-title>Filtros</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.employee"
              label="Empleado"
              :items="employees"
              item-title="name"
              item-value="id"
              clearable
              variant="outlined"
              density="compact"
            ></v-select>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.area"
              label="Área"
              :items="areas"
              item-title="name"
              item-value="id"
              clearable
              variant="outlined"
              density="compact"
            ></v-select>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-menu v-model="showDatePicker" :close-on-content-click="false">
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="filters.dateRange"
                  label="Rango de Fechas"
                  readonly
                  v-bind="props"
                  variant="outlined"
                  density="compact"
                  prepend-icon="mdi-calendar"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="filters.dateRange"
                range
                @update:model-value="showDatePicker = false"
              ></v-date-picker>
            </v-menu>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.status"
              label="Estado"
              :items="['all', 'present', 'absent', 'late']"
              item-title="name"
              item-value="value"
              variant="outlined"
              density="compact"
            ></v-select>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12" class="text-center">
            <v-btn color="primary" @click="generateReport" :loading="generating">
              Generar Reporte
            </v-btn>
            <v-btn color="secondary" @click="exportReport" :disabled="!reportData.length" class="ml-2">
              Exportar Excel
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Estadísticas -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="text-h6 text-primary">{{ stats.totalDays }}</div>
            <div class="text-subtitle-2">Total de Días</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="text-h6 text-success">{{ stats.attendanceRate }}%</div>
            <div class="text-subtitle-2">Tasa de Asistencia</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="text-h6 text-warning">{{ stats.lateCount }}</div>
            <div class="text-subtitle-2">Llegadas Tardes</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="text-h6 text-error">{{ stats.absentCount }}</div>
            <div class="text-subtitle-2">Ausencias</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabla de Reporte -->
    <v-card v-if="reportData.length > 0">
      <v-card-title>
        <span>Reporte de Asistencia</span>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar"
          single-line
          hide-details
          variant="outlined"
          density="compact"
          style="max-width: 300px"
        ></v-text-field>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="reportData"
        :search="search"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:item.date="{ item }">
          {{ formatDate(item.date) }}
        </template>
        
        <template v-slot:item.check_in="{ item }">
          <span v-if="item.check_in">{{ formatTime(item.check_in) }}</span>
          <span v-else class="text-grey">--</span>
        </template>
        
        <template v-slot:item.check_out="{ item }">
          <span v-if="item.check_out">{{ formatTime(item.check_out) }}</span>
          <span v-else class="text-grey">--</span>
        </template>
        
        <template v-slot:item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small">
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>
        
        <template v-slot:item.hours_worked="{ item }">
          {{ item.hours_worked || '--' }}
        </template>
      </v-data-table>
    </v-card>

    <!-- Gráfico -->
    <v-card v-if="reportData.length > 0" class="mt-6">
      <v-card-title>Distribución de Estados de Asistencia</v-card-title>
      <v-card-text>
        <AttendancePieChart :data="chartData" />
      </v-card-text>
    </v-card>

    <!-- Mensaje cuando no hay datos -->
    <v-card v-if="!reportData.length && !loading" class="text-center pa-8">
      <v-icon size="64" color="grey">mdi-chart-line</v-icon>
      <div class="text-h6 mt-4">No hay datos para mostrar</div>
      <div class="text-body-2 text-grey">Selecciona los filtros y genera un reporte</div>
    </v-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import AttendancePieChart from '../components/charts/AttendancePieChart.vue'
import { attendanceService } from '../services/attendanceService'
import { employeeService } from '../services/employeeService'
import areaService from '../services/areaService'

export default {
  name: 'Reports',
  components: {
    AttendancePieChart
  },
  setup() {
    const search = ref('')
    const loading = ref(false)
    const generating = ref(false)
    const showDatePicker = ref(false)
    
    const filters = ref({
      employee: null,
      area: null,
      dateRange: [],
      status: 'all'
    })
    
    const employees = ref([])
    const areas = ref([])
    const reportData = ref([])
    
    const stats = ref({
      totalDays: 0,
      attendanceRate: 0,
      lateCount: 0,
      absentCount: 0
    })
    
    const headers = [
      { title: 'Fecha', key: 'date', sortable: true },
      { title: 'Empleado', key: 'employee_name', sortable: true },
      { title: 'Área', key: 'area_name', sortable: true },
      { title: 'Entrada', key: 'check_in', sortable: true },
      { title: 'Salida', key: 'check_out', sortable: true },
      { title: 'Estado', key: 'status', sortable: true },
      { title: 'Horas Trabajadas', key: 'hours_worked', sortable: true },
      { title: 'Notas', key: 'notes', sortable: false }
    ]
    
    const chartData = computed(() => {
      if (!reportData.value.length) return []
      
      // Agrupar datos por fecha
      const groupedData = {}
      reportData.value.forEach(item => {
        const date = item.date
        if (!groupedData[date]) {
          groupedData[date] = { date: formatDate(date), present: 0, late: 0, absent: 0 }
        }
        
        if (item.status === 'present') {
          groupedData[date].present++
        } else if (item.status === 'late') {
          groupedData[date].late++
        } else if (item.status === 'absent') {
          groupedData[date].absent++
        }
      })
      
      return Object.values(groupedData)
    })
    
    const loadEmployees = async () => {
      try {
        // CARGAR DESDE API REAL
        const employeesData = await employeeService.getAll()
        // El backend devuelve {count, next, previous, results}
        // Necesitamos acceder a results que es el array de empleados
        employees.value = employeesData.results || employeesData
      } catch (error) {
        console.error('Error cargando empleados:', error)
      }
    }
    
    const loadAreas = async () => {
      try {
        // CARGAR DESDE API REAL
        const areasData = await areaService.getAll()
        // El backend devuelve results que es el array de áreas
        areas.value = areasData.results || areasData
      } catch (error) {
        console.error('Error cargando áreas:', error)
      }
    }
    
    const generateReport = async () => {
      generating.value = true
      loading.value = true
      
      try {
        // GENERAR REPORTE DESDE API REAL
        if (filters.value.dateRange.length === 2) {
          const [startDate, endDate] = filters.value.dateRange
          reportData.value = await attendanceService.getByDateRange(startDate, endDate)
        } else {
          const attendanceData = await attendanceService.getAll()
          // El backend devuelve {count, next, previous, results}
          // Necesitamos acceder a results que es el array de asistencias
          reportData.value = attendanceData.results || attendanceData
        }
        
        calculateStats()
      } catch (error) {
        console.error('Error generando reporte:', error)
      } finally {
        generating.value = false
        loading.value = false
      }
    }
    
    const calculateStats = () => {
      if (reportData.value.length === 0) return
      
      const totalDays = reportData.value.length
      const presentCount = reportData.value.filter(item => item.status === 'present').length
      const lateCount = reportData.value.filter(item => item.status === 'late').length
      const absentCount = reportData.value.filter(item => item.status === 'absent').length
      
      stats.value = {
        totalDays,
        attendanceRate: Math.round((presentCount / totalDays) * 100),
        lateCount,
        absentCount
      }
    }
    
    const exportReport = () => {
      // TODO: Implementar exportación a Excel
      console.log('Exportando reporte...')
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('es-ES')
    }
    
    const formatTime = (timeString) => {
      return timeString.substring(0, 5)
    }
    
    const getStatusColor = (status) => {
      const colors = {
        present: 'success',
        late: 'warning',
        absent: 'error'
      }
      return colors[status] || 'grey'
    }
    
    const getStatusText = (status) => {
      const texts = {
        present: 'Presente',
        late: 'Tarde',
        absent: 'Ausente'
      }
      return texts[status] || status
    }
    
    onMounted(() => {
      loadEmployees()
      loadAreas()
    })
    
    return {
      search,
      loading,
      generating,
      showDatePicker,
      filters,
      employees,
      areas,
      reportData,
      stats,
      headers,
      chartData,
      generateReport,
      exportReport,
      formatDate,
      formatTime,
      getStatusColor,
      getStatusText
    }
  }
}
</script>
