<template>
  <div class="employee-table">
    <v-data-table
      :headers="headers"
      :items="employees"
      :loading="loading"
      :search="search"
      :items-per-page="10"
      class="employee-data-table"
      hover
    >
      <!-- Nombre Completo -->
      <template v-slot:item.name="{ item }">
        <div class="employee-name-cell">
          {{ getCapitalizedName(item) }}
        </div>
      </template>

      <!-- Cédula -->
      <template v-slot:item.cedula="{ item }">
        <div class="employee-cedula-cell">
          {{ item.cedula_display || item.cedula || item.user?.cedula || 'N/A' }}
        </div>
      </template>

      <!-- Email -->
      <template v-slot:item.email="{ item }">
        <div class="employee-email-cell">
          {{ item.user?.email }}
        </div>
      </template>

      <!-- Cargo -->
      <template v-slot:item.position="{ item }">
        <div class="employee-position-cell">
          {{ getPositionLabel(item.position) }}
        </div>
      </template>

      <!-- Área -->
      <template v-slot:item.area="{ item }">
        <div class="employee-area-cell">
          {{ item.area_name || 'Sin asignar' }}
        </div>
      </template>

      <!-- Acciones -->
      <template v-slot:item.actions="{ item }">
        <div class="employee-actions-cell">
          <v-btn
            icon="mdi-pencil"
            size="small"
            color="white"
            variant="text"
            @click="$emit('edit', item)"
            class="action-btn"
          ></v-btn>
          
          <v-btn
            icon="mdi-account-star"
            size="small"
            color="white"
            variant="text"
            @click="$emit('face-registration', item)"
            class="action-btn"
          ></v-btn>
        </div>
      </template>

      <!-- Sin datos -->
      <template v-slot:no-data>
        <div class="text-center py-8">
          <v-icon size="64" color="grey-400" class="mb-4">mdi-account-group-off</v-icon>
          <h3 class="text-grey-500 mb-2">No hay empleados</h3>
          <p class="text-grey-400">Crea el primer empleado para comenzar</p>
        </div>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { capitalizeFullName } from '../utils/nameUtils'

export default {
  name: 'EmployeeTable',
  props: {
    employees: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    search: {
      type: String,
      default: ''
    }
  },
  emits: ['edit', 'delete', 'face-registration'],
  setup() {
    // Headers de la tabla exactamente como en la imagen
    const headers = [
      {
        title: 'Nombre Completo',
        key: 'name',
        sortable: true,
        width: '25%'
      },
      {
        title: 'Cédula',
        key: 'cedula',
        sortable: true,
        width: '15%'
      },
      {
        title: 'Email',
        key: 'email',
        sortable: true,
        width: '25%'
      },
      {
        title: 'Cargo',
        key: 'position',
        sortable: true,
        width: '15%'
      },
      {
        title: 'Área',
        key: 'area',
        sortable: true,
        width: '15%'
      },
      {
        title: 'Acciones',
        key: 'actions',
        sortable: false,
        width: '5%',
        align: 'center'
      }
    ]

    // Métodos de utilidad
    const getPositionLabel = (position) => {
      const positionLabels = {
        'desarrollador': 'Desarrollador',
        'disenador': 'Diseñador',
        'secretario': 'Secretario/a',
        'gerente': 'Gerente',
        'analista': 'Analista',
        'ingeniero': 'Ingeniero',
        'contador': 'Contador',
        'recursos_humanos': 'Recursos Humanos',
        'marketing': 'Marketing',
        'ventas': 'Ventas',
        'soporte': 'Soporte Técnico',
        'administrativo': 'Administrativo',
        'operativo': 'Operativo',
        'otro': 'Otro'
      }
      return positionLabels[position] || position
    }

    const getCapitalizedName = (employee) => {
      return capitalizeFullName(employee.user?.first_name, employee.user?.last_name)
    }

    return {
      headers,
      getPositionLabel,
      getCapitalizedName
    }
  }
}
</script>

<style scoped>
.employee-table {
  border-radius: 8px;
  overflow: hidden;
}

.cursor-pointer {
  cursor: pointer;
}

.actions-container {
  min-width: 120px;
}

/* Estilos para la tabla */
:deep(.v-data-table) {
  background: transparent !important;
}

:deep(.v-data-table__wrapper) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.v-data-table-header) {
  background: rgba(59, 130, 246, 0.1) !important;
}

:deep(.v-data-table-header th) {
  color: #60a5fa !important;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.875rem;
  letter-spacing: 0.05em;
}

:deep(.v-data-table__tr:hover) {
  background: rgba(59, 130, 246, 0.05) !important;
}

:deep(.v-data-table__td) {
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

:deep(.v-data-table__td:last-child) {
  border-bottom: none;
}
</style>
