import api from './api'

export const areaService = {
  async getAll() {
    const response = await api.get('/areas/')
    // Extraer el array de results si viene paginado
    return response.data.results || response.data
  },
  
  async getById(id) {
    const response = await api.get(`/areas/${id}/`)
    return response.data
  },
  
  async create(areaData) {
    const response = await api.post('/areas/', areaData)
    return response.data
  },
  
  async update(id, areaData) {
    const response = await api.put(`/areas/${id}/`, areaData)
    return response.data
  },
  
  async delete(id) {
    const response = await api.delete(`/areas/${id}/`)
    return response.data
  }
}
