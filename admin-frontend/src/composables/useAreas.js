import { ref, onMounted, onUnmounted } from 'vue'
import areaService from '../services/areaService'
import { useNotifications } from './useNotifications'

export default function useAreas() {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications()
  
  const areas = ref([])
  const loading = ref(false)
  const tableKey = ref(Date.now())
  const pollingInterval = ref(null)
  const POLLING_INTERVAL_MS = 30000 // 30 segundos
  
  // Función para ordenar áreas alfabéticamente
  const sortAreasAlphabetically = (areasArray) => {
    return areasArray.sort((a, b) => {
      const nameA = a.name.toLowerCase().trim()
      const nameB = b.name.toLowerCase().trim()
      return nameA.localeCompare(nameB, 'es', { 
        sensitivity: 'base',
        numeric: true,
        ignorePunctuation: true
      })
    })
  }
  
  const loadAreas = async () => {
    loading.value = true
    try {
      const areasData = await areaService.getAll()
      const areasArray = areasData.results || areasData
      
      console.log('📥 Datos crudos del backend:', areasData)
      console.log('📋 Array de áreas del backend:', areasArray)
      
      // Verificar si las áreas tienen schedule
      areasArray.forEach((area, index) => {
        console.log(`🔍 Área ${index + 1} (${area.name}):`, {
          id: area.id,
          name: area.name,
          hasSchedule: !!area.schedule,
          schedule: area.schedule,
          scheduleKeys: area.schedule ? Object.keys(area.schedule) : 'No schedule'
        })
      })
      
      // FILTRAR SOLO ÁREAS ACTIVAS para la lista principal
      const activeAreas = areasArray.filter(area => area.status === 'active')
      
      const areasWithCounts = activeAreas.map(area => ({
        ...area,
        employee_count: area.employee_count || 0,
        schedule: area.schedule || null
      }))
      
      // Ordenar alfabéticamente por nombre
      areas.value = sortAreasAlphabetically(areasWithCounts)
      
      console.log('✅ Áreas activas cargadas y ordenadas alfabéticamente:', areas.value.length, 'áreas')
      console.log('📋 Orden actual:', areas.value.map(area => area.name))
    } catch (error) {
      console.error('Error cargando áreas:', error)
      areas.value = []
      if (error.response?.status === 401) {
        alert('Error de autenticación. Por favor, inicia sesión nuevamente.')
      } else if (error.response?.status === 403) {
        alert('No tienes permisos para ver las áreas.')
      } else if (error.response?.status >= 500) {
        alert('Error del servidor. Por favor, intenta más tarde.')
      } else {
        alert('Error cargando áreas: ' + (error.response?.data?.message || error.message))
      }
    } finally {
      loading.value = false
    }
  }
  
  // Función de polling automático interno
  const startPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
    }
    
    pollingInterval.value = setInterval(async () => {
      if (!loading.value) {
        console.log('🔄 Polling automático: Recargando áreas...')
        await loadAreas()
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
  
  const editArea = async (area) => {
    try {
      console.log('✏️ Iniciando edición de área:', area.name)
      
      // Cargar datos completos del área desde la API
      const fullArea = await areaService.getById(area.id)
      
      console.log('📊 Datos completos del área desde BD:', fullArea)
      
      // Guardar las coordenadas para usar en el mapa
      fullArea.savedCoordinates = {
        lat: parseFloat(fullArea.latitude),
        lng: parseFloat(fullArea.longitude)
      }
      
      console.log('✅ Área cargada para edición:', fullArea)
      console.log('📍 Coordenadas para el mapa:', fullArea.savedCoordinates)
      
      return fullArea
    } catch (error) {
      console.error('❌ Error cargando área para editar:', error)
      alert('Error cargando área: ' + (error.response?.data?.message || error.message))
      return null
    }
  }
  
  const deleteArea = async (area) => {
    // Verificar si el área tiene empleados antes de permitir desactivarla
    if (area.employee_count > 0) {
      showWarning(`No se puede desactivar el área "${area.name}" porque tiene ${area.employee_count} empleado(s) asignado(s). Primero debes reasignar o desactivar los empleados.`)
      return false
    }
    
    try {
      // Eliminar desde API
      await areaService.delete(area.id)
      
      // Actualizar el estado del área en lugar de removerla
      const index = areas.value.findIndex(a => a.id === area.id)
      if (index !== -1) {
        areas.value[index].status = 'inactive'
      }
      
      showSuccess('Área desactivada correctamente')
      console.log('Área eliminada exitosamente')
      
      // Recargar la lista para mostrar el cambio de estado
      await loadAreas()
      return true
    } catch (error) {
      console.error('Error eliminando área:', error)
      alert('Error eliminando área: ' + (error.response?.data?.message || error.message))
      return false
    }
  }
  
  const activateArea = async (area) => {
    try {
      await areaService.activate(area.id)
      // Recargar áreas para actualizar el estado
      await loadAreas()
      showSuccess('Área reactivada correctamente')
      return true
    } catch (error) {
      console.error('Error reactivando área:', error)
      showError('Error reactivando área: ' + (error.response?.data?.message || error.message))
      return false
    }
  }
  
  // Función para reordenar la lista actual
  const reorderAreasList = () => {
    console.log('🔄 Reordenando lista de áreas alfabéticamente...')
    const currentOrder = areas.value.map(area => area.name)
    console.log('📋 Orden anterior:', currentOrder)
    
    areas.value = sortAreasAlphabetically([...areas.value])
    
    const newOrder = areas.value.map(area => area.name)
    console.log('📋 Nuevo orden:', newOrder)
    console.log('✅ Lista reordenada correctamente')
  }
  
  // ✅ Función para forzar actualización de la interfaz
  const forceUIUpdate = () => {
    console.log('🔄 Forzando actualización de la interfaz...')
    
    // ✅ Forzar re-render completo del componente
    areas.value = [...areas.value]
    
    // ✅ Forzar re-render de la tabla agregando un key único
    tableKey.value = Date.now()
    
    console.log('✅ Interfaz actualizada con re-render completo')
  }
  
  // ✅ Función para actualizar correctamente la lista local
  const updateLocalArea = (updatedAreaData) => {
    console.log('🔄 Actualizando área en lista local...')
    
    const areaIndex = areas.value.findIndex(area => area.id === updatedAreaData.id)
    if (areaIndex !== -1) {
      // ✅ Actualizar con los datos frescos del backend
      areas.value[areaIndex] = { ...updatedAreaData }
      console.log('✅ Área actualizada en la lista local')
      
      // ✅ Forzar re-render de la tabla
      tableKey.value = Date.now()
      
      // ✅ Verificar que se actualizó correctamente
      const updatedArea = areas.value[areaIndex]
      if (updatedArea.schedule) {
        console.log(`✅ Verificación: ${updatedArea.name} ahora tiene schedule_type = ${updatedArea.schedule.schedule_type}`)
      }
    } else {
      console.warn('⚠️ Área no encontrada en lista local para actualizar')
    }
  }
  
  onMounted(() => {
    loadAreas()
    // ✅ INICIAR POLLING AUTOMÁTICO
    startPolling()
    console.log('🚀 Composable useAreas cargado - Polling iniciado')
  })
  
  // ✅ LIMPIAR POLLING AL DESMONTAR EL COMPONENTE
  onUnmounted(() => {
    stopPolling()
    console.log('🧹 Composable useAreas desmontado - Polling detenido')
  })
  
  return {
    areas,
    loading,
    tableKey,
    loadAreas,
    editArea,
    deleteArea,
    activateArea,
    reorderAreasList,
    forceUIUpdate,
    updateLocalArea,
    sortAreasAlphabetically
  }
}
