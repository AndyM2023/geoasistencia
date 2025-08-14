<template>
  <div>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Empleados</h1>
          <v-btn color="blue-400" prepend-icon="mdi-plus" @click="showDialog = true" class="neon-border">
            Nuevo Empleado
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Tabla de Empleados -->
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white">
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar empleado"
          single-line
          hide-details
          variant="outlined"
          density="compact"
          color="blue-400"
          class="text-white"
        ></v-text-field>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="employees"
        :search="search"
        :loading="loading"
        class="elevation-1 bg-dark-surface"
        theme="dark"
      >
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" color="blue-400" @click="editEmployee(item)"></v-btn>
          <v-btn icon="mdi-delete" size="small" color="red-400" @click="deleteEmployee(item)"></v-btn>
        </template>
        
        <template v-slot:item.status="{ item }">
          <v-chip :color="item.status === 'active' ? 'green-500' : 'red-500'" size="small" variant="tonal">
            {{ item.status === 'active' ? 'Activo' : 'Inactivo' }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog para Crear/Editar Empleado -->
    <v-dialog v-model="showDialog" max-width="600px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">{{ editingEmployee ? 'Editar' : 'Nuevo' }} Empleado</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.first_name"
                  label="Nombre"
                  required
                  :rules="[v => !!v || 'Nombre es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.last_name"
                  label="Apellido"
                  required
                  :rules="[v => !!v || 'Apellido es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="employeeForm.email"
                  label="Email"
                  type="email"
                  required
                  :rules="[v => !!v || 'Email es requerido', v => /.+@.+\..+/.test(v) || 'Email debe ser válido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.employee_id"
                  label="ID de Empleado"
                  required
                  :rules="[v => !!v || 'ID es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="employeeForm.position"
                  label="Cargo"
                  :items="positions"
                  required
                  :rules="[v => !!v || 'Cargo es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-select
                  v-model="employeeForm.area"
                  label="Área de Trabajo"
                  :items="areas"
                  item-title="name"
                  item-value="id"
                  required
                  :rules="[v => !!v || 'Área es requerida']"
                  color="blue-400"
                  variant="outlined"
                ></v-select>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDialog = false">Cancelar</v-btn>
          <v-btn color="blue-400" @click="saveEmployee" :loading="saving" class="neon-border">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Confirmación para Eliminar -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-h5 text-white">Confirmar Eliminación</v-card-title>
        <v-card-text class="text-grey-300">
          ¿Estás seguro de que quieres eliminar a <strong>{{ employeeToDelete?.first_name }} {{ employeeToDelete?.last_name }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDeleteDialog = false">Cancelar</v-btn>
          <v-btn color="red-400" @click="confirmDelete" :loading="deleting">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Employees',
  setup() {
    const search = ref('')
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const showDialog = ref(false)
    const showDeleteDialog = ref(false)
    const valid = ref(false)
    const form = ref(null)
    
    const editingEmployee = ref(null)
    const employeeToDelete = ref(null)
    
    const employees = ref([])
    const areas = ref([])
    
    const employeeForm = ref({
      first_name: '',
      last_name: '',
      email: '',
      employee_id: '',
      position: '',
      area: null
    })
    
    const positions = [
      'Desarrollador',
      'Diseñador',
      'Gerente',
      'Analista',
      'Administrativo',
      'Operario'
    ]
    
    const headers = [
      { title: 'ID', key: 'employee_id', sortable: true },
      { title: 'Nombre', key: 'first_name', sortable: true },
      { title: 'Apellido', key: 'last_name', sortable: true },
      { title: 'Email', key: 'email', sortable: true },
      { title: 'Cargo', key: 'position', sortable: true },
      { title: 'Área', key: 'area_name', sortable: true },
      { title: 'Estado', key: 'status', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false }
    ]
    
    const loadEmployees = async () => {
      loading.value = true
      try {
        // TODO: Cargar desde API
        employees.value = [
          {
            id: 1,
            employee_id: 'EMP001',
            first_name: 'Juan',
            last_name: 'Pérez',
            email: 'juan.perez@empresa.com',
            position: 'Desarrollador',
            area: 1,
            area_name: 'Desarrollo',
            status: 'active'
          },
          {
            id: 2,
            employee_id: 'EMP002',
            first_name: 'María',
            last_name: 'García',
            email: 'maria.garcia@empresa.com',
            position: 'Diseñadora',
            area: 2,
            area_name: 'Diseño',
            status: 'active'
          }
        ]
      } catch (error) {
        console.error('Error cargando empleados:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadAreas = async () => {
      try {
        // TODO: Cargar desde API
        areas.value = [
          { id: 1, name: 'Desarrollo' },
          { id: 2, name: 'Diseño' },
          { id: 3, name: 'Administración' }
        ]
      } catch (error) {
        console.error('Error cargando áreas:', error)
      }
    }
    
    const editEmployee = (employee) => {
      editingEmployee.value = employee
      employeeForm.value = { ...employee }
      showDialog.value = true
    }
    
    const deleteEmployee = (employee) => {
      employeeToDelete.value = employee
      showDeleteDialog.value = true
    }
    
    const confirmDelete = async () => {
      if (!employeeToDelete.value) return
      
      deleting.value = true
      try {
        // TODO: Eliminar desde API
        employees.value = employees.value.filter(emp => emp.id !== employeeToDelete.value.id)
        showDeleteDialog.value = false
        employeeToDelete.value = null
      } catch (error) {
        console.error('Error eliminando empleado:', error)
      } finally {
        deleting.value = false
      }
    }
    
    const saveEmployee = async () => {
      if (!form.value.validate()) return
      
      saving.value = true
      try {
        if (editingEmployee.value) {
          // TODO: Actualizar en API
          const index = employees.value.findIndex(emp => emp.id === editingEmployee.value.id)
          if (index !== -1) {
            employees.value[index] = { ...editingEmployee.value, ...employeeForm.value }
          }
        } else {
          // TODO: Crear en API
          const newEmployee = {
            id: Date.now(),
            ...employeeForm.value,
            status: 'active'
          }
          employees.value.push(newEmployee)
        }
        
        showDialog.value = false
        editingEmployee.value = null
        employeeForm.value = {
          first_name: '',
          last_name: '',
          email: '',
          employee_id: '',
          position: '',
          area: null
        }
      } catch (error) {
        console.error('Error guardando empleado:', error)
      } finally {
        saving.value = false
      }
    }
    
    onMounted(() => {
      loadEmployees()
      loadAreas()
    })
    
    return {
      search,
      loading,
      saving,
      deleting,
      showDialog,
      showDeleteDialog,
      valid,
      form,
      editingEmployee,
      employeeToDelete,
      employees,
      areas,
      employeeForm,
      positions,
      headers,
      editEmployee,
      deleteEmployee,
      confirmDelete,
      saveEmployee
    }
  }
}
</script>
