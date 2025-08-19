import api from './api'

export const employeeService = {
  async getAll() {
    const response = await api.get('/employees/')
    // Extraer el array de results si viene paginado
    return response.data.results || response.data
  },
  
  async getAllWithStatus(status = 'active') {
    const params = status !== 'active' ? `?status=${status}` : ''
    const response = await api.get(`/employees/${params}`)
    // Extraer el array de results si viene paginado
    return response.data.results || response.data
  },
  
  async getById(id) {
    const response = await api.get(`/employees/${id}/`)
    return response.data
  },
  
  async create(employeeData) {
    // Si hay foto, enviar como FormData
    if (employeeData.photo && employeeData.photo instanceof File) {
      console.log('📸 Foto detectada en creación, enviando como FormData')
      const formData = new FormData()
      
      // Agregar todos los campos del formulario
      Object.keys(employeeData).forEach(key => {
        if (key === 'photo') {
          formData.append('photo', employeeData.photo)
        } else if (employeeData[key] !== null && employeeData[key] !== undefined) {
          formData.append(key, employeeData[key])
        }
      })
      
      console.log('📤 FormData creado para creación:', formData)
      const response = await api.post('/employees/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } else {
      // Sin foto, enviar como JSON normal
      const response = await api.post('/employees/', employeeData)
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
    
    // Si hay foto nueva, enviar como FormData
    if (employeeData.photo && employeeData.photo instanceof File) {
      console.log('📸 Foto nueva detectada, enviando como FormData')
      const formData = new FormData()
      
      // Agregar todos los campos del formulario
      Object.keys(employeeData).forEach(key => {
        if (key === 'photo') {
          formData.append('photo', employeeData.photo)
        } else if (employeeData[key] !== null && employeeData[key] !== undefined) {
          formData.append(key, employeeData[key])
        }
      })
      
      console.log('📤 FormData creado:', formData)
      const response = await api.put(`/employees/${id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
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
