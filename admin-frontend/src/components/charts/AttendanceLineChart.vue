<template>
  <div>
    <Line
      :data="chartData"
      :options="chartOptions"
      :height="300"
    />
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export default {
  name: 'AttendanceLineChart',
  components: { Line },
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    chartData() {
      return {
        labels: this.data.map(item => item.date),
        datasets: [
          {
            label: 'Asistencias',
            data: this.data.map(item => item.count),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#3B82F6',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6
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
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: '#3B82F6',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: false
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
        },
        elements: {
          point: {
            hoverRadius: 8
          }
        }
      }
    }
  }
}
</script>

