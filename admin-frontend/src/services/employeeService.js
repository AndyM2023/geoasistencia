import api from './api'

export const employeeService = {
  async getAll() {
    // Recolectar todas las páginas (el backend fija PAGE_SIZE=20)
    const items = []
    let url = '/employees/?page_size=100'
    while (url) {
      const response = await api.get(url)
      const data = response.data
      if (Array.isArray(data)) {
        // Sin paginación
        return data
      }
      items.push(...(data.results || []))
      // Usar 'next' absoluto o relativo
      url = data.next ? data.next.replace(response.config.baseURL, '') : null
    }
    return items
  },
  
  async getAllWithStatus(status = 'active') {
    const items = []
    const params = new URLSearchParams()
    if (status !== 'active') params.set('status', status)
    params.set('page_size', '100')
    let url = `/employees/?${params.toString()}`
    while (url) {
      const response = await api.get(url)
      const data = response.data
      if (Array.isArray(data)) {
        return data
      }
      items.push(...(data.results || []))
      url = data.next ? data.next.replace(response.config.baseURL, '') : null
    }
    return items
  },
  
  async getById(id) {
    const response = await api.get(`/employees/${id}/`)
    return response.data
  },
  
  async create(employeeData) {
    // Si hay foto (File o Blob de cámara), enviar como FormData
    if (employeeData.photo && (employeeData.photo instanceof File || employeeData.photo instanceof Blob)) {
      console.log('📸 Foto detectada en creación, enviando como FormData')
      const formData = new FormData()

      // Agregar todos los campos del formulario
      Object.keys(employeeData).forEach(key => {
        if (key === 'photo') {
          // Si es Blob (captura de cámara), agregar un nombre de archivo por compatibilidad
          const isBlob = employeeData.photo instanceof Blob && !(employeeData.photo instanceof File)
          const filename = isBlob ? 'photo.jpg' : employeeData.photo.name
          formData.append('photo', employeeData.photo, filename)
        } else if (employeeData[key] !== null && employeeData[key] !== undefined) {
          formData.append(key, employeeData[key])
        }
      })

      console.log('📤 FormData creado para creación (sin forzar Content-Type):', formData)
      // No forzar Content-Type; el navegador agregará el boundary correcto
      const response = await api.post('/employees/', formData)
      return response.data
    } else {
      // Sin foto válida, enviar como JSON normal removiendo el campo photo si existe
      const cleanData = { ...employeeData }
      if ('photo' in cleanData) {
        delete cleanData.photo
      }
      const response = await api.post('/employees/', cleanData)
      return response.data
    }
  },
  
  async update(id, employeeData) {
    console.log('🔍 employeeService.update() - Datos a enviar:')
    console.log('   - ID:', id)
    console.log('   - employeeData:', JSON.stringify(employeeData, null, 2))
    
    // Log detallado de cada campo
    console.log('🔍 Detalle de campos:')
    Object.keys(employeeData).forEach(key => {
      const value = employeeData[key]
      console.log(`   - ${key}: ${value} (tipo: ${typeof value}, null: ${value === null}, undefined: ${value === undefined})`)
    })
    
    // Si hay foto nueva (File o Blob), enviar como FormData
    if (employeeData.photo && (employeeData.photo instanceof File || employeeData.photo instanceof Blob)) {
      console.log('📸 Foto nueva detectada, enviando como FormData')
      const formData = new FormData()

      // Agregar todos los campos del formulario
      Object.keys(employeeData).forEach(key => {
        if (key === 'photo') {
          const isBlob = employeeData.photo instanceof Blob && !(employeeData.photo instanceof File)
          const filename = isBlob ? 'photo.jpg' : employeeData.photo.name
          formData.append('photo', employeeData.photo, filename)
        } else if (employeeData[key] !== null && employeeData[key] !== undefined) {
          formData.append(key, employeeData[key])
        }
      })

      console.log('📤 FormData creado (sin forzar Content-Type):', formData)
      const response = await api.put(`/employees/${id}/`, formData)
      return response.data
    } else if (employeeData.photo === 'DELETE_PHOTO') {
      // Si se marca para eliminar la foto, enviar señal especial
      console.log('🗑️ Foto marcada para eliminación, enviando señal')
      const cleanData = { ...employeeData }
      delete cleanData.photo // Remover el marcador especial
      
      // Agregar campo especial para indicar eliminación de foto
      cleanData.delete_photo = true
      
      console.log('📤 Datos para eliminación de foto:', JSON.stringify(cleanData, null, 2))
      const response = await api.put(`/employees/${id}/`, cleanData)
      return response.data
    } else {
      // Sin foto, enviar como JSON normal
      console.log('📤 Enviando como JSON normal')
      
      // Limpiar campos null/undefined antes de enviar
      const cleanData = {}
      Object.keys(employeeData).forEach(key => {
        if (employeeData[key] !== null && employeeData[key] !== undefined) {
          cleanData[key] = employeeData[key]
        }
      })
      
      // Validar que el position sea válido
      if (cleanData.position) {
        const validPositions = [
          'desarrollador', 'disenador', 'secretario', 'gerente', 'analista',
          'ingeniero', 'contador', 'recursos_humanos', 'marketing', 'ventas',
          'soporte', 'administrativo', 'operativo', 'otro'
        ]
        
        if (!validPositions.includes(cleanData.position)) {
          console.error(`❌ Position inválido: "${cleanData.position}". Valores válidos:`, validPositions)
          throw new Error(`Cargo inválido: "${cleanData.position}". Debe seleccionar una opción válida.`)
        }
      }
      
      console.log('📤 Datos limpios a enviar:', JSON.stringify(cleanData, null, 2))
      const response = await api.put(`/employees/${id}/`, cleanData)
      return response.data
    }
  },
  
  async delete(id) {
    const response = await api.delete(`/employees/${id}/`)
    // HTTP_204_NO_CONTENT no tiene data, retornar mensaje de éxito
    if (response.status === 204) {
      return { message: 'Empleado desactivado correctamente' }
    }
    return response.data
  },
  
  async activate(id) {
    const response = await api.post(`/employees/${id}/activate/`)
    return response.data
  }
}
