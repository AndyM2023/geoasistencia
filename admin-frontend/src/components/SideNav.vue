<template>
  <v-navigation-drawer
    v-model="internalDrawer"
    :location="$vuetify.display.mdAndDown ? 'left' : 'left'"
    :temporary="$vuetify.display.mdAndDown"
    :permanent="$vuetify.display.lgAndUp"
    class="bg-dark-surface"
    width="280"
    overlay-color="rgba(0, 0, 0, 0.7)"
    scrim="false"
  >
    <!-- Menú de navegación -->
    <v-list class="pa-2">
      <v-list-item
        v-for="item in menuItems"
        :key="item.title"
        :to="item.to"
        class="mb-1 rounded-lg"
        :class="{ 'bg-blue-500/20': $route.path === item.to }"
        color="blue-400"
        variant="text"
        @click="handleNavClick"
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
          
        </div>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script>
import { ref, watch } from 'vue'
import { useDisplay } from 'vuetify'

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
    const { lgAndUp } = useDisplay()
    const internalDrawer = ref(props.modelValue)

    // Debug: Log cuando cambia el valor
    console.log('SideNav: modelValue changed to:', props.modelValue)

    watch(
      () => props.modelValue,
      (val) => {
        console.log('SideNav: Updating internalDrawer to:', val)
        internalDrawer.value = val
      },
      { immediate: true }
    )

    watch(internalDrawer, (val) => {
      console.log('SideNav: Emitting update:modelValue with:', val)
      emit('update:modelValue', val)
    })

    // Función para manejar clicks en navegación en móviles
    const handleNavClick = () => {
      // Cerrar el drawer en dispositivos móviles y tablets
      if (!lgAndUp.value) {
        console.log('SideNav: Closing drawer on mobile navigation')
        setTimeout(() => {
          internalDrawer.value = false
        }, 150) // Pequeño delay para permitir la navegación
      }
    }

    return {
      internalDrawer,
      handleNavClick
    }
  }
}
</script>

<style scoped>
/* Overlay mejorado para mejor UX */
:deep(.v-overlay--active) {
  backdrop-filter: blur(2px);
}

/* Asegurar que el drawer sea visible */
:deep(.v-navigation-drawer) {
  z-index: 1000;
}

/* Estilos para el drawer temporal en móviles */
:deep(.v-navigation-drawer--temporary) {
  z-index: 1001;
}
</style>
