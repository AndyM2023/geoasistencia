<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4 text-white">Reportes de Asistencia</h1>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-card class="mb-6">
      <v-card-title class="d-flex align-center justify-space-between">
        <span>Filtros</span>
        <div class="d-flex align-center">
          <v-select
            v-model="filters.status"
            label="Estado"
            :items="[
              { title: 'Todos', value: 'all' },
              { title: 'Presente', value: 'present' },
              { title: 'Ausente', value: 'absent' },
              { title: 'Tarde', value: 'late' }
            ]"
            item-title="title"
            item-value="value"
            variant="outlined"
            density="compact"
            style="min-width: 150px; max-width: 200px;"
          ></v-select>
          

        </div>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.employee"
              label="Empleado"
              :items="[
                { title: 'Todos los empleados', value: null },
                ...employees.map(emp => ({
                  title: emp.user.full_name,
                  value: emp.id
                }))
              ]"
              item-title="title"
              item-value="value"
              variant="outlined"
              density="compact"
            ></v-select>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.area"
              label="Área"
              :items="[
                { title: 'Todas las áreas', value: null },
                ...areas.map(area => ({
                  title: area.name,
                  value: area.id
                }))
              ]"
              item-title="title"
              item-value="value"
              variant="outlined"
              density="compact"
              :disabled="filters.employee !== null"
              :prepend-icon="filters.employee ? 'mdi-lock' : 'mdi-map-marker'"
              :color="filters.employee ? 'warning' : 'primary'"
            ></v-select>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-menu v-model="showDatePickerFrom" :close-on-content-click="false">
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="formattedDateFrom"
                  label="Desde"
                  readonly
                  v-bind="props"
                  variant="outlined"
                  density="compact"
                  prepend-icon="mdi-calendar"
                  :hint="filters.dateTo && new Date(filters.dateFrom) > new Date(filters.dateTo) ? 'Fecha debe ser menor que Hasta' : ''"
                  :error="filters.dateTo && new Date(filters.dateFrom) > new Date(filters.dateTo)"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="filters.dateFrom"
                @update:model-value="showDatePickerFrom = false"
                :max="filters.dateTo"
                :format="'DD/MM/YYYY'"
              ></v-date-picker>
            </v-menu>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-menu v-model="showDatePickerTo" :close-on-content-click="false">
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="formattedDateTo"
                  label="Hasta"
                  readonly
                  v-bind="props"
                  variant="outlined"
                  density="compact"
                  prepend-icon="mdi-calendar"
                  :hint="filters.dateFrom && new Date(filters.dateFrom) > new Date(filters.dateTo) ? 'Fecha debe ser mayor que Desde' : ''"
                  :error="filters.dateFrom && new Date(filters.dateFrom) > new Date(filters.dateTo)"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="filters.dateTo"
                @update:model-value="showDatePickerTo = false"
                :min="filters.dateFrom"
                :format="'DD/MM/YYYY'"
              ></v-date-picker>
            </v-menu>
          </v-col>
        </v-row>
        
        <v-row class="mt-0">
          <v-col cols="12" class="text-center">
            
            <v-btn color="primary" @click="generateReport" :loading="generating" :disabled="!canGenerateReport">
              Generar Reporte
            </v-btn>
            <v-btn color="secondary" @click="exportReport" :disabled="!reportData.length" class="ml-2">
              Exportar Excel
            </v-btn>
            <v-btn color="outline" @click="clearFilters" class="ml-2">
              Limpiar Filtros
            </v-btn>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12">
            
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
        <div class="d-flex align-center">
          <span>Reporte de Asistencia</span>
          <v-chip 
            v-if="search.trim()" 
            :color="filteredReportData.length > 0 ? 'success' : 'warning'"
            size="small" 
            class="ml-3"
          >
            <v-icon size="small" class="mr-1">
              {{ filteredReportData.length > 0 ? 'mdi-check' : 'mdi-alert' }}
            </v-icon>
            {{ filteredReportData.length }} de {{ reportData.length }} resultados
          </v-chip>
          
          <!-- Indicador de búsqueda activa -->
          <v-chip 
            v-if="search.trim()" 
            color="info" 
            size="small" 
            class="ml-2"
          >
            <v-icon size="small" class="mr-1">mdi-magnify</v-icon>
            Búsqueda activa
          </v-chip>
          
          <!-- Debug info -->
          <v-chip 
            v-if="search.trim()" 
            color="warning" 
            size="small" 
            class="ml-2"
          >
            <v-icon size="small" class="mr-1">mdi-information</v-icon>
            Key: {{ tableKey }}
          </v-chip>
        </div>
        <v-spacer></v-spacer>
        <div class="d-flex align-center">
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Buscar"
            placeholder="Buscar por nombre, área, estado..."
            single-line
            hide-details
            variant="outlined"
            density="compact"
            style="max-width: 300px"
            clearable
            :hint="search.trim() ? '' : 'Escribe para filtrar los resultados'"
            persistent-hint
          ></v-text-field>
        </div>
      </v-card-title>

      <v-data-table
        :key="`table-${tableKey}-${search.trim()}-${filteredReportData.length}`"
        :headers="headers"
        :items="filteredReportData"
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

    <!-- Mensaje cuando no hay resultados de búsqueda -->
    <v-card v-if="reportData.length > 0 && filteredReportData.length === 0 && search.trim()" class="text-center pa-8">
      <v-icon size="64" color="warning">mdi-magnify</v-icon>
      <div class="text-h6 mt-4">No se encontraron resultados</div>
      <div class="text-body-2 text-grey">
        No hay resultados para "{{ search }}". 
        <v-btn 
          text 
          color="primary" 
          @click="search = ''"
          class="ml-2"
        >
          Limpiar búsqueda
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<style scoped>
/* Estilos específicos para los filtros si son necesarios */
</style>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import AttendancePieChart from '../components/charts/AttendancePieChart.vue'
import { attendanceService } from '../services/attendanceService'
import { employeeService } from '../services/employeeService'
import areaService from '../services/areaService'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Reports',
  components: {
    AttendancePieChart
  },
  setup() {
    const authStore = useAuthStore()
    
    // Verificar autenticación
    if (!authStore.isAuthenticated) {
      console.error('❌ Usuario no autenticado')
      // Redirigir al login o mostrar error
      return
    }
    
    console.log('✅ Usuario autenticado:', authStore.user)
    console.log('🔑 Token disponible:', authStore.token ? 'SÍ' : 'NO')
    
    const search = ref('')
    const loading = ref(false)
    const generating = ref(false)
    const showDatePickerFrom = ref(false)
    const showDatePickerTo = ref(false)
    const tableKey = ref(0) // Para forzar re-renderizado de la tabla
    
    const filters = ref({
      employee: null,
      area: null,
      dateFrom: null,
      dateTo: null,
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
    
    const filteredReportData = computed(() => {
      console.log('🔄 === COMPUTED filteredReportData EJECUTADO ===');
      console.log('🔍 search.value:', search.value);
      console.log('🔍 search.value?.trim():', search.value?.trim());
      console.log('🔍 search.value?.trim() === "":', search.value?.trim() === "");
      console.log('📊 reportData.value.length:', reportData.value.length);
      
      // Validación más estricta de la búsqueda
      if (!search.value || search.value.trim() === "") {
        console.log('✅ Sin búsqueda activa, retornando todos los datos');
        return reportData.value;
      }
      
      console.log('🔍 BÚSQUEDA ACTIVA - Valor:', search.value);
      console.log('📊 Datos disponibles:', reportData.value.length);
      
      const searchTerm = search.value.toLowerCase().trim();
      console.log('🔍 Buscando término:', `"${searchTerm}"`, 'en', reportData.value.length, 'registros');
      
      const filtered = reportData.value.filter(item => {
        console.log('🔍 Analizando item:', {
          employee_name: item.employee_name,
          area_name: item.area_name,
          status: item.status
        });
        
        // Buscar en nombre del empleado (búsqueda más flexible)
        if (item.employee_name) {
          const employeeName = item.employee_name.toLowerCase();
          if (employeeName.includes(searchTerm) || 
              employeeName.split(' ').some(word => word.includes(searchTerm))) {
            console.log('✅ Encontrado en nombre:', item.employee_name);
            return true;
          }
        }
        
        // Buscar en área
        if (item.area_name && item.area_name.toLowerCase().includes(searchTerm)) {
          console.log('✅ Encontrado en área:', item.area_name);
          return true;
        }
        
        // Buscar en estado
        if (item.status) {
          const statusText = getStatusText(item.status).toLowerCase();
          if (statusText.includes(searchTerm)) {
            console.log('✅ Encontrado en estado:', getStatusText(item.status));
            return true;
          }
        }
        
        // Buscar en fecha (formateada)
        if (item.date) {
          const formattedDate = formatDate(item.date).toLowerCase();
          if (formattedDate.includes(searchTerm)) {
            console.log('✅ Encontrado en fecha:', formattedDate);
            return true;
          }
        }
        
        // Buscar en horas trabajadas
        if (item.hours_worked && item.hours_worked.toString().includes(searchTerm)) {
          console.log('✅ Encontrado en horas trabajadas:', item.hours_worked);
          return true;
        }
        
        console.log('❌ No encontrado en este item');
        return false;
      });
      
      console.log('🎯 Resultados filtrados:', filtered.length, 'de', reportData.value.length);
      console.log('🔄 === FIN COMPUTED filteredReportData ===');
      return filtered;
    });

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
        // Verificar autenticación
        if (!authStore.isAuthenticated) {
          console.error('❌ No se pueden cargar empleados: usuario no autenticado')
          return
        }
        
        // CARGAR DESDE API REAL
        const employeesData = await employeeService.getAll()
        console.log('📊 Datos brutos de empleados recibidos:', employeesData)
        
        // El backend devuelve {count, next, previous, results}
        // Necesitamos acceder a results que es el array de empleados
        employees.value = employeesData.results || employeesData
        console.log('👥 Empleados procesados:', employees.value)
        
        // Verificar estructura de cada empleado
        if (employees.value.length > 0) {
          console.log('🔍 Estructura del primer empleado:', employees.value[0])
          console.log('🔍 Campos disponibles:', Object.keys(employees.value[0]))
          
          // Verificar que el mapeo funcione correctamente
          const mappedEmployees = employees.value.map(emp => ({
            title: emp.user?.full_name || 'Nombre no disponible',
            value: emp.id
          }))
          console.log('🎯 Empleados mapeados para el filtro:', mappedEmployees)
        }
        
      } catch (error) {
        console.error('Error cargando empleados:', error)
      }
    }
    
    const loadAreas = async () => {
      try {
        // Verificar autenticación
        if (!authStore.isAuthenticated) {
          console.error('❌ No se pueden cargar áreas: usuario no autenticado')
          return
        }
        
        // CARGAR DESDE API REAL
        const areasData = await areaService.getAll()
        // El backend devuelve results que es el array de áreas
        areas.value = areasData.results || areasData
      } catch (error) {
        console.error('Error cargando áreas:', error)
      }
    }
    
    // Watcher para establecer automáticamente el área cuando se selecciona un empleado
    watch(() => filters.value.employee, (newEmployeeId) => {
      if (newEmployeeId) {
        // Buscar el empleado seleccionado
        const selectedEmployee = employees.value.find(emp => emp.id === newEmployeeId)
        console.log('🔍 Empleado seleccionado:', selectedEmployee)
        
        if (selectedEmployee && selectedEmployee.area) {
          // Establecer automáticamente el área del empleado
          filters.value.area = selectedEmployee.area
          console.log(`✅ Área automáticamente establecida para ${selectedEmployee.user?.full_name || 'Empleado'}: ${selectedEmployee.area}`)
        } else {
          console.log('⚠️ Empleado seleccionado pero sin área:', selectedEmployee)
        }
      } else {
        // Si se deselecciona el empleado, liberar el área
        filters.value.area = null
        console.log('🔄 Empleado deseleccionado, área liberada')
      }
    })

    // Watcher para la búsqueda
    watch(search, (newSearch, oldSearch) => {
      console.log('🔍 Búsqueda cambiada:', {
        anterior: oldSearch,
        nueva: newSearch,
        longitud: newSearch?.length || 0
      });
      
      // Forzar recálculo de filteredReportData
      console.log('🔄 Forzando recálculo de filteredReportData...');
      console.log('📊 Estado actual de filteredReportData:', filteredReportData.value.length);
      
      // Forzar re-renderizado de la tabla
      tableKey.value++;
      console.log('🔄 Tabla forzada a re-renderizar con key:', tableKey.value);
    }, { immediate: true, deep: true });
    
    const generateReport = async () => {
      // Verificar autenticación antes de proceder
      if (!authStore.isAuthenticated) {
        alert('❌ No estás autenticado. Por favor, inicia sesión.')
        return
      }
      
      generating.value = true
      loading.value = true
      
      try {
        console.log('🔍 Generando reporte con filtros:', filters.value);
        console.log('🔑 Token de autenticación:', localStorage.getItem('token') ? 'SÍ' : 'NO');
        console.log('🔑 Token preview:', localStorage.getItem('token')?.substring(0, 30) + '...');
        
        // Validar fechas si están seleccionadas
        if (filters.value.dateFrom && filters.value.dateTo) {
          const fromDate = new Date(filters.value.dateFrom);
          const toDate = new Date(filters.value.dateTo);
          
          if (fromDate > toDate) {
            throw new Error('La fecha "Desde" no puede ser mayor que la fecha "Hasta"');
          }
        }
        
        // Crear objeto de filtros para el servicio
        const reportFilters = {};
        
        // Aplicar filtros si están seleccionados
        if (filters.value.employee) {
          reportFilters.employee = filters.value.employee;
          
          // Verificar que el área esté establecida para el empleado seleccionado
          if (!filters.value.area) {
            const selectedEmployee = employees.value.find(emp => emp.id === filters.value.employee);
            if (selectedEmployee && selectedEmployee.area) {
              filters.value.area = selectedEmployee.area;
              reportFilters.area = selectedEmployee.area;
              console.log(`🔒 Área automáticamente establecida para reporte: ${selectedEmployee.area}`);
            }
          }
        }
        if (filters.value.area) {
          reportFilters.area = filters.value.area;
        }
        if (filters.value.status && filters.value.status !== 'all') {
          reportFilters.status = filters.value.status;
        }
        if (filters.value.dateFrom && filters.value.dateTo) {
          // Convertir fechas a formato YYYY-MM-DD usando zona horaria local
          const fromDate = new Date(filters.value.dateFrom);
          const toDate = new Date(filters.value.dateTo);
          
          // Usar toLocaleDateString para evitar problemas de zona horaria
          const formatDateToISO = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
          };
          
          reportFilters.dateFrom = formatDateToISO(fromDate);
          reportFilters.dateTo = formatDateToISO(toDate);
          
          console.log('📅 Fechas convertidas para backend:', {
            original: { from: filters.value.dateFrom, to: filters.value.dateTo },
            converted: { from: reportFilters.dateFrom, to: reportFilters.dateTo },
            fromDate: fromDate,
            toDate: toDate,
            fromDateLocal: fromDate.toLocaleDateString('es-EC'),
            toDateLocal: toDate.toLocaleDateString('es-EC')
          });
        }
        
        console.log('📊 Filtros aplicados:', reportFilters);
        console.log('🔑 Token de autenticación:', localStorage.getItem('token') ? 'SÍ' : 'NO');
        
        // Obtener datos con filtros aplicados
        let responseData;
        console.log('🚀 Iniciando petición al servicio...');
        
        if (filters.value.dateFrom && filters.value.dateTo) {
          // Usar rango de fechas específico
          console.log('📅 Usando getByDateRange con fechas:', filters.value.dateFrom, filters.value.dateTo);
          responseData = await attendanceService.getByDateRange(
            filters.value.dateFrom, 
            filters.value.dateTo, 
            reportFilters
          );
        } else {
          // Obtener todas las asistencias con filtros
          console.log('📊 Usando getAll con filtros:', reportFilters);
          responseData = await attendanceService.getAll(reportFilters);
        }
        
        console.log('✅ Datos obtenidos del servicio:', responseData);
        
        // Verificar que responseData sea un array
        if (Array.isArray(responseData)) {
          reportData.value = responseData;
          console.log('✅ Datos asignados correctamente:', reportData.value.length, 'registros');
        } else {
          console.warn('⚠️ Respuesta no es un array:', responseData);
          reportData.value = responseData.results || responseData.data || [];
          console.log('✅ Datos extraídos de respuesta:', reportData.value.length, 'registros');
        }
        
        calculateStats();
      } catch (error) {
        console.error('❌ Error generando reporte:', error);
        console.error('📡 Detalles del error:', {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          config: error.config
        });
        
        // Mostrar mensaje de error más detallado
        let errorMessage = 'Error generando reporte';
        if (error.response?.status === 500) {
          errorMessage = 'Error interno del servidor (500). Verifica que el backend esté funcionando.';
        } else if (error.response?.status === 401) {
          errorMessage = 'No autorizado. Verifica tu sesión.';
        } else if (error.response?.status === 404) {
          errorMessage = 'Endpoint no encontrado. Verifica la configuración del backend.';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        // Mostrar mensaje de error al usuario
        reportData.value = [];
        alert(errorMessage);
      } finally {
        generating.value = false;
        loading.value = false;
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

    const clearFilters = () => {
      filters.value = {
        employee: null,
        area: null,
        dateFrom: null,
        dateTo: null,
        status: 'all'
      }
      showDatePickerFrom.value = false
      showDatePickerTo.value = false
      search.value = ''
      console.log('🧹 Filtros limpiados, área liberada y búsqueda limpiada')
      // No generar reporte automáticamente al limpiar, solo limpiar los filtros
    }

    const formattedDateFrom = computed(() => {
      if (!filters.value.dateFrom) return '';
      return new Date(filters.value.dateFrom).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    });

    const formattedDateTo = computed(() => {
      if (!filters.value.dateTo) return '';
      return new Date(filters.value.dateTo).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    });

    const canGenerateReport = computed(() => {
      // Al menos debe tener un filtro activo o fechas seleccionadas
      const hasFilters = filters.value.employee !== undefined || 
                        filters.value.area !== undefined || 
                        filters.value.status !== 'all' ||
                        filters.value.dateFrom || 
                        filters.value.dateTo;
      
      // Si tiene fechas, ambas deben estar seleccionadas
      if (filters.value.dateFrom || filters.value.dateTo) {
        if (!filters.value.dateFrom || !filters.value.dateTo) {
          return false;
        }
        
        // Validar que la fecha "Desde" no sea mayor que "Hasta"
        const fromDate = new Date(filters.value.dateFrom);
        const toDate = new Date(filters.value.dateTo);
        if (fromDate > toDate) {
          return false;
        }
      }
      
      return hasFilters;
    })

    const activeFiltersCount = computed(() => {
      let count = 0;
      if (filters.value.employee !== undefined) count++;
      if (filters.value.area !== undefined) count++;
      if (filters.value.status !== 'all') count++;
      if (filters.value.dateFrom) count++;
      if (filters.value.dateTo) count++;
      return count;
    });
    
    onMounted(async () => {
      // Verificar autenticación antes de cargar datos
      if (!authStore.isAuthenticated) {
        console.error('❌ Usuario no autenticado en onMounted')
        return
      }
      
      console.log('🚀 Reports.vue montado, usuario autenticado, cargando datos...')
      await loadEmployees()
      await loadAreas()
    })

    const testAuth = () => {
      console.log('🔑 Token actual:', authStore.token);
      console.log('👤 Usuario actual:', authStore.user);
      console.log('🔑 Autenticación actual:', authStore.isAuthenticated);
      console.log('🔑 Token en localStorage:', localStorage.getItem('token'));
      console.log('🔑 Usuario en localStorage:', localStorage.getItem('user_data'));
      
      // Verificar si el token está expirado
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // Decodificar el token JWT (solo para ver la estructura, no para validar)
          const payload = JSON.parse(atob(token.split('.')[1]));
          const exp = new Date(payload.exp * 1000);
          const now = new Date();
          console.log('🔑 Token expira en:', exp);
          console.log('🔑 Tiempo actual:', now);
          console.log('🔑 Token expirado:', now > exp);
          
          if (now > exp) {
            alert('⚠️ El token ha expirado. Por favor, inicia sesión nuevamente.');
          } else {
            alert('✅ Token válido. Estado de autenticación (consola)');
          }
        } catch (e) {
          console.error('Error decodificando token:', e);
          alert('❌ Error decodificando token');
        }
      } else {
        alert('❌ No hay token disponible');
      }
    };

    const testBackendConnection = async () => {
      try {
        console.log('🌐 Probando conexión con el backend...');
        console.log('🔑 Token disponible:', localStorage.getItem('token') ? 'SÍ' : 'NO');
        
        // Usar la URL del proxy (que debería redirigir a localhost:8000)
        const response = await fetch('/app/attendance/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        console.log('📡 Status de respuesta:', response.status);
        console.log('📡 Headers de respuesta:', response.headers);
        
        if (response.ok) {
          const data = await response.json();
          console.log('✅ Respuesta de prueba del backend:', data);
          alert('✅ Conexión con el backend exitosa!');
        } else {
          console.error('❌ Error HTTP:', response.status, response.statusText);
          const errorText = await response.text();
          console.error('❌ Respuesta de error:', errorText);
          alert(`❌ Error HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.error('❌ Error de conexión con el backend:', error);
        alert('❌ Error de conexión con el backend. Verifica la configuración de la URL y el backend.');
      }
    };

    const testAttendanceService = async () => {
      try {
        console.log('📊 Probando el servicio de asistencia...');
        console.log('🔑 Token disponible:', localStorage.getItem('token') ? 'SÍ' : 'NO');
        
        // Intentar obtener todas las asistencias
        const response = await attendanceService.getAll();
        console.log('📊 Respuesta del servicio de asistencia (getAll):', response);
        alert('✅ Servicio de asistencia (getAll) funcionando correctamente!');
      } catch (error) {
        console.error('❌ Error al probar el servicio de asistencia:', error);
        console.error('📡 Detalles del error:', {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          config: error.config
        });
        alert('❌ Servicio de asistencia (getAll) no está funcionando. Verifica la configuración del backend.');
      }
    };






    
    return {
      search,
      loading,
      generating,
      showDatePickerFrom,
      showDatePickerTo,
      tableKey,
      filters,
      employees,
      areas,
      reportData,
      stats,
      headers,
      chartData,
      filteredReportData,
      formattedDateFrom,
      formattedDateTo,
      generateReport,
      exportReport,
      formatDate,
      formatTime,
      getStatusColor,
      getStatusText,
      clearFilters,
      canGenerateReport,
      activeFiltersCount,
      testAuth,
      testBackendConnection,
      testAttendanceService
    }
  }
}
</script>
