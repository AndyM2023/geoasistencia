<template>
  <v-dialog :model-value="showDeleteDialog" @update:model-value="$emit('update:showDeleteDialog', $event)" max-width="400px">
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
        <v-btn color="grey-400" variant="text" @click="$emit('cancel')">Cancelar</v-btn>
        <v-btn color="red-400" @click="$emit('confirm')" :loading="deleting">Eliminar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'DeleteConfirmationDialog',
  props: {
    showDeleteDialog: {
      type: Boolean,
      required: true
    },
    areaToDelete: {
      type: Object,
      default: null
    },
    deleting: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel', 'update:showDeleteDialog']
}
</script>
