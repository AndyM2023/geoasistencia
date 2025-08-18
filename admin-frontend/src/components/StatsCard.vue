<template>
  <v-card class="stats-card" :color="color" variant="tonal">
    <v-card-text class="pa-1">
      <div class="d-flex align-center mb-1">
        <div class="flex-grow-1">
          <div class="text-h6 font-weight-bold mb-1">{{ title }}</div>
          <div class="text-h4 font-weight-bold">{{ displayValue }}</div>
          <div class="text-body-2 text-medium-emphasis">{{ subtitle }}</div>
        </div>
        <div class="ml-1">
          <v-icon size="28" :color="iconColor">{{ icon }}</v-icon>
        </div>
      </div>
      
      <!-- Indicador de cambio - siempre presente para mantener layout -->

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
  },
  computed: {
    displayValue() {
      if (this.value === null || this.value === undefined || this.value === '') {
        return '0'
      }
      return this.value.toString()
    }
  }
}
</script>
