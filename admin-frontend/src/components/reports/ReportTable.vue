<template>
  <v-card v-if="reportData.length > 0" class="mt-2">
    <v-card-title>
      <div class="d-flex align-center">
        <span>Reporte de Asistencia</span>
        <v-chip 
          v-if="search.trim()" 
          :color="filteredReportData.length > 0 ? 'success' : 'warning'"
          size="small" 
          class="ml-3"
        >
          <v-icon size="small" class="mr-1">
            {{ filteredReportData.length > 0 ? 'mdi-check' : 'mdi-alert' }}
          </v-icon>
          {{ filteredReportData.length }} de {{ reportData.length }} resultados
        </v-chip>
        
        <!-- Indicador de búsqueda activa -->
        <v-chip 
          v-if="search.trim()" 
          color="info" 
          size="small" 
          class="ml-2"
        >
          <v-icon size="small" class="mr-1">mdi-magnify</v-icon>
          Búsqueda activa
        </v-chip>
        
        <!-- Debug info -->
        <v-chip 
          v-if="search.trim()" 
          color="warning" 
          size="small" 
          class="ml-2"
        >
          <v-icon size="small" class="mr-1">mdi-information</v-icon>
          Key: {{ tableKey }}
        </v-chip>
      </div>
    </v-card-title>

    <v-data-table
      :key="`table-${tableKey}-${search.trim()}-${filteredReportData.length}`"
      :headers="headers"
      :items="filteredReportData"
      :loading="loading"
      class="elevation-1"
    >
      <template v-slot:item.date="{ item }">
        {{ formatDate(item.date) }}
      </template>
      
      <template v-slot:item.check_in="{ item }">
        <span v-if="item.check_in">{{ formatTime(item.check_in) }}</span>
        <span v-else class="text-grey">--</span>
      </template>
      
      <template v-slot:item.check_out="{ item }">
        <span v-if="item.check_out">{{ formatTime(item.check_out) }}</span>
        <span v-else class="text-grey">--</span>
      </template>
      
      <template v-slot:item.status="{ item }">
        <v-chip :color="getStatusColor(item.status)" size="small">
          {{ getStatusText(item.status) }}
        </v-chip>
      </template>
      
      <template v-slot:item.hours_worked="{ item }">
        {{ item.hours_worked || '--' }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
export default {
  name: 'ReportTable',
  props: {
    reportData: {
      type: Array,
      required: true,
      default: () => []
    },
    filteredReportData: {
      type: Array,
      required: true,
      default: () => []
    },
    search: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    },
    tableKey: {
      type: Number,
      default: 0
    },
    headers: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup() {
    const formatDate = (dateString) => {
      if (!dateString) return '';
      
      try {
        if (typeof dateString === 'string' && dateString.includes('-')) {
          const [year, month, day] = dateString.split('-');
          return `${day}/${month}/${year}`;
        }
        
        if (dateString instanceof Date) {
          const day = String(dateString.getDate()).padStart(2, '0');
          const month = String(dateString.getMonth() + 1).padStart(2, '0');
          const year = dateString.getFullYear();
          return `${day}/${month}/${year}`;
        }
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
          console.warn('⚠️ Fecha inválida:', dateString);
          return dateString;
        }
        
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          timeZone: 'America/Guayaquil'
        });
        
      } catch (error) {
        console.error('❌ Error formateando fecha:', error, dateString);
        return dateString;
      }
    };
    
    const formatTime = (timeString) => {
      return timeString.substring(0, 5);
    };
    
    const getStatusColor = (status) => {
      const colors = {
        present: 'success',
        late: 'warning',
        absent: 'error'
      };
      return colors[status] || 'grey';
    };
    
    const getStatusText = (status) => {
      const texts = {
        present: 'Presente',
        late: 'Tarde',
        absent: 'Ausente'
      };
      return texts[status] || status;
    };

    return {
      formatDate,
      formatTime,
      getStatusColor,
      getStatusText
    };
  }
}
</script>
