<template>
  <v-card class="mb-6">
    <v-card-title class="d-flex align-center justify-space-between">
      <span>Filtros</span>
      <div class="d-flex align-center">
        <v-select
          v-model="filters.status"
          label="Estado"
          :items="[
            { title: 'Todos', value: 'all' },
            { title: 'Presente', value: 'present' },
            { title: 'Ausente', value: 'absent' },
            { title: 'Tarde', value: 'late' }
          ]"
          item-title="title"
          item-value="value"
          variant="outlined"
          density="compact"
          style="min-width: 150px; max-width: 200px;"
        ></v-select>
      </div>
    </v-card-title>
    
    <v-card-text>
      <v-row>
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="filters.employee"
            label="Empleado"
            :items="[
              { title: 'Todos los empleados', value: null },
              ...employees.map(emp => ({
                title: emp.user.full_name,
                value: emp.id
              }))
            ]"
            item-title="title"
            item-value="value"
            variant="outlined"
            density="compact"
          ></v-select>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="filters.area"
            label="Área"
            :items="[
              { title: 'Todas las áreas', value: null },
              ...areas.map(area => ({
                title: area.name,
                value: area.id
              }))
            ]"
            item-title="title"
            item-value="value"
            variant="outlined"
            density="compact"
            :disabled="filters.employee !== null"
            :prepend-icon="filters.employee ? 'mdi-lock' : 'mdi-map-marker'"
            :color="filters.employee ? 'warning' : 'primary'"
          ></v-select>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-menu v-model="showDatePickerFrom" :close-on-content-click="false">
            <template v-slot:activator="{ props }">
              <v-text-field
                v-model="formattedDateFrom"
                label="Desde"
                readonly
                v-bind="props"
                variant="outlined"
                density="compact"
                prepend-icon="mdi-calendar"
                :hint="filters.dateTo && new Date(filters.dateFrom) > new Date(filters.dateTo) ? 'Fecha debe ser menor que Hasta' : ''"
                :error="filters.dateTo && new Date(filters.dateFrom) > new Date(filters.dateTo)"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="filters.dateFrom"
              @update:model-value="showDatePickerFrom = false"
              :max="filters.dateTo"
              :format="'DD/MM/YYYY'"
            ></v-date-picker>
          </v-menu>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-menu v-model="showDatePickerTo" :close-on-content-click="false">
            <template v-slot:activator="{ props }">
              <v-text-field
                v-model="formattedDateTo"
                label="Hasta"
                readonly
                v-bind="props"
                variant="outlined"
                density="compact"
                prepend-icon="mdi-calendar"
                :hint="filters.dateFrom && new Date(filters.dateFrom) > new Date(filters.dateTo) ? 'Fecha debe ser mayor que Desde' : ''"
                :error="filters.dateFrom && new Date(filters.dateFrom) > new Date(filters.dateTo)"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="filters.dateTo"
              @update:model-value="showDatePickerTo = false"
              :min="filters.dateFrom"
              :format="'DD/MM/YYYY'"
            ></v-date-picker>
          </v-menu>
        </v-col>
      </v-row>
      
      <v-row class="mt-0">
        <v-col cols="12" class="text-center pa-0">
          <v-btn 
            color="primary" 
            @click="$emit('generate-report')" 
            :loading="generating" 
            :disabled="!canGenerateReport" 
            class="ma-1"
          >
            Generar Reporte
          </v-btn>
          
          <v-btn 
            color="secondary" 
            @click="$emit('export-report')" 
            :disabled="!hasReportData" 
            class="ma-1" 
            data-export-btn
          >
            Exportar Excel
          </v-btn>
          
          <v-btn 
            color="outline" 
            @click="clearFilters" 
            class="ma-1"
          >
            Limpiar Filtros
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { computed, watch, ref } from 'vue'

export default {
  name: 'ReportFilters',
  props: {
    filters: {
      type: Object,
      required: true
    },
    employees: {
      type: Array,
      default: () => []
    },
    areas: {
      type: Array,
      default: () => []
    },
    generating: {
      type: Boolean,
      default: false
    },
    hasReportData: {
      type: Boolean,
      default: false
    }
  },
  emits: ['generate-report', 'export-report', 'update:filters'],
  setup(props, { emit }) {
    const showDatePickerFrom = ref(false)
    const showDatePickerTo = ref(false)

    const formattedDateFrom = computed(() => {
      if (!props.filters.dateFrom) return '';
      return new Date(props.filters.dateFrom).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    });

    const formattedDateTo = computed(() => {
      if (!props.filters.dateTo) return '';
      return new Date(props.filters.dateTo).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    });

    const canGenerateReport = computed(() => {
      const hasFilters = props.filters.employee !== undefined || 
                        props.filters.area !== undefined || 
                        props.filters.status !== 'all' ||
                        props.filters.dateFrom || 
                        props.filters.dateTo;
      
      if (props.filters.dateFrom || props.filters.dateTo) {
        if (!props.filters.dateFrom || !props.filters.dateTo) {
          return false;
        }
        
        const fromDate = new Date(props.filters.dateFrom);
        const toDate = new Date(props.filters.dateTo);
        if (fromDate > toDate) {
          return false;
        }
      }
      
      return hasFilters;
    });

    const clearFilters = () => {
      const newFilters = {
        employee: null,
        area: null,
        dateFrom: null,
        dateTo: null,
        status: 'all'
      };
      emit('update:filters', newFilters);
      showDatePickerFrom.value = false;
      showDatePickerTo.value = false;
    };

    // Watcher para establecer automáticamente el área cuando se selecciona un empleado
    watch(() => props.filters.employee, (newEmployeeId) => {
      if (newEmployeeId) {
        const selectedEmployee = props.employees.find(emp => emp.id === newEmployeeId);
        if (selectedEmployee && selectedEmployee.area) {
          const updatedFilters = { ...props.filters, area: selectedEmployee.area };
          emit('update:filters', updatedFilters);
        }
      } else {
        const updatedFilters = { ...props.filters, area: null };
        emit('update:filters', updatedFilters);
      }
    });

    return {
      showDatePickerFrom,
      showDatePickerTo,
      formattedDateFrom,
      formattedDateTo,
      canGenerateReport,
      clearFilters
    }
  }
}
</script>
