<template>
  <div>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Áreas</h1>
          <v-btn color="blue-400" prepend-icon="mdi-plus" @click="showDialog = true" class="neon-border">
            Nueva Área
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Tabla de Áreas -->
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white">
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
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="areas"
        :search="search"
        :loading="loading"
        class="elevation-1 bg-dark-surface"
        theme="dark"
      >
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" color="blue-400" @click="editArea(item)"></v-btn>
          <v-btn icon="mdi-delete" size="small" color="red-400" @click="deleteArea(item)"></v-btn>
          <v-btn icon="mdi-map-marker" size="small" color="green-400" @click="showMap(item)"></v-btn>
        </template>
        
        <template v-slot:item.radius="{ item }">
          {{ item.radius }} metros
        </template>
        
        <template v-slot:item.employee_count="{ item }">
          <v-chip :color="item.employee_count > 0 ? 'green-500' : 'grey-500'" size="small" variant="tonal">
            {{ item.employee_count }} empleados
          </v-chip>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog para Crear/Editar Área -->
    <v-dialog v-model="showDialog" max-width="700px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">{{ editingArea ? 'Editar' : 'Nueva' }} Área</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.name"
                  label="Nombre del Área"
                  required
                  :rules="[v => !!v || 'Nombre es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.description"
                  label="Descripción"
                  required
                  :rules="[v => !!v || 'Descripción es requerida']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.latitude"
                  label="Latitud"
                  type="number"
                  step="0.000001"
                  required
                  :rules="[v => !!v || 'Latitud es requerida']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.longitude"
                  label="Longitud"
                  type="number"
                  step="0.000001"
                  required
                  :rules="[v => !!v || 'Longitud es requerida']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.radius"
                  label="Radio (metros)"
                  type="number"
                  min="10"
                  max="10000"
                  required
                  :rules="[v => !!v || 'Radio es requerido', v => v >= 10 || 'Radio mínimo 10m', v => v <= 10000 || 'Radio máximo 10km']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="areaForm.status"
                  label="Estado"
                  :items="['active', 'inactive']"
                  item-title="name"
                  item-value="value"
                  required
                  :rules="[v => !!v || 'Estado es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="areaForm.notes"
                  label="Notas Adicionales"
                  rows="3"
                  variant="outlined"
                  color="blue-400"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDialog = false">Cancelar</v-btn>
          <v-btn color="blue-400" @click="saveArea" :loading="saving" class="neon-border">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Confirmación para Eliminar -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-h5 text-white">Confirmar Eliminación</v-card-title>
        <v-card-text class="text-grey-300">
          ¿Estás seguro de que quieres eliminar el área <strong>{{ areaToDelete?.name }}</strong>?
          <br><br>
          <v-alert type="warning" variant="tonal">
            Esta acción no se puede deshacer y eliminará todas las referencias a esta área.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDeleteDialog = false">Cancelar</v-btn>
          <v-btn color="red-400" @click="confirmDelete" :loading="deleting">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog del Mapa -->
    <v-dialog v-model="showMapDialog" max-width="800px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">Ubicación del Área: {{ selectedArea?.name }}</span>
        </v-card-title>
        
        <v-card-text>
          <div class="text-center pa-8">
            <v-icon size="64" color="green-400">mdi-map-marker</v-icon>
            <div class="text-h6 mt-4 text-white">Mapa de Ubicación</div>
            <div class="text-body-2 text-grey-300 mb-4">
              Coordenadas: {{ selectedArea?.latitude }}, {{ selectedArea?.longitude }}
              <br>
              Radio: {{ selectedArea?.radius }} metros
            </div>
            <v-alert type="info" variant="tonal">
              Aquí se implementará un mapa interactivo para visualizar y editar la ubicación del área.
            </v-alert>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-400" @click="showMapDialog = false" class="neon-border">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Areas',
  setup() {
    const search = ref('')
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const showDialog = ref(false)
    const showDeleteDialog = ref(false)
    const showMapDialog = ref(false)
    const valid = ref(false)
    const form = ref(null)
    
    const editingArea = ref(null)
    const areaToDelete = ref(null)
    const selectedArea = ref(null)
    
    const areas = ref([])
    
    const areaForm = ref({
      name: '',
      description: '',
      latitude: '',
      longitude: '',
      radius: 100,
      status: 'active',
      notes: ''
    })
    
    const headers = [
      { title: 'ID', key: 'id', sortable: true },
      { title: 'Nombre', key: 'name', sortable: true },
      { title: 'Descripción', key: 'description', sortable: true },
      { title: 'Latitud', key: 'latitude', sortable: true },
      { title: 'Longitud', key: 'longitude', sortable: true },
      { title: 'Radio', key: 'radius', sortable: true },
      { title: 'Empleados', key: 'employee_count', sortable: true },
      { title: 'Estado', key: 'status', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false }
    ]
    
    const loadAreas = async () => {
      loading.value = true
      try {
        // TODO: Cargar desde API
        areas.value = [
          {
            id: 1,
            name: 'Oficina Central',
            description: 'Edificio principal de la empresa',
            latitude: 19.4326,
            longitude: -99.1332,
            radius: 150,
            status: 'active',
            employee_count: 15,
            notes: 'Área principal de trabajo'
          },
          {
            id: 2,
            name: 'Almacén Norte',
            description: 'Almacén de productos del norte',
            latitude: 19.4426,
            longitude: -99.1432,
            radius: 200,
            status: 'active',
            employee_count: 8,
            notes: 'Almacén de distribución'
          }
        ]
      } catch (error) {
        console.error('Error cargando áreas:', error)
      } finally {
        loading.value = false
      }
    }
    
    const editArea = (area) => {
      editingArea.value = area
      areaForm.value = { ...area }
      showDialog.value = true
    }
    
    const deleteArea = (area) => {
      areaToDelete.value = area
      showDeleteDialog.value = true
    }
    
    const showMap = (area) => {
      selectedArea.value = area
      showMapDialog.value = true
    }
    
    const confirmDelete = async () => {
      if (!areaToDelete.value) return
      
      deleting.value = true
      try {
        // TODO: Eliminar desde API
        areas.value = areas.value.filter(area => area.id !== areaToDelete.value.id)
        showDeleteDialog.value = false
        areaToDelete.value = null
      } catch (error) {
        console.error('Error eliminando área:', error)
      } finally {
        deleting.value = false
      }
    }
    
    const saveArea = async () => {
      if (!form.value.validate()) return
      
      saving.value = true
      try {
        if (editingArea.value) {
          // TODO: Actualizar en API
          const index = areas.value.findIndex(area => area.id === editingArea.value.id)
          if (index !== -1) {
            areas.value[index] = { ...editingArea.value, ...areaForm.value }
          }
        } else {
          // TODO: Crear en API
          const newArea = {
            id: Date.now(),
            ...areaForm.value,
            employee_count: 0
          }
          areas.value.push(newArea)
        }
        
        showDialog.value = false
        editingArea.value = null
        areaForm.value = {
          name: '',
          description: '',
          latitude: '',
          longitude: '',
          radius: 100,
          status: 'active',
          notes: ''
        }
      } catch (error) {
        console.error('Error guardando área:', error)
      } finally {
        saving.value = false
      }
    }
    
    onMounted(() => {
      loadAreas()
    })
    
    return {
      search,
      loading,
      saving,
      deleting,
      showDialog,
      showDeleteDialog,
      showMapDialog,
      valid,
      form,
      editingArea,
      areaToDelete,
      selectedArea,
      areas,
      areaForm,
      headers,
      editArea,
      deleteArea,
      showMap,
      confirmDelete,
      saveArea
    }
  }
}
</script>
