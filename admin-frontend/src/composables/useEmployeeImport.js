import { ref, computed } from 'vue'
import { employeeService } from '../services/employeeService'
import { useNotifications } from './useNotifications'

export function useEmployeeImport() {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications()
  
  // Estado reactivo
  const selectedFile = ref(null)
  const fileError = ref('')
  const filePreview = ref([])
  const fileHeaders = ref([])
  const importing = ref(false)
  const importProgress = ref(0)
  const currentEmployeeIndex = ref(0)
  const totalEmployees = ref(0)
  const currentEmployeeName = ref('')
  const showProgress = ref(false)
  const skipDuplicates = ref(true)
  const sendWelcomeEmail = ref(true)
  
  // Computed properties
  const fileValid = computed(() => {
    return selectedFile.value && filePreview.value.length > 0 && fileHeaders.value.length > 0
  })
  
  // Métodos
  const onFileSelected = async (file) => {
    if (!file) {
      resetImport()
      return
    }
    
    try {
      fileError.value = ''
      
      // Validar tipo de archivo
      if (!file.name.toLowerCase().endsWith('.csv')) {
        fileError.value = 'Solo se permiten archivos CSV'
        return
      }
      
      // Leer archivo CSV
      const text = await file.text()
      const lines = text.split('\n').filter(line => line.trim())
      
      if (lines.length < 2) {
        fileError.value = 'El archivo debe contener al menos un encabezado y una fila de datos'
        return
      }
      
      // Procesar encabezados
      const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
      const requiredHeaders = ['first_name', 'last_name', 'email', 'cedula', 'position', 'area', 'hire_date']
      
      // Validar encabezados requeridos
      const missingHeaders = requiredHeaders.filter(h => !headers.includes(h))
      if (missingHeaders.length > 0) {
        fileError.value = `Faltan columnas requeridas: ${missingHeaders.join(', ')}`
        return
      }
      
      fileHeaders.value = headers
      
      // Procesar datos
      const data = []
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''))
        const row = {}
        
        headers.forEach((header, index) => {
          row[header] = values[index] || ''
        })
        
        // Validar datos básicos
        if (row.first_name && row.last_name && row.email && row.cedula) {
          data.push(row)
        }
      }
      
      filePreview.value = data
      
      if (data.length === 0) {
        fileError.value = 'No se encontraron datos válidos en el archivo'
        return
      }
      
      showInfo(`Archivo cargado exitosamente. ${data.length} empleados encontrados.`)
      
    } catch (error) {
      console.error('Error al procesar archivo:', error)
      fileError.value = 'Error al procesar el archivo. Verifique que sea un CSV válido.'
    }
  }
  
  const startImport = async () => {
    if (!fileValid.value) {
      showError('Archivo no válido para importar')
      return
    }
    
    try {
      importing.value = true
      showProgress.value = true
      totalEmployees.value = filePreview.value.length
      currentEmployeeIndex.value = 0
      importProgress.value = 0
      
      const results = {
        success: 0,
        errors: 0,
        skipped: 0,
        details: []
      }
      
      for (let i = 0; i < filePreview.value.length; i++) {
        const employee = filePreview.value[i]
        currentEmployeeIndex.value = i + 1
        currentEmployeeName.value = `${employee.first_name} ${employee.last_name}`
        importProgress.value = ((i + 1) / filePreview.value.length) * 100
        
        try {
          // Validar datos del empleado
          const validationError = validateEmployeeData(employee)
          if (validationError) {
            results.errors++
            results.details.push({
              employee: `${employee.first_name} ${employee.last_name}`,
              error: validationError
            })
            continue
          }
          
          // Verificar duplicados si está habilitado
          if (skipDuplicates.value) {
            const isDuplicate = await checkDuplicate(employee.cedula)
            if (isDuplicate) {
              results.skipped++
              results.details.push({
                employee: `${employee.first_name} ${employee.last_name}`,
                error: 'Cédula duplicada'
              })
              continue
            }
          }
          
          // Crear empleado
          const employeeData = {
            user: {
              first_name: employee.first_name,
              last_name: employee.last_name,
              email: employee.email
            },
            cedula: employee.cedula,
            position: employee.position,
            area: employee.area,
            hire_date: employee.hire_date
          }
          
          await employeeService.create(employeeData)
          results.success++
          
          // Enviar email de bienvenida si está habilitado
          if (sendWelcomeEmail.value) {
            // TODO: Implementar envío de email de bienvenida
            console.log('📧 Email de bienvenida para:', employee.email)
          }
          
        } catch (error) {
          results.errors++
          results.details.push({
            employee: `${employee.first_name} ${employee.last_name}`,
            error: error.message || 'Error desconocido'
          })
        }
        
        // Pequeña pausa para no sobrecargar el servidor
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      // Mostrar resultados
      showImportResults(results)
      
    } catch (error) {
      console.error('Error durante la importación:', error)
      showError('Error durante la importación: ' + error.message)
    } finally {
      importing.value = false
      showProgress.value = false
    }
  }
  
  const validateEmployeeData = (employee) => {
    // Validar nombre
    if (!employee.first_name || employee.first_name.length < 2) {
      return 'Nombre debe tener al menos 2 caracteres'
    }
    
    if (!employee.last_name || employee.last_name.length < 2) {
      return 'Apellido debe tener al menos 2 caracteres'
    }
    
    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(employee.email)) {
      return 'Email no válido'
    }
    
    // Validar cédula
    if (!employee.cedula || employee.cedula.length < 10) {
      return 'Cédula debe tener al menos 10 dígitos'
    }
    
    // Validar cargo
    const validPositions = [
      'desarrollador', 'disenador', 'secretario', 'gerente', 'analista',
      'ingeniero', 'contador', 'recursos_humanos', 'marketing', 'ventas',
      'soporte', 'administrativo', 'operativo', 'otro'
    ]
    
    if (!validPositions.includes(employee.position)) {
      return 'Cargo no válido'
    }
    
    // Validar área
    if (!employee.area) {
      return 'Área es requerida'
    }
    
    // Validar fecha de contratación
    if (!employee.hire_date) {
      return 'Fecha de contratación es requerida'
    }
    
    const hireDate = new Date(employee.hire_date)
    if (isNaN(hireDate.getTime())) {
      return 'Fecha de contratación no válida'
    }
    
    return null
  }
  
  const checkDuplicate = async (cedula) => {
    try {
      // TODO: Implementar verificación de duplicados en el backend
      // Por ahora, retornamos false (no duplicado)
      return false
    } catch (error) {
      console.error('Error al verificar duplicados:', error)
      return false
    }
  }
  
  const showImportResults = (results) => {
    const message = `Importación completada:\n` +
      `✅ ${results.success} empleados importados\n` +
      `⚠️ ${results.skipped} empleados omitidos\n` +
      `❌ ${results.errors} errores`
    
    if (results.success > 0) {
      showSuccess(message)
    } else if (results.errors > 0) {
      showError(message)
    } else {
      showWarning(message)
    }
    
    // Mostrar detalles de errores si los hay
    if (results.errors > 0 || results.skipped > 0) {
      console.log('📋 Detalles de la importación:', results.details)
    }
  }
  
  const resetImport = () => {
    selectedFile.value = null
    fileError.value = ''
    filePreview.value = []
    fileHeaders.value = []
    importing.value = false
    importProgress.value = 0
    currentEmployeeIndex.value = 0
    totalEmployees.value = 0
    currentEmployeeName.value = ''
    showProgress.value = false
    skipDuplicates.value = true
    sendWelcomeEmail.value = true
  }
  
  return {
    // Estado
    selectedFile,
    fileError,
    filePreview,
    fileHeaders,
    fileValid,
    importing,
    importProgress,
    currentEmployeeIndex,
    totalEmployees,
    currentEmployeeName,
    showProgress,
    skipDuplicates,
    sendWelcomeEmail,
    
    // Métodos
    onFileSelected,
    startImport,
    resetImport
  }
}
