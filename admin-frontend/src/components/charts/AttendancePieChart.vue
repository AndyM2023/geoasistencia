<template>
  <div>
    <Doughnut
      :data="chartData"
      :options="chartOptions"
      :height="300"
    />
  </div>
</template>

<script>
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
)

export default {
  name: 'AttendancePieChart',
  components: { Doughnut },
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    chartData() {
      // Calcular totales de cada estado
      let totalPresent = 0
      let totalLate = 0
      let totalAbsent = 0
      
      this.data.forEach(item => {
        totalPresent += item.present || 0
        totalLate += item.late || 0
        totalAbsent += item.absent || 0
      })
      
      return {
        labels: ['Presentes', 'Atrasos', 'Ausencias'],
        datasets: [
          {
            label: 'Estados de Asistencia',
            data: [totalPresent, totalLate, totalAbsent],
            backgroundColor: [
              '#4CAF50',  // Verde para presentes
              '#FF9800',  // Naranja para tardanzas
              '#F44336'   // Rojo para ausencias
            ],
            borderColor: [
              '#388E3C',
              '#F57F17',
              '#D32F2F'
            ],
            borderWidth: 2
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
            position: 'bottom',
            labels: {
              color: '#FFFFFF',
              font: {
                size: 12
              },
              padding: 20
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#FFFFFF',
            bodyColor: '#FFFFFF',
            callbacks: {
              label: function(context) {
                const dataset = context.dataset
                const total = dataset.data.reduce((sum, value) => sum + value, 0)
                const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0
                return `${context.label}: ${context.parsed} (${percentage}%)`
              }
            }
          }
        }
      }
    }
  }
}
</script>