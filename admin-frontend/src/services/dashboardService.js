import api from './api'

export const dashboardService = {
  async getStats() {
    const response = await api.get('/dashboard/stats/')
    return response.data
  },
  
  async getWeeklyAttendance() {
    const response = await api.get('/dashboard/weekly_attendance/')
    return response.data
  },
  
  async getRecentActivity() {
    const response = await api.get('/dashboard/recent_activity/')
    return response.data
  }
}

