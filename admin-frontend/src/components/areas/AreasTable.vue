<template>
  <v-card class="bg-dark-surface border border-blue-500/20 areas-table-card">
    <v-card-title class="text-white d-flex align-center">
      <!-- Input de búsqueda -->
      <v-text-field
        v-model="search"
        label="Buscar área"
        placeholder="Buscar área"
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        color="blue-400"
        bg-color="dark-surface"
        clearable
        class="search-input"
      ></v-text-field>
    </v-card-title>

    <v-data-table
      :key="tableKey"
      :headers="headers"
      :items="areas"
      :search="search"
      :loading="loading"
      :sort-by="[{ key: 'name', order: 'asc' }]"
      class="areas-data-table"
      theme="dark"
      :no-data-text="loading ? 'Cargando áreas...' : 'No hay áreas registradas'"
      :no-results-text="'No se encontraron áreas que coincidan con la búsqueda'"
    >
      <!-- Nombre -->
      <template v-slot:item.name="{ item }">
        <div class="area-name-cell">
          {{ item.name }}
        </div>
      </template>

      <!-- Descripción -->
      <template v-slot:item.description="{ item }">
        <div class="area-description-cell">
          <span class="area-description-wrap" :title="item.description">{{ item.description }}</span>
        </div>
      </template>

      <!-- Latitud -->
      <template v-slot:item.latitude="{ item }">
        <div class="area-coordinate-cell">
          <span :title="item.latitude">{{ formatCoordinate(item.latitude) }}</span>
        </div>
      </template>

      <!-- Longitud -->
      <template v-slot:item.longitude="{ item }">
        <div class="area-coordinate-cell">
          <span :title="item.longitude">{{ formatCoordinate(item.longitude) }}</span>
        </div>
      </template>

      <!-- Radio -->
      <template v-slot:item.radius="{ item }">
        <div class="area-radius-cell">
          {{ item.radius }}m
        </div>
      </template>

      <!-- Empleados -->
      <template v-slot:item.employee_count="{ item }">
        <div class="area-employee-count-cell">
          <v-chip 
            :color="item.employee_count > 0 ? 'green-500' : 'grey-500'" 
            size="small" 
            variant="tonal"
          >
            {{ item.employee_count || 0 }}
          </v-chip>
        </div>
      </template>

      <!-- Horario -->
      <template v-slot:item.schedule_info="{ item }">
        <div class="area-schedule-cell">
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
        </div>
      </template>

      <!-- Acciones -->
      <template v-slot:item.actions="{ item }">
        <div class="areas-actions-cell">
          <v-btn
            icon="mdi-pencil"
            size="small"
            color="white"
            variant="text"
            @click="$emit('edit', item)"
            class="action-btn"
            title="Editar área"
          ></v-btn>
          
          <!-- Botón dinámico según el estado del área -->
          <v-btn 
            v-if="item.status === 'active'"
            icon="mdi-account-off" 
            size="small" 
            color="white"
            variant="text"
            @click="item.employee_count > 0 ? null : $emit('delete', item)"
            :disabled="item.employee_count > 0"
            :title="item.employee_count > 0 ? 'No se puede desactivar: tiene empleados asignados' : 'Desactivar área'"
            class="action-btn"
          ></v-btn>
          
          <v-btn 
            v-else
            icon="mdi-account-check" 
            size="small" 
            color="white"
            variant="text"
            @click="$emit('activate', item)"
            title="Reactivar área"
            class="action-btn"
          ></v-btn>
        </div>
      </template>

      <!-- Sin datos -->
      <template v-slot:no-data>
        <div class="text-center py-8">
          <v-icon size="64" color="grey-400" class="mb-4">mdi-map-marker-off</v-icon>
          <h3 class="text-grey-500 mb-2">No hay áreas</h3>
          <p class="text-grey-400">Crea la primera área para comenzar</p>
        </div>
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
        {
          title: 'Nombre',
          key: 'name',
          sortable: true,
          width: '20%'
        },
        {
          title: 'Descripción',
          key: 'description',
          sortable: false,
          width: '25%'
        },
        {
          title: 'Latitud',
          key: 'latitude',
          sortable: true,
          width: '12%'
        },
        {
          title: 'Longitud',
          key: 'longitude',
          sortable: true,
          width: '12%'
        },
        {
          title: 'Radio',
          key: 'radius',
          sortable: true,
          width: '8%'
        },
        {
          title: 'Empleados',
          key: 'employee_count',
          sortable: true,
          width: '10%'
        },
        {
          title: 'Horario',
          key: 'schedule_info',
          sortable: false,
          width: '13%'
        },
        {
          title: 'Acciones',
          key: 'actions',
          sortable: false,
          width: '10%',
          align: 'center'
        }
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
