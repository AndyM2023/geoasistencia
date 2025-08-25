<template>
  <div class="employee-cards">
    <v-row>
      <v-col 
        v-for="employee in employees" 
        :key="employee.id" 
        cols="12" 
        sm="6" 
        md="4" 
        lg="3"
      >
        <v-card class="employee-card" hover>
          <!-- Header de la tarjeta con foto -->
          <div class="card-header">
            <v-avatar 
              size="80" 
              class="employee-avatar cursor-pointer" 
              @click="openPhotoModal(employee.photo_url)"
            >
              <v-img 
                v-if="employee.photo_url"
                :src="employee.photo_url" 
                cover
                :alt="`${employee.user.first_name} ${employee.user.last_name}`"
              />
              <div
                v-else
                class="avatar-placeholder"
              >
                <v-icon 
                  size="48" 
                  color="white"
                >
                  mdi-account
                </v-icon>
              </div>
            </v-avatar>
          </div>
          
          <!-- Contenido de la tarjeta -->
          <v-card-text class="pa-4">
            <div class="employee-info">
              <!-- Nombre del empleado -->
              <h3 class="employee-name">
                {{ employee.user.first_name }} {{ employee.user.last_name }}
              </h3>
              
              <!-- Posición -->
              <p class="employee-position">
                {{ getPositionLabel(employee.position) }}
              </p>
              
              <!-- Área -->
              <p class="employee-area">
                {{ employee.area_name || 'Sin asignar' }}
              </p>
              
              <!-- Email -->
              <p class="employee-email">
                {{ employee.user.email }}
              </p>
              
              <!-- Cédula -->
              <p class="employee-cedula">
                Cédula: {{ employee.cedula_display || employee.cedula || 'N/A' }}
              </p>
            </div>
          </v-card-text>
          
          <!-- Acciones de la tarjeta -->
          <v-card-actions class="pa-4 pt-0">
            <div class="actions-container">
              <v-btn
                icon="mdi-pencil"
                size="small"
                color="white"
                variant="text"
                @click="$emit('edit', employee)"
                class="action-btn"
              ></v-btn>
              
              <v-btn
                icon="mdi-delete"
                size="small"
                color="white"
                variant="text"
                @click="$emit('delete', employee)"
                class="action-btn"
              ></v-btn>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Sin datos -->
    <div v-if="employees.length === 0 && !loading" class="text-center py-8">
      <v-icon size="64" color="grey-400" class="mb-4">mdi-account-group-off</v-icon>
      <h3 class="text-grey-500 mb-2">No hay empleados</h3>
      <p class="text-grey-400">Crea el primer empleado para comenzar</p>
    </div>
    
    <!-- Modal de foto expandida -->
    <EmployeePhotoModal
      v-model:show-modal="showPhotoModal"
      :photo-url="selectedPhotoUrl"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import EmployeePhotoModal from './EmployeePhotoModal.vue'

export default {
  name: 'EmployeeCards',
  components: {
    EmployeePhotoModal
  },
  props: {
    employees: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['edit', 'delete'],
  setup() {
    const showPhotoModal = ref(false)
    const selectedPhotoUrl = ref(null)
    
    // Métodos de utilidad
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
        'otro': 'Otro',
        'administrador_personal': 'Administrador Personal'
      }
      return labels[position] || position
    }
    
    const openPhotoModal = (photoUrl) => {
      selectedPhotoUrl.value = photoUrl
      showPhotoModal.value = true
    }
    
    return {
      // Estado
      showPhotoModal,
      selectedPhotoUrl,
      
      // Métodos
      getPositionLabel,
      openPhotoModal
    }
  }
}
</script>
