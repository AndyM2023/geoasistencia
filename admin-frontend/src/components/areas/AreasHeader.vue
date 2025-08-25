<template>
  <v-row class="mt-0 areas-header">
    <v-col cols="12">
      <div class="d-flex justify-space-between align-center">
        <h1 class="text-h4 text-white">Gestión de Áreas</h1>
        <div class="d-flex gap-3">
          <v-btn 
            color="blue-400" 
            prepend-icon="mdi-plus" 
            @click="$emit('newArea')" 
            class="neon-border"
          >
            NUEVA ÁREA
          </v-btn>
        </div>
      </div>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'AreasHeader',
  emits: ['newArea']
}
</script>
