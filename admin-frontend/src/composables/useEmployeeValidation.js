import { computed, ref } from 'vue'

export function useEmployeeValidation(employees, editingEmployee) {
  // Cache para cédulas existentes - solo se recalcula cuando es necesario
  const cedulasCache = ref(new Set())
  const lastEmployeesLength = ref(0)
  const lastEditingEmployeeId = ref(null)
  
  // Función optimizada para obtener cédulas existentes
  const getExistingCedulas = () => {
    // Solo recalcular si cambió la lista de empleados o el empleado en edición
    if (!employees || !employees.value || !Array.isArray(employees.value)) {
      cedulasCache.value.clear()
      return []
    }
    
    const currentLength = employees.value.length
    const currentEditingId = editingEmployee?.value?.id
    
    // Si no cambió nada, usar cache
    if (currentLength === lastEmployeesLength.value && 
        currentEditingId === lastEditingEmployeeId.value) {
      return Array.from(cedulasCache.value)
    }
    
    // Recalcular cache
    const cedulas = employees.value
      .filter(emp => emp && emp.id && emp.id !== currentEditingId)
      .map(emp => emp.cedula_display || emp.cedula || emp.user?.cedula)
      .filter(Boolean)
    
    // Actualizar cache
    cedulasCache.value = new Set(cedulas)
    lastEmployeesLength.value = currentLength
    lastEditingEmployeeId.value = currentEditingId
    
    return cedulas
  }
  
  // Validar cédula ecuatoriana - optimizada
  const validateEcuadorianCedula = (cedula) => {
    if (!cedula || typeof cedula !== 'string' || cedula.length !== 10) return false
    if (!/^\d+$/.test(cedula)) return false
    
    // Algoritmo optimizado
    let suma = 0
    for (let i = 0; i < 9; i++) {
      const producto = parseInt(cedula[i]) * (i % 2 === 0 ? 2 : 1)
      suma += producto >= 10 ? Math.floor(producto / 10) + (producto % 10) : producto
    }
    
    const digitoVerificador = parseInt(cedula[9])
    const modulo = suma % 10
    const digitoCalculado = modulo === 0 ? 0 : 10 - modulo
    
    return digitoVerificador === digitoCalculado
  }
  
  // Filtros optimizados - solo se ejecutan cuando es necesario
  const filterLettersOnly = (event) => {
    const input = event.target
    const newValue = input.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '')
    if (newValue !== input.value) {
      input.value = newValue
    }
  }
  
  const filterEmail = (event) => {
    const input = event.target
    const newValue = input.value.replace(/[^a-zA-Z0-9@._-]/g, '')
    if (newValue !== input.value) {
      input.value = newValue
    }
  }
  
  const filterNumbersOnly = (event) => {
    const input = event.target
    const newValue = input.value.replace(/[^0-9]/g, '')
    if (newValue !== input.value) {
      input.value = newValue
    }
  }
  
  // Event handlers optimizados
  const blockInvalidCharacters = (event) => {
    const char = String.fromCharCode(event.keyCode || event.charCode)
    if (!/[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/.test(char)) {
      event.preventDefault()
    }
  }
  
  const blockNonNumericCharacters = (event) => {
    const char = String.fromCharCode(event.keyCode || event.charCode)
    if (!/[0-9]/.test(char)) {
      event.preventDefault()
    }
  }
  
  const blockInvalidEmailCharacters = (event) => {
    const char = String.fromCharCode(event.keyCode || event.charCode)
    if (!/[a-zA-Z0-9@._-]/.test(char)) {
      event.preventDefault()
    }
  }
  
  const blockCedulaPaste = (event) => {
    event.preventDefault()
    const pastedText = (event.clipboardData || window.clipboardData).getData('text')
    const cleanText = pastedText.replace(/[^0-9]/g, '')
    event.target.value = cleanText
  }
  
  // Reglas de validación optimizadas - memoizadas
  const createValidationRule = (validator) => {
    const cache = new Map()
    return (value) => {
      // Cache simple para evitar re-validaciones
      const cacheKey = String(value)
      if (cache.has(cacheKey)) {
        return cache.get(cacheKey)
      }
      
      const result = validator(value)
      cache.set(cacheKey, result)
      
      // Limpiar cache si es muy grande
      if (cache.size > 100) {
        const firstKey = cache.keys().next().value
        cache.delete(firstKey)
      }
      
      return result
    }
  }
  
  const rules = {
    required: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'Este campo es requerido'
      }
      return true
    }),
    
    firstName: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'El nombre es requerido'
      }
      const strValue = String(value)
      if (strValue.length < 2) return 'El nombre debe tener al menos 2 caracteres'
      if (strValue.length > 50) return 'El nombre no puede exceder 50 caracteres'
      if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(strValue)) {
        return 'El nombre solo puede contener letras y espacios'
      }
      return true
    }),
    
    lastName: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'El apellido es requerido'
      }
      const strValue = String(value)
      if (strValue.length < 2) return 'El apellido debe tener al menos 2 caracteres'
      if (strValue.length > 50) return 'El apellido no puede exceder 50 caracteres'
      if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(strValue)) {
        return 'El apellido solo puede contener letras y espacios'
      }
      return true
    }),
    
    email: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'El email es requerido'
      }
      const strValue = String(value)
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(strValue)) return 'Formato de email inválido'
      return true
    }),
    
    cedula: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'La cédula es requerida'
      }
      const strValue = String(value)
      if (strValue.length !== 10) return 'La cédula debe tener 10 dígitos'
      if (!/^\d+$/.test(strValue)) return 'La cédula solo puede contener números'
      if (!validateEcuadorianCedula(strValue)) return 'Cédula inválida'
      
      // Verificar duplicados solo cuando sea necesario
      const existingCedulas = getExistingCedulas()
      if (existingCedulas.includes(strValue)) {
        return 'Esta cédula ya está registrada'
      }
      
      return true
    }),
    
    position: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'La posición es requerida'
      }
      return true
    }),
    
    area: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'El área es requerida'
      }
      return true
    }),
    
    hireDate: createValidationRule((value) => {
      if (value === null || value === undefined || value === '') {
        return 'La fecha de contratación es requerida'
      }
      const strValue = String(value)
      const date = new Date(strValue)
      if (isNaN(date.getTime())) return 'Fecha inválida'
      const today = new Date()
      if (date > today) return 'La fecha no puede ser futura'
      return true
    })
  }
  
  return {
    getExistingCedulas,
    validateEcuadorianCedula,
    filterLettersOnly,
    filterEmail,
    filterNumbersOnly,
    blockInvalidCharacters,
    blockNonNumericCharacters,
    blockInvalidEmailCharacters,
    blockCedulaPaste,
    rules
  }
}
