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
  
  // Utilidad: ordenar alfabéticamente por nombre completo
  const sortEmployees = (list) => {
    const normalize = (s) => (s || '').toString().toLocaleLowerCase('es-ES')
    return [...list].sort((a, b) => {
      const aName = `${normalize(a?.user?.first_name)} ${normalize(a?.user?.last_name)}`.trim()
      const bName = `${normalize(b?.user?.first_name)} ${normalize(b?.user?.last_name)}`.trim()
      return aName.localeCompare(bName, 'es-ES')
    })
  }

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
    
    // Siempre devolver ordenados alfabéticamente
    return sortEmployees(filtered)
  })
  
  // Métodos para CRUD
  const loadEmployees = async () => {
    try {
      loading.value = true
      const response = await employeeService.getAll()
      employees.value = sortEmployees(response)
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
      await loadEmployees() // Recargar lista y quedará ordenada
      showSuccess('✅ Empleado creado exitosamente')
      return response
    } catch (error) {
      console.error('❌ Error al crear empleado:', error)
      const status = error.response?.status
      const rawData = error.response?.data

      // 1) Intentar construir mensaje desde errores de validación JSON
      if (rawData && typeof rawData === 'object' && !Array.isArray(rawData)) {
        const fieldMessages = []
        Object.keys(rawData).forEach((k) => {
          const val = rawData[k]
          if (Array.isArray(val)) {
            fieldMessages.push(`${k}: ${val.join(' ')}`)
          } else if (typeof val === 'string') {
            fieldMessages.push(`${k}: ${val}`)
          }
        })
        if (fieldMessages.length > 0) {
          showError('Error al crear empleado: ' + fieldMessages.join(' | '))
          throw error
        }
      }

      // 2) Detectar cédula duplicada incluso cuando viene como HTML (500 IntegrityError)
      const htmlText = typeof rawData === 'string' ? rawData : (rawData?.toString ? rawData.toString() : '')
      const looksLikeUniqueCedula =
        (status === 500 && /UNIQUE/i.test(htmlText) && /cedula/i.test(htmlText)) || /cedula.*ya existe/i.test(htmlText)
      if (looksLikeUniqueCedula) {
        showError('La cédula ya está registrada en el sistema. Usa una diferente.')
        throw error
      }

      // 3) Extraer <title> de la página de error de Django si existe para dar más detalle
      if (typeof htmlText === 'string' && htmlText.includes('<title')) {
        const match = htmlText.match(/<title>([^<]+)<\/title>/i)
        if (match && match[1]) {
          showError('Error al crear empleado: ' + match[1])
          throw error
        }
      }

      // 4) Fallback genérico
      showError('Error al crear empleado: ' + (error.response?.statusText || error.message))
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
      
      const status = error.response?.status
      const rawData = error.response?.data

      // 1) Intentar construir mensaje desde errores de validación JSON
      if (rawData && typeof rawData === 'object' && !Array.isArray(rawData)) {
        const fieldMessages = []
        Object.keys(rawData).forEach((k) => {
          const val = rawData[k]
          if (Array.isArray(val)) {
            fieldMessages.push(`${k}: ${val.join(' ')}`)
          } else if (typeof val === 'string') {
            fieldMessages.push(`${k}: ${val}`)
          }
        })
        if (fieldMessages.length > 0) {
          showError('Error al actualizar empleado: ' + fieldMessages.join(' | '))
          throw error
        }
      }

      // 2) Detectar cédula duplicada incluso cuando viene como HTML (500 IntegrityError)
      const htmlText = typeof rawData === 'string' ? rawData : (rawData?.toString ? rawData.toString() : '')
      const looksLikeUniqueCedula =
        (status === 500 && /UNIQUE/i.test(htmlText) && /cedula/i.test(htmlText)) || /cedula.*ya existe/i.test(htmlText)
      if (looksLikeUniqueCedula) {
        showError('La cédula ya está registrada en el sistema. Usa una diferente.')
        throw error
      }

      // 3) Extraer <title> de la página de error de Django si existe para dar más detalle
      if (typeof htmlText === 'string' && htmlText.includes('<title')) {
        const match = htmlText.match(/<title>([^<]+)<\/title>/i)
        if (match && match[1]) {
          showError('Error al actualizar empleado: ' + match[1])
          throw error
        }
      }

      // 4) Fallback genérico
      showError('Error al actualizar empleado: ' + (error.response?.statusText || error.message))
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
      
      const status = error.response?.status
      const rawData = error.response?.data

      // 1) Intentar construir mensaje desde errores de validación JSON
      if (rawData && typeof rawData === 'object' && !Array.isArray(rawData)) {
        const fieldMessages = []
        Object.keys(rawData).forEach((k) => {
          const val = rawData[k]
          if (Array.isArray(val)) {
            fieldMessages.push(`${k}: ${val.join(' ')}`)
          } else if (typeof val === 'string') {
            fieldMessages.push(`${k}: ${val}`)
          }
        })
        if (fieldMessages.length > 0) {
          showError('Error al eliminar empleado: ' + fieldMessages.join(' | '))
          throw error
        }
      }

      // 2) Fallback genérico
      showError('Error al eliminar empleado: ' + (error.response?.statusText || error.message))
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
