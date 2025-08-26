<template>
  <v-dialog
    :model-value="showModal"
    @update:model-value="$emit('update:showModal', $event)"
    max-width="600px"
    persistent
  >
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white d-flex align-center">
        <v-icon color="blue-400" class="mr-2">mdi-image</v-icon>
         Vista Expandida de la Foto
        <v-spacer></v-spacer>
        <v-btn 
          icon="mdi-close" 
          size="small" 
          color="grey-400" 
          variant="text"
          @click="$emit('update:showModal', false)"
        ></v-btn>
      </v-card-title>
      
      <v-card-text class="pa-6">
        <div class="text-center">
          <v-avatar size="400" class="mb-4">
            <v-img 
              :src="photoUrl || '/default-avatar.png'" 
              cover
              class="photo-expanded"
            ></v-img>
          </v-avatar>
          
          <div v-if="photoUrl" class="mt-4">
            <p class="text-grey-300 text-sm">
              Haz clic derecho en la imagen para guardarla
            </p>
          </div>
          
          <div v-else class="mt-4">
            <v-icon color="grey-500" size="64" class="mb-2">mdi-image-off</v-icon>
            <p class="text-grey-500">No hay foto disponible</p>
          </div>
        </div>
      </v-card-text>
      
      <v-card-actions class="justify-center pa-4">
        <v-btn
          color="blue-400"
          variant="outlined"
          @click="$emit('update:showModal', false)"
        >
          Cerrar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'EmployeePhotoModal',
  props: {
    showModal: {
      type: Boolean,
      default: false
    },
    photoUrl: {
      type: String,
      default: null
    }
  },
  emits: ['update:showModal']
}
</script>

<style scoped>
.photo-expanded {
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.photo-expanded:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}
</style>
