<template>
  <v-row class="mt-2 areas-header">
    <v-col cols="12">
      <div class="d-flex justify-space-between align-center">
        <h1 class="text-h4 text-white">Gestión de Áreas</h1>
        <div class="d-flex gap-2">
          <v-btn 
            color="blue-400" 
            prepend-icon="mdi-plus" 
            @click="$emit('newArea')" 
            class="neon-border"
          >
            Nueva Área
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

<style scoped>
.areas-header h1 {
  margin: 0;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.neon-border {
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.neon-border:hover {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}
</style>
