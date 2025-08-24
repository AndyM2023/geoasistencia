<template>
  <v-card class="bg-dark-surface border border-blue-500/20">
    <v-card-title class="text-white">
      <div class="d-flex align-center gap-3">
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar área"
          single-line
          hide-details
          variant="outlined"
          density="compact"
          color="blue-400"
          class="text-white"
        ></v-text-field>
      </div>
    </v-card-title>

    <v-data-table
      :key="tableKey"
      :headers="headers"
      :items="areas"
      :search="search"
      :loading="loading"
      :sort-by="[{ key: 'name', order: 'asc' }]"
      class="elevation-1 bg-dark-surface"
      theme="dark"
      :no-data-text="loading ? 'Cargando áreas...' : 'No hay áreas registradas'"
      :no-results-text="'No se encontraron áreas que coincidan con la búsqueda'"
    >
      <template v-slot:item.radius="{ item }">
        {{ item.radius }}m
      </template>
      
      <template v-slot:item.actions="{ item }">
        <v-btn icon="mdi-pencil" size="small" color="blue-400" @click="$emit('edit', item)" title="Editar área"></v-btn>
        
        <!-- Botón dinámico según el estado del área -->
        <v-btn 
          v-if="item.status === 'active'"
          icon="mdi-account-off" 
          size="small" 
          :color="item.employee_count > 0 ? 'grey-400' : 'red-400'"
          @click="item.employee_count > 0 ? null : $emit('delete', item)"
          :disabled="item.employee_count > 0"
          :title="item.employee_count > 0 ? 'No se puede desactivar: tiene empleados asignados' : 'Desactivar área'"
        ></v-btn>
        
        <v-btn 
          v-else
          icon="mdi-account-check" 
          size="small" 
          color="green-400" 
          @click="$emit('activate', item)"
          title="Reactivar área"
        ></v-btn>
      </template>
      
      <template v-slot:item.latitude="{ item }">
        <span :title="item.latitude">{{ formatCoordinate(item.latitude) }}</span>
      </template>
      
      <template v-slot:item.longitude="{ item }">
        <span :title="item.longitude">{{ formatCoordinate(item.longitude) }}</span>
      </template>
      
      <template v-slot:item.description="{ item }">
        {{ item.description }}
      </template>
      
      <template v-slot:item.employee_count="{ item }">
        <v-chip 
          :color="item.employee_count > 0 ? 'green-500' : 'grey-500'" 
          size="small" 
          variant="tonal"
        >
          {{ item.employee_count || 0 }}
        </v-chip>
      </template>
      
      <template v-slot:item.schedule_info="{ item }">
        <v-chip 
          v-if="item.schedule"
          :color="getScheduleColor(item.schedule)" 
          size="small" 
          variant="tonal"
          :title="getScheduleTooltip(item.schedule)"
        >
          <v-icon left size="small">{{ getScheduleIcon(item.schedule) }}</v-icon>
          {{ getScheduleText(item.schedule) }}
        </v-chip>
        <v-chip 
          v-else
          color="grey-500" 
          size="small" 
          variant="tonal"
          title="Sin horario configurado"
        >
          <v-icon left size="small">mdi-close-circle</v-icon>
          Sin horario
        </v-chip>
      </template>
      
      <template v-slot:item.status="{ item }">
        <v-chip 
          :color="item.status === 'active' ? 'green-500' : 'red-500'" 
          size="small" 
          variant="tonal"
        >
          {{ item.status === 'active' ? 'Activa' : 'Inactiva' }}
        </v-chip>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
export default {
  name: 'AreasTable',
  props: {
    areas: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    tableKey: {
      type: [String, Number],
      default: 0
    }
  },
  emits: ['edit', 'delete', 'activate'],
  data() {
    return {
      search: '',
      headers: [
        { title: 'Nombre', key: 'name', sortable: true },
        { title: 'Descripción', key: 'description', sortable: false },
        { title: 'Latitud', key: 'latitude', sortable: true },
        { title: 'Longitud', key: 'longitude', sortable: true },
        { title: 'Radio', key: 'radius', sortable: true },
        { title: 'Empleados', key: 'employee_count', sortable: true },
        { title: 'Horario', key: 'schedule_info', sortable: false },
        { title: 'Estado', key: 'status', sortable: true },
        { title: 'Acciones', key: 'actions', sortable: false, width: '120px' }
      ]
    }
  },
  methods: {
    formatCoordinate(value) {
      if (!value) return 'N/A'
      return parseFloat(value).toFixed(6)
    },
    getScheduleColor(schedule) {
      if (!schedule) return 'grey'
      if (schedule.schedule_type === 'default') return 'green'
      if (schedule.schedule_type === 'custom') return 'blue'
      return 'grey'
    },
    getScheduleIcon(schedule) {
      if (!schedule) return 'mdi-close-circle'
      if (schedule.schedule_type === 'default') return 'mdi-check-circle'
      if (schedule.schedule_type === 'custom') return 'mdi-cog'
      return 'mdi-close-circle'
    },
    getScheduleText(schedule) {
      if (!schedule) return 'Sin horario'
      if (schedule.schedule_type === 'default') return 'Por defecto'
      if (schedule.schedule_type === 'custom') return 'Personalizado'
      return 'Sin horario'
    },
    getScheduleTooltip(schedule) {
      if (!schedule) return 'Sin horario configurado'
      if (schedule.schedule_type === 'default') return 'Horario por defecto (8:00 AM - 5:00 PM, Lunes a Viernes)'
      if (schedule.schedule_type === 'custom') return 'Horario personalizado configurado'
      return 'Sin horario configurado'
    }
  }
}
</script>

<style scoped>
/* Estilos específicos para la tabla */
.v-data-table {
  background: transparent !important;
}

.v-data-table .v-data-table__wrapper {
  background: transparent !important;
}

.v-data-table .v-data-table__thead {
  background: rgba(15, 23, 42, 0.8) !important;
}

.v-data-table .v-data-table__tbody tr:hover {
  background: rgba(59, 130, 246, 0.1) !important;
}

.v-data-table .v-data-table__tbody tr:nth-child(even) {
  background: rgba(15, 23, 42, 0.3) !important;
}

.v-data-table .v-data-table__tbody tr:nth-child(odd) {
  background: rgba(15, 23, 42, 0.1) !important;
}
</style>
