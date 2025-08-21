<template>
  <div>
    <!-- AppBar sin sidebar -->
    <AppBar />
    
    <!-- Contenido principal -->
    <div class="pa-6">
      <!-- Header con título -->
      <div class="d-flex justify-space-between align-center mb-6">
        <h1 class="text-h4 text-white">Mis Reportes de Asistencia</h1>
      </div>
    
    <div v-if="loading" class="text-center pa-8">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <div class="mt-4 text-grey-400">Cargando reportes...</div>
    </div>
    
    <div v-else>
      <!-- Información del Empleado -->
      <v-card class="bg-dark-surface border border-blue-500/20 mb-6">
        <v-card-title class="text-white pb-2">Información Personal</v-card-title>
        <v-card-text class="pt-0">
          <v-row>
            <v-col cols="12" md="6">
              <div class="text-grey-300 mb-2">
                <strong>Nombre:</strong> {{ employeeInfo.fullName }}
              </div>

              <div class="text-grey-300 mb-2">
                <strong>Cargo:</strong> {{ employeeInfo.position }}
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-grey-300 mb-2">
                <strong>Área:</strong> {{ employeeInfo.area || 'Sin área asignada' }}
              </div>
              <div class="text-grey-300 mb-2">
                <strong>Fecha de Contratación:</strong> {{ employeeInfo.hireDate }}
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Estadísticas Personales -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <v-card class="bg-dark-surface border border-blue-500/20 text-center">
            <v-card-text>
              <v-icon size="48" color="primary" class="mb-2">mdi-calendar-check</v-icon>
              <div class="text-h5 text-white">{{ stats.totalDays }}</div>
              <div class="text-grey-400">Días Trabajados</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card class="bg-dark-surface border border-blue-500/20 text-center">
            <v-card-text>
              <v-icon size="48" color="success" class="mb-2">mdi-clock-in</v-icon>
              <div class="text-h5 text-white">{{ stats.onTimeDays }}</div>
              <div class="text-grey-400">A Tiempo</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card class="bg-dark-surface border border-blue-500/20 text-center">
            <v-card-text>
              <v-icon size="48" color="warning" class="mb-2">mdi-clock-alert</v-icon>
              <div class="text-h5 text-white">{{ stats.lateDays }}</div>
              <div class="text-grey-400">Llegadas Tarde</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card class="bg-dark-surface border border-blue-500/20 text-center">
            <v-card-text>
              <v-icon size="48" color="info" class="mb-2">mdi-percent</v-icon>
              <div class="text-h5 text-white">{{ stats.attendanceRate }}%</div>
              <div class="text-grey-400">Tasa de Asistencia</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Historial de Asistencias -->
      <v-card class="bg-dark-surface border border-blue-500/20">
                 <v-card-title class="text-white pb-2">
           Historial de Asistencias
           <v-spacer></v-spacer>
           
                       <!-- Filtro de Fechas -->
            <div class="d-flex align-center gap-2">
              <v-text-field
                v-model="dateFrom"
                label="Fecha Desde"
                type="date"
                density="compact"
                variant="outlined"
                class="max-width-150"
                color="primary"
                hide-details
                :max="today"
                :rules="[rules.dateNotFuture]"
                @update:model-value="validateAndFilterDate"
              ></v-text-field>
              
              <v-text-field
                v-model="dateTo"
                label="Fecha Hasta"
                type="date"
                density="compact"
                variant="outlined"
                class="max-width-150"
                color="primary"
                hide-details
                :max="today"
                :rules="[rules.dateNotFuture]"
                @update:model-value="validateAndFilterDate"
              ></v-text-field>
              
              <v-btn
                @click="clearDateFilter"
                variant="outlined"
                color="grey"
                size="small"
                prepend-icon="mdi-close"
              >
                Limpiar
              </v-btn>
            </div>
         </v-card-title>
        
        <v-card-text class="pt-0">
          <v-data-table
            :headers="headers"
            :items="filteredAttendances"
            :search="search"
            :loading="loading"
            class="bg-transparent"
            density="compact"
            hover
          >
            <template v-slot:item.date="{ item }">
              <span class="text-white">{{ formatDate(item.date) }}</span>
            </template>
            
            <template v-slot:item.check_in="{ item }">
              <span class="text-success">{{ formatTime(item.check_in) }}</span>
            </template>
            
            <template v-slot:item.check_out="{ item }">
              <span class="text-info">{{ item.check_out ? formatTime(item.check_out) : 'No registrado' }}</span>
            </template>
            
            <template v-slot:item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
                variant="tonal"
              >
                {{ getStatusText(item.status) }}
              </v-chip>
            </template>
            
            <template v-slot:item.area="{ item }">
              <span class="text-grey-300">{{ item.area || 'Sin área' }}</span>
            </template>
          </v-data-table>
        </v-card-text>
             </v-card>
     </div>
   </div>
 </div>
 </template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { attendanceService } from '../services/attendanceService'
import AppBar from '../components/AppBar.vue'

export default {
  name: 'EmployeeReports',
  components: {
    AppBar
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
         const loading = ref(true)
     const dateFrom = ref('')
     const dateTo = ref('')
     
     // Fecha actual para validaciones
     const today = ref(new Date().toISOString().split('T')[0])
    
    const employeeInfo = ref({
      fullName: '',
      employeeId: '',
      position: '',
      area: '',
      hireDate: ''
    })
    
    const stats = ref({
      totalDays: 0,
      onTimeDays: 0,
      lateDays: 0,
      attendanceRate: 0
    })
    
    const attendances = ref([])
    
         // Reglas de validación
     const rules = {
       dateNotFuture: (value) => {
         if (!value) return true
         const selectedDate = new Date(value)
         const currentDate = new Date()
         currentDate.setHours(0, 0, 0, 0)
         return selectedDate <= currentDate || 'La fecha no puede ser futura'
       }
     }
     
     const headers = [
       { title: 'Fecha', key: 'date', sortable: true },
       { title: 'Entrada', key: 'check_in', sortable: true },
       { title: 'Salida', key: 'check_out', sortable: true },
       { title: 'Estado', key: 'status', sortable: true },
       { title: 'Área', key: 'area', sortable: true }
     ]
    
         const filteredAttendances = computed(() => {
       let filtered = attendances.value
       
       // Filtro por rango de fechas
       if (dateFrom.value || dateTo.value) {
         filtered = filtered.filter(attendance => {
           const attendanceDate = new Date(attendance.date)
           
           if (dateFrom.value && dateTo.value) {
             // Ambas fechas seleccionadas
             const fromDate = new Date(dateFrom.value)
             const toDate = new Date(dateTo.value)
             toDate.setHours(23, 59, 59) // Incluir todo el día hasta
             
             return attendanceDate >= fromDate && attendanceDate <= toDate
           } else if (dateFrom.value) {
             // Solo fecha desde
             const fromDate = new Date(dateFrom.value)
             return attendanceDate >= fromDate
           } else if (dateTo.value) {
             // Solo fecha hasta
             const toDate = new Date(dateTo.value)
             toDate.setHours(23, 59, 59) // Incluir todo el día hasta
             return attendanceDate <= toDate
           }
           
           return true
         })
       }
       
       return filtered
     })
    
    const loadEmployeeData = async () => {
      try {
        loading.value = true
        
        // Cargar información del empleado
        const employeeData = await attendanceService.getEmployeeInfo()
        employeeInfo.value = employeeData
        
        // Cargar estadísticas del empleado
        const statsData = await attendanceService.getEmployeeStats()
        stats.value = statsData
        
        // Cargar historial de asistencias
        const attendancesData = await attendanceService.getEmployeeAttendances()
        console.log('📊 Datos de asistencias recibidos:', attendancesData)
        
        // Log detallado de cada asistencia para debugging
        if (attendancesData && Array.isArray(attendancesData)) {
          attendancesData.forEach((attendance, index) => {
            console.log(`📅 Asistencia ${index + 1}:`, {
              date: attendance.date,
              check_in: attendance.check_in,
              check_out: attendance.check_out,
              status: attendance.status,
              area: attendance.area
            })
          })
        }
        
        attendances.value = attendancesData
        
      } catch (error) {
        console.error('Error cargando datos del empleado:', error)
      } finally {
        loading.value = false
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'Sin fecha'
      
      try {
        // Intentar parsear la fecha
        const date = new Date(dateString)
        
        // Verificar si la fecha es válida
        if (isNaN(date.getTime())) {
          console.warn('⚠️ Fecha inválida recibida:', dateString)
          return 'Fecha inválida'
        }
        
        // Formatear la fecha
        return date.toLocaleDateString('es-ES', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      } catch (error) {
        console.error('❌ Error formateando fecha:', error, 'Valor:', dateString)
        return 'Error de formato'
      }
    }
    
    const formatTime = (timeString) => {
      if (!timeString) return 'No registrado'
      
      try {
        // Si solo es hora (formato HH:MM:SS), convertir a fecha completa
        if (typeof timeString === 'string' && timeString.match(/^\d{2}:\d{2}:\d{2}/)) {
          console.log('🕐 Formato de hora detectado:', timeString)
          
          // Crear fecha de hoy con la hora especificada
          const today = new Date()
          const [hours, minutes, seconds] = timeString.split(':')
          
          const time = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 
                               parseInt(hours), parseInt(minutes), parseInt(seconds))
          
          const formattedTime = time.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
          })
          
          console.log('✅ Hora formateada exitosamente:', formattedTime)
          return formattedTime
        }
        
        // Si es una fecha completa, parsear normalmente
        const time = new Date(timeString)
        
        // Verificar si la fecha es válida
        if (isNaN(time.getTime())) {
          console.warn('⚠️ Fecha inválida recibida:', timeString)
          return 'Fecha inválida'
        }
        
        // Formatear la hora
        return time.toLocaleTimeString('es-ES', {
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        console.error('❌ Error formateando tiempo:', error, 'Valor:', timeString)
        return 'Error de formato'
      }
    }
    
    const getStatusColor = (status) => {
      switch (status) {
        case 'present': return 'success'
        case 'late': return 'warning'
        case 'absent': return 'error'
        case 'half_day': return 'info'
        default: return 'primary'
      }
    }
    
    const getStatusText = (status) => {
      switch (status) {
        case 'present': return 'Presente'
        case 'late': return 'Llegada Tarde'
        case 'absent': return 'Ausente'
        case 'half_day': return 'Medio Día'
        default: return 'Registrado'
      }
    }
    
         // Función para validar y filtrar por rango de fechas
     const validateAndFilterDate = () => {
       // Validar que fecha desde no sea mayor que fecha hasta
       if (dateFrom.value && dateTo.value && dateFrom.value > dateTo.value) {
         console.warn('⚠️ Fecha desde mayor que fecha hasta, intercambiando...')
         const temp = dateFrom.value
         dateFrom.value = dateTo.value
         dateTo.value = temp
       }
       
       // Validar que no sean fechas futuras
       const currentDate = new Date().toISOString().split('T')[0]
       
       if (dateFrom.value && dateFrom.value > currentDate) {
         console.warn('⚠️ Fecha desde es futura, limpiando...')
         dateFrom.value = ''
       }
       
       if (dateTo.value && dateTo.value > currentDate) {
         console.warn('⚠️ Fecha hasta es futura, limpiando...')
         dateTo.value = ''
       }
       
       console.log('📅 Filtro de fechas validado y aplicado:', { 
         dateFrom: dateFrom.value, 
         dateTo: dateTo.value 
       })
     }
     
     // Función para limpiar filtros de fecha
     const clearDateFilter = () => {
       dateFrom.value = ''
       dateTo.value = ''
       console.log('🧹 Filtros de fecha limpiados')
     }
     
     onMounted(() => {
       loadEmployeeData()
     })
    
    
    
         return {
       loading,
       dateFrom,
       dateTo,
       today,
       rules,
       employeeInfo,
       stats,
       attendances,
       headers,
       filteredAttendances,
       formatDate,
       formatTime,
       getStatusColor,
       getStatusText,
       validateAndFilterDate,
       clearDateFilter
     }
  }
}
</script>

<style scoped>
 .max-width-150 {
   max-width: 150px;
 }
 
 .max-width-200 {
   max-width: 200px;
 }
 
 /* Estilos para campos de fecha con validación */
 .date-field-error {
   border-color: #f44336 !important;
 }
 
 .date-field-error :deep(.v-field__outline) {
   border-color: #f44336 !important;
 }

.v-data-table {
  background: transparent !important;
}

.v-data-table :deep(.v-data-table__wrapper) {
  background: transparent !important;
}

.v-data-table :deep(.v-data-table-header) {
  background: rgba(59, 130, 246, 0.1) !important;
}

.v-data-table :deep(.v-data-table__tr) {
  background: transparent !important;
}

.v-data-table :deep(.v-data-table__td) {
  background: transparent !important;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2) !important;
}
</style>
