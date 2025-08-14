<template>
  <v-card class="stats-card" :color="color" variant="tonal">
    <v-card-text class="pa-4">
      <div class="d-flex align-center">
        <div class="flex-grow-1">
          <div class="text-h6 font-weight-bold mb-1">{{ title }}</div>
          <div class="text-h4 font-weight-bold">{{ value }}</div>
          <div class="text-body-2 text-medium-emphasis">{{ subtitle }}</div>
        </div>
        <div class="ml-4">
          <v-icon size="48" :color="iconColor">{{ icon }}</v-icon>
        </div>
      </div>
      
      <!-- Indicador de cambio -->
      <div v-if="change" class="mt-3 d-flex align-center">
        <v-icon 
          :color="change > 0 ? 'success' : 'error'"
          size="small"
          class="mr-1"
        >
          {{ change > 0 ? 'mdi-trending-up' : 'mdi-trending-down' }}
        </v-icon>
        <span 
          :class="change > 0 ? 'text-success' : 'text-error'"
          class="text-body-2 font-weight-medium"
        >
          {{ Math.abs(change) }}%
        </span>
        <span class="text-body-2 text-medium-emphasis ml-1">vs mes anterior</span>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'StatsCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      required: true
    },
    color: {
      type: String,
      default: 'primary'
    },
    iconColor: {
      type: String,
      default: 'primary'
    },
    change: {
      type: Number,
      default: null
    }
  }
}
</script>
