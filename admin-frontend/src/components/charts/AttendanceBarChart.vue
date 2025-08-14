<template>
  <div>
    <Bar
      :data="chartData"
      :options="chartOptions"
      :height="300"
    />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'AttendanceBarChart',
  components: { Bar },
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    chartData() {
      const labels = this.data.map(item => item.date)
      const presentData = this.data.map(item => item.present || 0)
      const lateData = this.data.map(item => item.late || 0)
      const absentData = this.data.map(item => item.absent || 0)
      
      return {
        labels,
        datasets: [
          {
            label: 'Presentes',
            data: presentData,
            backgroundColor: '#10B981',
            borderColor: '#10B981',
            borderWidth: 1,
            borderRadius: 4
          },
          {
            label: 'Llegadas Tarde',
            data: lateData,
            backgroundColor: '#F59E0B',
            borderColor: '#F59E0B',
            borderWidth: 1,
            borderRadius: 4
          },
          {
            label: 'Ausentes',
            data: absentData,
            backgroundColor: '#EF4444',
            borderColor: '#EF4444',
            borderWidth: 1,
            borderRadius: 4
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#9CA3AF',
              usePointStyle: true,
              padding: 20
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: '#3B82F6',
            borderWidth: 1,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
              borderColor: 'rgba(255, 255, 255, 0.2)'
            },
            ticks: {
              color: '#9CA3AF',
              font: {
                size: 12
              }
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
              borderColor: 'rgba(255, 255, 255, 0.2)'
            },
            ticks: {
              color: '#9CA3AF',
              font: {
                size: 12
              },
              stepSize: 1
            },
            beginAtZero: true
          }
        }
      }
    }
  }
}
</script>
