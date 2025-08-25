<template>
  <v-card class="bg-dark-surface border border-blue-500/20 mb-6">
    <v-card-title class="text-white d-flex align-center">
      <v-icon color="blue-400" class="mr-2">mdi-magnify</v-icon>
      🔍 Búsqueda de Empleados
    </v-card-title>
    
    <v-card-text>
      <v-row>
        <!-- Búsqueda por texto -->
        <v-col cols="12" md="8">
          <v-text-field
            :model-value="searchQuery"
            label="Buscar empleados"
            placeholder="Nombre, apellido, cédula o email..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            color="blue-400"
            bg-color="dark-surface"
            clearable
            @update:model-value="$emit('update:searchQuery', $event)"
          ></v-text-field>
        </v-col>
        
        <!-- Botón limpiar -->
        <v-col cols="12" md="4" class="d-flex align-center">
          <v-btn
            color="blue-400"
            variant="outlined"
            @click="clearSearch"
            prepend-icon="mdi-refresh"
            size="large"
            block
          >
            Limpiar
          </v-btn>
        </v-col>
      </v-row>
      
      <!-- Filtros activos -->
      <div v-if="searchQuery" class="mt-4">
        <v-divider class="mb-3"></v-divider>
        <div class="d-flex align-center">
          <span class="text-grey-400 mr-3">Búsqueda activa:</span>
          <div class="d-flex flex-wrap gap-2">
            <v-chip
              color="blue-400"
              variant="tonal"
              closable
              @click:close="clearSearch"
            >
              🔍 "{{ searchQuery }}"
            </v-chip>
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'EmployeeFilters',
  props: {
    searchQuery: {
      type: String,
      default: ''
    }
  },
  emits: ['update:searchQuery'],
  setup(props, { emit }) {
    // Métodos
    const clearSearch = () => {
      emit('update:searchQuery', '')
    }
    
    return {
      clearSearch
    }
  }
}
</script>

<style scoped>
.v-chip {
  cursor: pointer;
}

.v-chip:hover {
  transform: scale(1.05);
  transition: transform 0.2s ease;
}
</style>
