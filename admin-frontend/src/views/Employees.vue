<template>
  <div>
    <!-- Header principal -->
    <v-row class="mt-0 employee-header">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Empleados</h1>
          <div class="d-flex gap-3">
            <v-btn 
              color="blue-400" 
              prepend-icon="mdi-plus" 
              @click="openCreateDialog" 
              class="neon-border"
            >
              NUEVO EMPLEADO
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Contenido principal -->
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white d-flex align-center">
        <!-- Input de búsqueda -->
        <v-text-field
          :model-value="searchQuery"
          label="Buscar empleado"
          placeholder="Buscar empleado"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          color="blue-400"
          bg-color="dark-surface"
          clearable
          class="search-input"
          @update:model-value="searchQuery = $event"
        ></v-text-field>
        
        <!-- Toggle para cambiar entre vista de lista y tarjetas -->
        <v-spacer></v-spacer>
        <v-btn-toggle
          v-model="viewMode"
          color="blue-400"
          group
          density="compact"
          class="view-toggle-buttons"
        >
          <v-btn value="table" prepend-icon="mdi-format-list-bulleted" title="Vista de Tabla">
            Lista
          </v-btn>
          <v-btn value="cards" prepend-icon="mdi-view-grid" title="Vista de Tarjetas">
            Tarjetas
          </v-btn>
        </v-btn-toggle>
      </v-card-title>

      <!-- Vista de tabla -->
      <div v-if="viewMode === 'table'">
        <EmployeeTable
          :employees="filteredEmployees"
          :loading="loading"
          :search-query="searchQuery"
          @edit="openEditDialog"
          @delete="openDeleteDialog"
          @face-registration="openFaceRegistration"
        />
      </div>

      <!-- Vista de tarjetas -->
      <div v-else-if="viewMode === 'cards'">
        <EmployeeCards
          :employees="filteredEmployees"
          :loading="loading"
          @edit="openEditDialog"
          @delete="openDeleteDialog"
          @face-registration="openFaceRegistration"
        />
      </div>

      <!-- Estado de carga -->
      <div v-if="loading" class="text-center py-8">
        <v-progress-circular indeterminate color="blue-400" size="64" class="mb-4"></v-progress-circular>
        <p class="text-grey-300">Cargando empleados...</p>
      </div>

      <!-- Sin datos -->
      <div v-else-if="filteredEmployees.length === 0" class="text-center py-8">
        <v-icon size="64" color="grey-400" class="mb-4">mdi-account-group-off</v-icon>
        <h3 class="text-h6 text-grey-400 mb-2">
          {{ hasActiveFilters ? 'No se encontraron resultados' : 'No hay empleados' }}
        </h3>
        <p class="text-grey-500 mb-4">
          {{ hasActiveFilters ? 'Intenta ajustar los filtros de búsqueda' : 'Crea el primer empleado para comenzar' }}
        </p>
        <v-btn 
          v-if="hasActiveFilters" 
          color="blue-400" 
          @click="clearFilters"
          prepend-icon="mdi-refresh"
        >
          Limpiar Filtros
        </v-btn>
      </div>
    </v-card>

    <!-- Formulario de empleado -->
    <EmployeeForm
      v-model:show-dialog="showDialog"
      :editing-employee="editingEmployee"
      :areas="areas"
      :employees="employees"
      :saving="saving"
      @close="closeDialog"
      @save="handleSaveEmployee"
      @face-registration="openFaceRegistration"
    />

    <!-- Diálogo de confirmación de eliminación -->
    <EmployeeDeleteDialog
      v-model:show-dialog="showDeleteDialog"
      :employee="employeeToDelete"
      :deleting="deleting"
      @confirm="confirmDelete"
    />

    <!-- Modal de registro facial -->
    <FaceRegistration
      v-if="showFaceRegistrationDialog"
      :show-dialog="showFaceRegistrationDialog"
      :employee-id="selectedEmployeeForFace?.id"
      :employee-name="selectedEmployeeForFace ? `${selectedEmployeeForFace.user.first_name} ${selectedEmployeeForFace.user.last_name}` : ''"
      :target-count="15"
      @registro-completo="onFaceRegistrationComplete"
      @registro-error="onFaceRegistrationError"
      @close="closeFaceRegistrationDialog"
    />

    <!-- Modal de importación -->
    <EmployeeImport
      v-model:show-dialog="showImportDialog"
      @import-complete="onImportComplete"
      @import-error="onImportError"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useEmployees } from '../composables/useEmployees'
import EmployeeForm from '../components/EmployeeForm.vue'
import EmployeeTable from '../components/EmployeeTable.vue'
import EmployeeCards from '../components/EmployeeCards.vue'
import EmployeeFilters from '../components/EmployeeFilters.vue'
import EmployeeDeleteDialog from '../components/EmployeeDeleteDialog.vue'
import FaceRegistration from '../components/FaceRegistration.vue'
import EmployeeImport from '../components/EmployeeImport.vue'

export default {
  name: 'Employees',
  components: {
    EmployeeForm,
    EmployeeTable,
    EmployeeCards,
    EmployeeFilters,
    EmployeeDeleteDialog,
    FaceRegistration,
    EmployeeImport
  },
  setup() {
    // Usar el composable principal
    const {
      // Estado
      employees,
      areas,
      loading,
      saving,
      showDialog,
      editingEmployee,
      searchQuery,
      viewMode,
      
      // Computed
      filteredEmployees,
      
      // Métodos CRUD
      loadEmployees,
      createEmployee,
      updateEmployee,
      deleteEmployee,
      
      // Métodos UI
      openCreateDialog,
      openEditDialog,
      closeDialog,
      saveEmployee,
      toggleViewMode,
      clearFilters
    } = useEmployees()

    // Debug: Verificar que areas se está recibiendo correctamente
    console.log('🔍 Employees.vue - areas recibido del composable:', areas)
    console.log('🔍 Employees.vue - areas es ref:', areas?.__v_isRef)
    console.log('🔍 Employees.vue - areas.value:', areas?.value)
    console.log('🔍 Employees.vue - areas length:', areas?.value?.length)

    // Estado local para diálogos adicionales
    const showDeleteDialog = ref(false)
    const employeeToDelete = ref(null)
    const deleting = ref(false)
    const showFaceRegistrationDialog = ref(false)
    const selectedEmployeeForFace = ref(null)
    const showImportDialog = ref(false)

    // Computed properties
    const hasActiveFilters = computed(() => {
      return searchQuery.value
    })

    // Métodos para manejo de eliminación
    const openDeleteDialog = (employee) => {
      employeeToDelete.value = employee
      showDeleteDialog.value = true
    }

    const confirmDelete = async (employee) => {
      try {
        deleting.value = true
        await deleteEmployee(employee.id)
        showDeleteDialog.value = false
        employeeToDelete.value = null
      } catch (error) {
        console.error('Error al eliminar empleado:', error)
      } finally {
        deleting.value = false
      }
    }

    // Métodos para manejo de registro facial
    const openFaceRegistration = (employee) => {
      console.log('🎯 openFaceRegistration llamado con:', employee);
      console.log('🔍 employee.id:', employee?.id);
      console.log('🔍 employee.user:', employee?.user);
      console.log('🔍 employee.user.first_name:', employee?.user?.first_name);
      console.log('🔍 employee.user.last_name:', employee?.user?.last_name);
      
      selectedEmployeeForFace.value = employee;
      console.log('🔍 selectedEmployeeForFace.value después:', selectedEmployeeForFace.value);
      
      showFaceRegistrationDialog.value = true;
      console.log('🔍 showFaceRegistrationDialog.value después:', showFaceRegistrationDialog.value);
      
      // Debug adicional
      console.log('🔍 Estado completo del modal:', {
        showFaceRegistrationDialog: showFaceRegistrationDialog.value,
        selectedEmployeeForFace: selectedEmployeeForFace.value,
        employeeId: selectedEmployeeForFace.value?.id,
        employeeName: selectedEmployeeForFace.value ? `${selectedEmployeeForFace.value.user.first_name} ${selectedEmployeeForFace.value.user.last_name}` : ''
      });
    }

    const closeFaceRegistrationDialog = () => {
      showFaceRegistrationDialog.value = false
      selectedEmployeeForFace.value = null
    }

    const onFaceRegistrationComplete = (result) => {
      console.log('✅ Registro facial completado:', result)
      closeFaceRegistrationDialog()
      // Recargar empleados para actualizar estado facial
      loadEmployees()
    }

    const onFaceRegistrationError = (error) => {
      console.error('❌ Error en registro facial:', error)
      closeFaceRegistrationDialog()
    }

    // Métodos para manejo de importación
    const onImportComplete = (result) => {
      console.log('✅ Importación completada:', result)
      showImportDialog.value = false
      // Recargar empleados para mostrar los nuevos
      loadEmployees()
    }

    const onImportError = (error) => {
      console.error('❌ Error en importación:', error)
      showImportDialog.value = false
    }

    // Métodos para manejo de empleados
    const handleSaveEmployee = async (employeeData) => {
      try {
        console.log('🔄 handleSaveEmployee llamado con:', employeeData);
        console.log('🔍 editingEmployee.value:', editingEmployee.value);
        
        const result = await saveEmployee(employeeData)
        console.log('✅ saveEmployee completado, resultado:', result);
        
        // Si es un empleado nuevo (no editingEmployee), abrir registro facial
        if (!editingEmployee.value) {
          console.log('🆕 Empleado nuevo creado, abriendo registro facial...');
          console.log('👤 Empleado creado:', result);
          console.log('🔍 selectedEmployeeForFace antes:', selectedEmployeeForFace.value);
          
          // Configurar el empleado para el registro facial
          selectedEmployeeForFace.value = result;
          console.log('🔍 selectedEmployeeForFace después:', selectedEmployeeForFace.value);
          
          // Cerrar el formulario de creación y abrir el registro facial
          showDialog.value = false;
          showFaceRegistrationDialog.value = true;
          console.log('🎯 showFaceRegistrationDialog.value = true');
          console.log('🔍 showFaceRegistrationDialog.value después:', showFaceRegistrationDialog.value);
        } else {
          console.log('✏️ Empleado editado, cerrando diálogo...');
          // Si es edición, cerrar el diálogo
          closeDialog()
        }
      } catch (error) {
        console.error('❌ Error en handleSaveEmployee:', error);
        // El error ya se maneja en el composable
      }
    }

    // Inicialización
    onMounted(async () => {
      console.log('🚀 Componente Employees montado')
      // Los datos se cargan automáticamente en el composable
    })

    return {
      // Estado del composable
      employees,
      areas, // ✅ AGREGAR areas al return
      loading,
      saving,
      showDialog,
      editingEmployee,
      searchQuery,
      viewMode,
      
      // Computed del composable
      filteredEmployees,
      
      // Estado local
      showDeleteDialog,
      employeeToDelete,
      deleting,
      showFaceRegistrationDialog,
      selectedEmployeeForFace,
      showImportDialog,
      
      // Computed local
      hasActiveFilters,
      
      // Métodos del composable
      loadEmployees,
      createEmployee,
      updateEmployee,
      deleteEmployee,
      openCreateDialog,
      openEditDialog,
      closeDialog,
      saveEmployee,
      toggleViewMode,
      clearFilters,
      
      // Métodos locales
      openDeleteDialog,
      confirmDelete,
      openFaceRegistration,
      closeFaceRegistrationDialog,
      onFaceRegistrationComplete,
      onFaceRegistrationError,
      onImportComplete,
      onImportError,
      handleSaveEmployee
    }
  }
}
</script>
