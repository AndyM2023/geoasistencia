<template>
  <v-navigation-drawer
    v-model="internalDrawer"
    app
    class="bg-dark-surface"
    width="280"
  >
    <!-- Logo en el drawer -->
    <div class="pa-4 border-b border-blue-500/20">
      <div class="d-flex align-center">
        <v-icon
          size="28"
          color="blue-400"
          class="mr-3"
        >
          mdi-fingerprint
        </v-icon>
        <span class="text-h6 font-weight-bold text-white">
          GeoAsistencia
        </span>
      </div>
    </div>

    <!-- Menú de navegación -->
    <v-list class="pa-2">
      <v-list-item
        v-for="item in menuItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        class="mb-1 rounded-lg"
        :class="{ 'bg-blue-500/20': $route.path === item.to }"
        color="blue-400"
        variant="text"
      >
        <template v-slot:prepend>
          <v-icon
            :color="$route.path === item.to ? 'blue-400' : 'grey-400'"
            size="20"
          >
            {{ item.icon }}
          </v-icon>
        </template>
        
        <v-list-item-title
          :class="$route.path === item.to ? 'text-blue-400 font-weight-medium' : 'text-grey-300'"
        >
          {{ item.title }}
        </v-list-item-title>
      </v-list-item>
    </v-list>

    <!-- Información del sistema -->
    <template v-slot:append>
      <div class="pa-4 border-t border-blue-500/20">
        <div class="text-center">
          <v-chip
            color="green-500"
            size="small"
            variant="tonal"
            class="mb-2"
          >
            <v-icon left size="16">mdi-circle</v-icon>
            Sistema Activo
          </v-chip>
          <p class="text-caption text-grey-400 mb-0">
            v1.0.0
          </p>
        </div>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'SideNav',
  props: {
    modelValue: {
      type: Boolean,
      default: true
    },
    menuItems: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const internalDrawer = ref(props.modelValue)

    watch(
      () => props.modelValue,
      (val) => {
        internalDrawer.value = val
      }
    )

    watch(internalDrawer, (val) => {
      emit('update:modelValue', val)
    })

    return {
      internalDrawer
    }
  }
}
</script>
