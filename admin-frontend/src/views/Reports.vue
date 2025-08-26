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
      @clear-search="search = ''"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import ReportFilters from '../components/reports/ReportFilters.vue'
import ReportStats from '../components/reports/ReportStats.vue'
import ReportTable from '../components/reports/ReportTable.vue'
import ReportChart from '../components/reports/ReportChart.vue'
import ReportMessages from '../components/reports/ReportMessages.vue'
import { attendanceService } from '../services/attendanceService'
import { employeeService } from '../services/employeeService'
import areaService from '../services/areaService'
import { useAuthStore } from '../stores/auth'
import { useNotifications } from '../composables/useNotifications'
import * as XLSX from 'xlsx'

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
    const authStore = useAuthStore()
    const { showSuccess, showError, showInfo, showWarning } = useNotifications()
    
    // Verificar autenticación
    if (!authStore.isAuthenticated) {
      console.error('❌ Usuario no autenticado')
      return
    }
    
    console.log('✅ Usuario autenticado:', authStore.user)
    console.log('🔑 Token disponible:', authStore.token ? 'SÍ' : 'NO')
    
    const search = ref('')
    const loading = ref(false)
    const generating = ref(false)
    const tableKey = ref(0)
    
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
      { title: 'Horas Trabajadas', key: 'hours_worked', sortable: true }
    ]
    
    const filteredReportData = computed(() => {
      console.log('🔄 === COMPUTED filteredReportData EJECUTADO ===');
      console.log('🔍 search.value:', search.value);
      console.log('🔍 search.value?.trim():', search.value?.trim());
      console.log('🔍 search.value?.trim() === "":', search.value?.trim() === "");
      console.log('📊 reportData.value.length:', reportData.value.length);
      
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
        
        if (item.employee_name) {
          const employeeName = item.employee_name.toLowerCase();
          if (employeeName.includes(searchTerm) || 
              employeeName.split(' ').some(word => word.includes(searchTerm))) {
            console.log('✅ Encontrado en nombre:', item.employee_name);
            return true;
          }
        }
        
        if (item.area_name && item.area_name.toLowerCase().includes(searchTerm)) {
          console.log('✅ Encontrado en área:', item.area_name);
          return true;
        }
        
        if (item.status) {
          const statusText = getStatusText(item.status).toLowerCase();
          if (statusText.includes(searchTerm)) {
            console.log('✅ Encontrado en estado:', getStatusText(item.status));
            return true;
          }
        }
        
        if (item.date) {
          const formattedDate = formatDate(item.date).toLowerCase();
          if (formattedDate.includes(searchTerm)) {
            console.log('✅ Encontrado en fecha:', formattedDate);
            return true;
          }
        }
        
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
        if (!authStore.isAuthenticated) {
          console.error('❌ No se pueden cargar empleados: usuario no autenticado')
          return
        }
        
        const employeesData = await employeeService.getAll()
        console.log('📊 Datos brutos de empleados recibidos:', employeesData)
        
        employees.value = employeesData.results || employeesData
        console.log('👥 Empleados procesados:', employees.value)
        
        if (employees.value.length > 0) {
          console.log('🔍 Estructura del primer empleado:', employees.value[0])
          console.log('🔍 Campos disponibles:', Object.keys(employees.value[0]))
          
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
        if (!authStore.isAuthenticated) {
          console.error('❌ No se pueden cargar áreas: usuario no autenticado')
          return
        }
        
        const areasData = await areaService.getAll()
        areas.value = areasData.results || areasData
      } catch (error) {
        console.error('Error cargando áreas:', error)
      }
    }

    // Watcher para la búsqueda
    watch(search, (newSearch, oldSearch) => {
      console.log('🔍 Búsqueda cambiada:', {
        anterior: oldSearch,
        nueva: newSearch,
        longitud: newSearch?.length || 0
      });
      
      console.log('🔄 Forzando recálculo de filteredReportData...');
      console.log('📊 Estado actual de filteredReportData:', filteredReportData.value.length);
      
      tableKey.value++;
      console.log('🔄 Tabla forzada a re-renderizar con key:', tableKey.value);
    }, { immediate: true, deep: true });
    
    const generateReport = async () => {
      if (!authStore.isAuthenticated) {
        showError('No estás autenticado. Por favor, inicia sesión.', {
          title: '❌ No Autenticado',
          icon: 'mdi-account-lock'
        })
        return
      }
      
      generating.value = true
      loading.value = true
      
      try {
        console.log('🔍 Generando reporte con filtros:', filters.value);
        console.log('🔑 Token de autenticación:', localStorage.getItem('token') ? 'SÍ' : 'NO');
        console.log('🔑 Token preview:', localStorage.getItem('token')?.substring(0, 30) + '...');
        
        if (filters.value.dateFrom && filters.value.dateTo) {
          const fromDate = new Date(filters.value.dateFrom);
          const toDate = new Date(filters.value.dateTo);
          
          if (fromDate > toDate) {
            throw new Error('La fecha "Desde" no puede ser mayor que la fecha "Hasta"');
          }
        }
        
        const reportFilters = {};
        
        if (filters.value.employee) {
          reportFilters.employee = filters.value.employee;
          
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
          const fromDate = new Date(filters.value.dateFrom);
          const toDate = new Date(filters.value.dateTo);
          
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
        
        let responseData;
        console.log('🚀 Iniciando petición al servicio...');
        
        if (filters.value.dateFrom && filters.value.dateTo) {
          console.log('📅 Usando getByDateRange con fechas:', filters.value.dateFrom, filters.value.dateTo);
          responseData = await attendanceService.getByDateRange(
            filters.value.dateFrom, 
            filters.value.dateTo, 
            reportFilters
          );
        } else {
          console.log('📊 Usando getAll con filtros:', reportFilters);
          responseData = await attendanceService.getAll(reportFilters);
        }
        
        console.log('✅ Datos obtenidos del servicio:', responseData);
        
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
        
        reportData.value = [];
        showError(errorMessage, {
          title: '❌ Error de Generación',
          icon: 'mdi-chart-line-off'
        })
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
    
    const exportReport = async () => {
      try {
        if (!reportData.value.length) {
          showWarning('No hay datos para exportar', {
            title: '⚠️ Sin Datos',
            icon: 'mdi-database-off'
          })
          return;
        }

        const exportBtn = document.querySelector('[data-export-btn]');
        if (exportBtn) {
          exportBtn.disabled = true;
          exportBtn.innerHTML = '<v-progress-circular indeterminate size="20"></v-progress-circular> Exportando...';
        }

        const excelData = reportData.value.map(item => ({
          'Fecha': formatDate(item.date),
          'Empleado': item.employee_name || '',
          'Área': item.area_name || '',
          'Entrada': item.check_in ? formatTime(item.check_in) : '--',
          'Salida': item.check_out ? formatTime(item.check_out) : '--',
          'Estado': getStatusText(item.status),
          'Horas Trabajadas': item.hours_worked ? `${item.hours_worked}h` : '--',
          'Verificación Facial': item.face_verified ? 'Sí' : 'No',
          'Latitud': item.latitude || '--',
          'Longitud': item.longitude || '--'
        }));

        const now = new Date();
        const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-');
        const fileName = `Reporte_Asistencia_${timestamp}.xlsx`;

        const workbook = XLSX.utils.book_new();
        const worksheet = XLSX.utils.json_to_sheet(excelData);

        const columnWidths = [
          { wch: 12 }, // Fecha
          { wch: 25 }, // Empleado
          { wch: 20 }, // Área
          { wch: 10 }, // Entrada
          { wch: 10 }, // Salida
          { wch: 12 }, // Estado
          { wch: 15 }, // Horas Trabajadas
          { wch: 15 }, // Verificación Facial
          { wch: 12 }, // Latitud
          { wch: 12 }  // Longitud
        ];
        worksheet['!cols'] = columnWidths;

        XLSX.utils.book_append_sheet(workbook, worksheet, 'Reporte de Asistencia');
        XLSX.writeFile(workbook, fileName);

        console.log('✅ Reporte exportado exitosamente:', fileName);
        
        showSuccess(`Reporte exportado exitosamente como: ${fileName}`, {
          title: '✅ Exportación Exitosa',
          icon: 'mdi-file-excel'
        })

      } catch (error) {
        console.error('❌ Error exportando reporte:', error);
        showError('Error al exportar el reporte. Por favor, inténtalo de nuevo.', {
          title: '❌ Error de Exportación',
          icon: 'mdi-file-excel-off'
        })
      } finally {
        const exportBtn = document.querySelector('[data-export-btn]');
        if (exportBtn) {
          exportBtn.disabled = false;
          exportBtn.innerHTML = 'Exportar Excel';
        }
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      
      try {
        if (typeof dateString === 'string' && dateString.includes('-')) {
          const [year, month, day] = dateString.split('-');
          return `${day}/${month}/${year}`;
        }
        
        if (dateString instanceof Date) {
          const day = String(dateString.getDate()).padStart(2, '0');
          const month = String(dateString.getMonth() + 1).padStart(2, '0');
          const year = dateString.getFullYear();
          return `${day}/${month}/${year}`;
        }
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
          console.warn('⚠️ Fecha inválida:', dateString);
          return dateString;
        }
        
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          timeZone: 'America/Guayaquil'
        });
        
      } catch (error) {
        console.error('❌ Error formateando fecha:', error, dateString);
        return dateString;
      }
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
    
    onMounted(async () => {
      if (!authStore.isAuthenticated) {
        console.error('❌ Usuario no autenticado en onMounted')
        return
      }
      
      console.log('🚀 Reports.vue montado, usuario autenticado, cargando datos...')
      await loadEmployees()
      await loadAreas()
    })
    
    return {
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
      chartData,
      filteredReportData,
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

<style>
@import '../style/reports.css';
</style>
