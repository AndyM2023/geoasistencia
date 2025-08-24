import { ref, nextTick } from 'vue'

export default function useFormValidation() {
  // Estado para errores del formulario
  const formErrors = ref({
    name: '',
    description: '',
    latitude: '',
    longitude: '',
    radius: '',
    grace_period: ''
  })
  
  // Estado para el hint de descripción
  const showDescriptionHint = ref(false)
  const descriptionHint = ref('Solo se permiten letras y números')
  
  // Estado para el hint del nombre
  const showNameHint = ref(false)
  const nameHint = ref('Se permiten letras, números, espacios, guiones (-) y guiones bajos (_)')
  
  // Funciones de validación del formulario
  const validateField = (fieldName, areaForm, scheduleType, schedule) => {
    const value = areaForm[fieldName]
    let error = ''
    
    switch (fieldName) {
      case 'name':
        if (!value) {
          error = 'Nombre es requerido'
        } else if (value.length < 3) {
          error = 'El nombre debe tener al menos 3 caracteres'
        } else if (value.length > 100) {
          error = 'El nombre no puede exceder 100 caracteres'
        } else if (!/^[a-zA-Z0-9\s_-]+$/.test(value)) {
          error = 'Se permiten letras, números, espacios, guiones (-) y guiones bajos (_)'
        }
        break
        
      case 'description':
        if (!value) {
          error = 'Descripción es requerida'
        } else if (value.length < 3) {
          error = 'La descripción debe tener al menos 3 caracteres'
        } else if (value.length > 500) {
          error = 'La descripción no puede exceder 500 caracteres'
        } else if (!/^[a-zA-Z0-9\s]+$/.test(value)) {
          error = 'Solo se permiten letras y números'
        }
        break
        
      case 'latitude':
        if (!value) {
          error = 'Selecciona ubicación en el mapa'
        }
        break
        
      case 'longitude':
        if (!value) {
          error = 'Selecciona ubicación en el mapa'
        }
        break
        
      case 'radius':
        if (!value || value < 10) {
          error = 'Radio mínimo: 10 metros'
        }
        break
        
      case 'grace_period':
        if (scheduleType !== 'none') {
          const gracePeriod = schedule.grace_period_minutes
          if (!gracePeriod && gracePeriod !== 0) {
            error = 'Tolerancia requerida'
          } else if (gracePeriod < 0) {
            error = 'Mínimo 0 minutos'
          } else if (gracePeriod > 120) {
            error = 'Máximo 120 minutos'
          }
        }
        break
    }
    
    formErrors.value[fieldName] = error
    return !error
  }
  
  const validateScheduleField = (fieldName, schedule) => {
    const [day, type] = fieldName.split('_')
    const startTime = schedule[`${day}_start`]
    const endTime = schedule[`${day}_end`]
    
    if (schedule[`${day}_active`]) {
      if (type === 'start' && startTime && endTime && startTime >= endTime) {
        return false
      }
      if (type === 'end' && startTime && endTime && startTime >= endTime) {
        return false
      }
    }
    
    return true
  }
  
  const getScheduleFieldError = (fieldName, schedule) => {
    const [day, type] = fieldName.split('_')
    const startTime = schedule[`${day}_start`]
    const endTime = schedule[`${day}_end`]
    
    if (schedule[`${day}_active`]) {
      if (startTime && endTime && startTime >= endTime) {
        return 'La hora de entrada debe ser anterior a la de salida'
      }
    }
    
    return ''
  }
  
  const validateAllFields = (areaForm, scheduleType, schedule, scheduleDays) => {
    const fields = ['name', 'description', 'latitude', 'longitude', 'radius']
    let isValid = true
    
    // Validar campos básicos
    fields.forEach(field => {
      if (!validateField(field, areaForm, scheduleType, schedule)) {
        isValid = false
      }
    })
    
    // Validar horarios si es necesario
    if (scheduleType !== 'none') {
      if (!validateField('grace_period', areaForm, scheduleType, schedule)) {
        isValid = false
      }
      
      // Validar que al menos un día esté activo
      const activeDays = scheduleDays.filter(day => schedule[`${day.key}_active`])
      if (activeDays.length === 0) {
        isValid = false
      }
      
      // Validar horarios de días activos
      activeDays.forEach(day => {
        const startTime = schedule[`${day.key}_start`]
        const endTime = schedule[`${day.key}_end`]
        
        if (!startTime || !endTime) {
          isValid = false
        } else if (startTime >= endTime) {
          isValid = false
        }
      })
    }
    
    return isValid
  }
  
  const validateScheduleDay = (dayKey, schedule, scheduleDays) => {
    // Validar que si se activa un día, tenga horarios válidos
    if (schedule[`${dayKey}_active`]) {
      const startTime = schedule[`${dayKey}_start`]
      const endTime = schedule[`${dayKey}_end`]
      
      if (!startTime || !endTime) {
        return `⚠️ El día ${scheduleDays.find(d => d.key === dayKey)?.label} está activo pero no tiene horarios configurados`
      }
    }
    return ''
  }
  
  // Función para sanitizar el nombre del área (solo caracteres permitidos)
  const sanitizeName = (event, areaForm) => {
    const input = event.target
    const value = input.value
    
    // Mostrar el hint cuando el usuario empiece a escribir
    if (!showNameHint.value && value.length > 0) {
      showNameHint.value = true
    }
    
    // Remover caracteres no permitidos (letras, números, espacios, guiones y guiones bajos)
    const sanitized = value.replace(/[^a-zA-Z0-9\s_-]/g, '')
    
    // Si el valor cambió, actualizar el campo
    if (sanitized !== value) {
      areaForm.name = sanitized
      // Mover el cursor al final del texto
      nextTick(() => {
        input.setSelectionRange(sanitized.length, sanitized.length)
      })
    }
  }
  
  // Función para sanitizar la descripción (solo letras y números)
  const sanitizeDescription = (event, areaForm) => {
    const input = event.target
    const value = input.value
    
    // Mostrar el hint cuando el usuario empiece a escribir
    if (!showDescriptionHint.value && value.length > 0) {
      showDescriptionHint.value = true
    }
    
    // Remover caracteres no permitidos (solo letras, números y espacios)
    const sanitized = value.replace(/[^a-zA-Z0-9\s]/g, '')
    
    // Si el valor cambió, actualizar el campo
    if (sanitized !== value) {
      areaForm.description = sanitized
      // Mover el cursor al final del texto
      nextTick(() => {
        input.setSelectionRange(sanitized.length, sanitized.length)
      })
    }
  }
  
  const clearFormErrors = () => {
    Object.keys(formErrors.value).forEach(key => {
      formErrors.value[key] = ''
    })
  }
  
  const resetHints = () => {
    showDescriptionHint.value = false
    showNameHint.value = false
  }
  
  return {
    formErrors,
    showDescriptionHint,
    descriptionHint,
    showNameHint,
    nameHint,
    validateField,
    validateScheduleField,
    validateAllFields,
    validateScheduleDay,
    getScheduleFieldError,
    sanitizeName,
    sanitizeDescription,
    clearFormErrors,
    resetHints
  }
}
