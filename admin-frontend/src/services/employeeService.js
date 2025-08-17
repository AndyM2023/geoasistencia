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
    const response = await api.post('/employees/', employeeData)
    return response.data
  },
  
  async update(id, employeeData) {
    console.log('🔍 employeeService.update() - Datos a enviar:')
    console.log('   - ID:', id)
    console.log('   - employeeData:', JSON.stringify(employeeData, null, 2))
    
    const response = await api.put(`/employees/${id}/`, employeeData)
    return response.data
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
