import api from './api'

export const attendanceService = {
  async getAll() {
    const response = await api.get('/attendance/')
    // Extraer el array de results si viene paginado
    return response.data.results || response.data
  },
  
  async getByEmployee(employeeId) {
    const response = await api.get(`/attendance/?employee=${employeeId}`)
    return response.data.results || response.data
  },
  
  async getByDateRange(startDate, endDate) {
    const response = await api.get(`/attendance/?start_date=${startDate}&end_date=${endDate}`)
    return response.data.results || response.data
  },
  
  async create(attendanceData) {
    const response = await api.post('/attendance/', attendanceData)
    return response.data
  },
  
  async update(id, attendanceData) {
    const response = await api.put(`/attendance/${id}/`, attendanceData)
    return response.data
  }
}
