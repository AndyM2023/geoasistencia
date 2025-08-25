<template>
  <v-dialog
    :model-value="showDialog"
    @update:model-value="$emit('update:showDialog', $event)"
    max-width="500px"
    persistent
  >
    <v-card class="bg-dark-surface border border-red-500/20">
      <v-card-title class="text-white d-flex align-center">
        <v-icon color="red-400" class="mr-2">mdi-alert-circle</v-icon>
        ⚠️ Confirmar Eliminación
        <v-spacer></v-spacer>
        <v-btn 
          icon="mdi-close" 
          size="small" 
          color="grey-400" 
          variant="text"
          @click="$emit('update:showDialog', false)"
        ></v-btn>
      </v-card-title>
      
      <v-card-text class="pa-6">
        <div class="text-center">
          <v-avatar size="80" class="mb-4">
            <v-img 
              :src="employee?.photo_url || '/default-avatar.png'" 
              cover
              :alt="`${employee?.user?.first_name} ${employee?.user?.last_name}`"
            ></v-img>
          </v-avatar>
          
          <h3 class="text-white mb-3">
            ¿Estás seguro de que quieres eliminar a este empleado?
          </h3>
          
          <div class="bg-red-500/10 border border-red-500/20 rounded-lg pa-4 mb-4">
            <p class="text-red-400 font-weight-medium mb-2">
              {{ employee?.user?.first_name }} {{ employee?.user?.last_name }}
            </p>
            <p class="text-grey-300 text-sm mb-1">
              <strong>Cédula:</strong> {{ employee?.cedula_display || employee?.cedula }}
            </p>
            <p class="text-grey-300 text-sm mb-1">
              <strong>Posición:</strong> {{ getPositionLabel(employee?.position) }}
            </p>
            <p class="text-grey-300 text-sm">
              <strong>Área:</strong> {{ employee?.area_name || 'Sin asignar' }}
            </p>
          </div>
          
          <v-alert
            type="warning"
            variant="tonal"
            density="compact"
            class="text-left"
          >
            <template v-slot:prepend>
              <v-icon color="orange">mdi-alert</v-icon>
            </template>
            <div>
              <p class="font-weight-medium mb-1">Esta acción no se puede deshacer</p>
              <ul class="text-sm mb-0">
                <li>Se eliminará el empleado del sistema</li>
                <li>Se perderá acceso a todas las funcionalidades</li>
                <li>Los datos de registro facial se eliminarán</li>
                <li>Se eliminarán las fotos asociadas</li>
              </ul>
            </div>
          </v-alert>
        </div>
      </v-card-text>
      
      <v-card-actions class="justify-center pa-4">
        <v-btn
          color="grey-600"
          variant="outlined"
          @click="$emit('update:showDialog', false)"
          :disabled="deleting"
        >
          Cancelar
        </v-btn>
        
        <v-btn
          color="red-400"
          @click="confirmDelete"
          :loading="deleting"
          :disabled="deleting"
          prepend-icon="mdi-delete"
        >
          {{ deleting ? 'Eliminando...' : 'Sí, Eliminar' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'EmployeeDeleteDialog',
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    employee: {
      type: Object,
      default: null
    },
    deleting: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:showDialog', 'confirm'],
  setup(props, { emit }) {
    // Métodos
    const confirmDelete = () => {
      emit('confirm', props.employee)
    }
    
    const getPositionLabel = (position) => {
      const labels = {
        'desarrollador': 'Desarrollador',
        'disenador': 'Diseñador',
        'secretario': 'Secretario/a',
        'gerente': 'Gerente',
        'analista': 'Analista',
        'ingeniero': 'Ingeniero',
        'contador': 'Contador',
        'recursos_humanos': 'RRHH',
        'marketing': 'Marketing',
        'ventas': 'Ventas',
        'soporte': 'Soporte',
        'administrativo': 'Administrativo',
        'operativo': 'Operativo',
        'otro': 'Otro'
      }
      return labels[position] || position
    }
    
    return {
      // Métodos
      confirmDelete,
      getPositionLabel
    }
  }
}
</script>

<style scoped>
.v-avatar {
  border: 3px solid rgba(239, 68, 68, 0.3);
}

.v-alert {
  border-left: 4px solid #f59e0b;
}
</style>
