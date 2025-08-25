<template>
  <v-dialog
    :model-value="showDialog"
    @update:model-value="$emit('update:showDialog', $event)"
    max-width="600px"
    persistent
  >
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white d-flex align-center">
        <v-icon color="blue-400" class="mr-2">mdi-upload</v-icon>
        Importar Empleados
        <v-spacer></v-spacer>
        <v-btn
          icon="mdi-close"
          variant="text"
          color="grey-400"
          @click="$emit('update:showDialog', false)"
        ></v-btn>
      </v-card-title>

      <v-card-text class="pa-6">
        <div class="mb-6">
          <p class="text-grey-300 mb-4">
            Importa empleados desde un archivo CSV. El archivo debe contener las siguientes columnas:
          </p>
          
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
            color="blue-400"
          >
            <div class="text-body-2">
              <strong>Columnas requeridas:</strong><br>
              • first_name (Nombre)<br>
              • last_name (Apellido)<br>
              • email (Correo electrónico)<br>
              • cedula (Cédula)<br>
              • position (Cargo)<br>
              • area (Área)<br>
              • hire_date (Fecha de contratación - YYYY-MM-DD)
            </div>
          </v-alert>

          <v-alert
            type="warning"
            variant="tonal"
            class="mb-4"
            color="orange-400"
          >
            <div class="text-body-2">
              <strong>Nota:</strong> Los empleados importados se crearán con contraseñas temporales que deberán cambiar en su primer inicio de sesión.
            </div>
          </v-alert>
        </div>

        <!-- Upload de archivo -->
        <v-file-input
          v-model="selectedFile"
          accept=".csv"
          label="Seleccionar archivo CSV"
          prepend-icon="mdi-file-document"
          variant="outlined"
          color="blue-400"
          :rules="[v => !!v || 'Debe seleccionar un archivo']"
          :error-messages="fileError"
          @change="onFileSelected"
        ></v-file-input>

        <!-- Vista previa del archivo -->
        <div v-if="filePreview.length > 0" class="mt-4">
          <h4 class="text-h6 text-white mb-3">Vista previa del archivo:</h4>
          <v-table class="bg-dark-surface">
            <thead>
              <tr>
                <th v-for="header in fileHeaders" :key="header" class="text-left text-white">
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in filePreview.slice(0, 5)" :key="index">
                <td v-for="header in fileHeaders" :key="header" class="text-grey-300">
                  {{ row[header] || '-' }}
                </td>
              </tr>
              <tr v-if="filePreview.length > 5">
                <td :colspan="fileHeaders.length" class="text-center text-grey-500">
                  ... y {{ filePreview.length - 5 }} filas más
                </td>
              </tr>
            </tbody>
          </v-table>
        </div>

        <!-- Opciones de importación -->
        <div v-if="selectedFile" class="mt-4">
          <v-checkbox
            v-model="skipDuplicates"
            label="Omitir empleados duplicados (por cédula)"
            color="blue-400"
            hide-details
          ></v-checkbox>
          
          <v-checkbox
            v-model="sendWelcomeEmail"
            label="Enviar email de bienvenida"
            color="blue-400"
            hide-details
          ></v-checkbox>
        </div>
      </v-card-text>

      <v-card-actions class="pa-6 pt-0">
        <v-spacer></v-spacer>
        <v-btn
          color="grey-400"
          variant="outlined"
          @click="$emit('update:showDialog', false)"
          :disabled="importing"
        >
          Cancelar
        </v-btn>
        <v-btn
          color="blue-400"
          :loading="importing"
          :disabled="!selectedFile || !fileValid"
          @click="startImport"
        >
          <v-icon left>mdi-upload</v-icon>
          {{ importing ? 'Importando...' : 'Importar' }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Modal de progreso -->
    <v-dialog
      v-model="showProgress"
      persistent
      max-width="400px"
    >
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white text-center">
          <v-icon color="blue-400" class="mr-2">mdi-progress-clock</v-icon>
          Importando Empleados
        </v-card-title>
        
        <v-card-text class="text-center pa-6">
          <v-progress-circular
            :value="importProgress"
            size="80"
            width="8"
            color="blue-400"
            class="mb-4"
          >
            {{ Math.round(importProgress) }}%
          </v-progress-circular>
          
          <p class="text-grey-300 mb-2">
            Procesando empleado {{ currentEmployeeIndex }} de {{ totalEmployees }}
          </p>
          
          <p class="text-grey-500 text-body-2">
            {{ currentEmployeeName }}
          </p>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useEmployeeImport } from '../composables/useEmployeeImport'

export default {
  name: 'EmployeeImport',
  props: {
    showDialog: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:showDialog', 'import-complete', 'import-error'],
  setup(props, { emit }) {
    const {
      selectedFile,
      fileError,
      filePreview,
      fileHeaders,
      fileValid,
      importing,
      importProgress,
      currentEmployeeIndex,
      totalEmployees,
      currentEmployeeName,
      showProgress,
      skipDuplicates,
      sendWelcomeEmail,
      onFileSelected,
      startImport,
      resetImport
    } = useEmployeeImport()

    // Resetear estado cuando se cierra el diálogo
    watch(() => props.showDialog, (newValue) => {
      if (!newValue) {
        resetImport()
      }
    })

    return {
      selectedFile,
      fileError,
      filePreview,
      fileHeaders,
      fileValid,
      importing,
      importProgress,
      currentEmployeeIndex,
      totalEmployees,
      currentEmployeeName,
      showProgress,
      skipDuplicates,
      sendWelcomeEmail,
      onFileSelected,
      startImport
    }
  }
}
</script>

<style scoped>
.v-table {
  border-radius: 8px;
  overflow: hidden;
}

.v-table th {
  background-color: rgba(59, 130, 246, 0.1);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.v-table td {
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}
</style>
