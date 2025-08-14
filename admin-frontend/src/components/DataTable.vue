<template>
  <div>
    <!-- Barra de búsqueda y filtros -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="search"
              label="Buscar..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6" class="d-flex justify-end">
            <slot name="actions"></slot>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tabla de datos -->
    <v-data-table
      :headers="headers"
      :items="items"
      :search="search"
      :loading="loading"
      :items-per-page="10"
      class="elevation-1"
    >
      <!-- Slot para acciones personalizadas en cada fila -->
      <template v-slot:item.actions="{ item }">
        <slot name="row-actions" :item="item"></slot>
      </template>

      <!-- Slot para contenido personalizado en columnas específicas -->
      <template v-slot:item="{ item, index }">
        <tr>
          <td v-for="header in headers" :key="header.key">
            <slot 
              :name="`item.${header.key}`" 
              :item="item" 
              :index="index"
              :value="item[header.key]"
            >
              {{ item[header.key] }}
            </slot>
          </td>
        </tr>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'DataTable',
  props: {
    headers: {
      type: Array,
      required: true
    },
    items: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const search = ref('')
    
    return {
      search
    }
  }
}
</script>
