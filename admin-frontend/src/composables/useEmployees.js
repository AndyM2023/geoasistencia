import { ref, computed, onMounted } from 'vue'
import { employeeService } from '../services/employeeService'
import areaService from '../services/areaService'
import { useNotifications } from './useNotifications'

export function useEmployees() {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications()
  
  // Estado reactivo
  const employees = ref([])
  const areas = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const showDialog = ref(false)
  const editingEmployee = ref(null)
  const searchQuery = ref('')
  const viewMode = ref('table') // 'table' o 'cards'
  
  // Computed properties
  const filteredEmployees = computed(() => {
    let filtered = employees.value
    
    // Filtro por búsqueda
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(employee => 
        employee.user.first_name.toLowerCase().includes(query) ||
        employee.user.last_name.toLowerCase().includes(query) ||
        employee.cedula_display?.toLowerCase().includes(query) ||
        employee.user.email.toLowerCase().includes(query)
      )
    }
    
    return filtered
  })
  
  // Métodos para CRUD
  const loadEmployees = async () => {
    try {
      loading.value = true
      const response = await employeeService.getAll()
      employees.value = response
      console.log('✅ Empleados cargados:', employees.value.length, 'encontrados')
    } catch (error) {
      console.error('❌ Error al cargar empleados:', error)
      showError('Error al cargar empleados')
    } finally {
      loading.value = false
    }
  }
  
  const loadAreas = async () => {
    try {
      console.log('🔄 Cargando áreas...')
      const response = await areaService.getAll()
      console.log('📥 Respuesta del servicio de áreas:', response)
      
      // El backend devuelve {count: 33, results: [...]}
      if (response && response.results) {
        areas.value = response.results
        console.log('✅ Áreas cargadas desde response.results:', areas.value.length, 'encontradas')
      } else if (Array.isArray(response)) {
        areas.value = response
        console.log('✅ Áreas cargadas desde array directo:', areas.value.length, 'encontradas')
      } else {
        console.warn('⚠️ Formato de respuesta inesperado:', response)
        areas.value = []
      }
      
      console.log('📋 Lista de áreas:', areas.value)
    } catch (error) {
      console.error('❌ Error al cargar áreas:', error)
      showError('Error al cargar áreas')
    }
  }
  
  const createEmployee = async (employeeData) => {
    try {
      saving.value = true
      const response = await employeeService.create(employeeData)
      await loadEmployees() // Recargar lista
      showSuccess('✅ Empleado creado exitosamente')
      return response
    } catch (error) {
      console.error('❌ Error al crear empleado:', error)
      showError('Error al crear empleado: ' + (error.response?.data?.message || error.message))
      throw error
    } finally {
      saving.value = false
    }
  }
  
  const updateEmployee = async (employeeData) => {
    try {
      saving.value = true
      const response = await employeeService.update(editingEmployee.value.id, employeeData)
      await loadEmployees() // Recargar lista
      showSuccess('✅ Empleado actualizado exitosamente')
      return response
    } catch (error) {
      console.error('❌ Error al actualizar empleado:', error)
      showError('Error al actualizar empleado: ' + (error.response?.data?.message || error.message))
      throw error
    } finally {
      saving.value = false
    }
  }
  
  const deleteEmployee = async (employeeId) => {
    try {
      await employeeService.delete(employeeId)
      await loadEmployees() // Recargar lista
      showSuccess('✅ Empleado eliminado exitosamente')
    } catch (error) {
      console.error('❌ Error al eliminar empleado:', error)
      showError('Error al eliminar empleado: ' + (error.response?.data?.message || error.message))
      throw error
    }
  }
  

  
  // Métodos para UI
  const openCreateDialog = () => {
    editingEmployee.value = null
    showDialog.value = true
  }
  
  const openEditDialog = (employee) => {
    editingEmployee.value = employee
    showDialog.value = true
  }
  
  const closeDialog = () => {
    showDialog.value = false
    editingEmployee.value = null
  }
  
  const saveEmployee = async (employeeData) => {
    try {
      let result
      if (editingEmployee.value) {
        result = await updateEmployee(employeeData)
      } else {
        result = await createEmployee(employeeData)
      }
      // No cerrar el diálogo aquí, retornar el resultado
      return result
    } catch (error) {
      // Error ya manejado en los métodos individuales
      console.error('Error en saveEmployee:', error)
      throw error
    }
  }
  
  const toggleViewMode = () => {
    viewMode.value = viewMode.value === 'table' ? 'cards' : 'table'
  }
  
  const clearFilters = () => {
    searchQuery.value = ''
  }
  
  // Inicialización
  onMounted(async () => {
    await Promise.all([loadEmployees(), loadAreas()])
  })
  
  return {
    // Estado
    employees,
    areas, // Retornar el estado de áreas
    loading,
    saving,
    showDialog,
    editingEmployee,
    searchQuery,
    viewMode,
    
    // Computed
    filteredEmployees,
    
          // Métodos CRUD
      loadEmployees,
      loadAreas,
      createEmployee,
      updateEmployee,
      deleteEmployee,
    
    // Métodos UI
    openCreateDialog,
    openEditDialog,
    closeDialog,
    saveEmployee,
    toggleViewMode,
    clearFilters
  }
}
