<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card>
      <v-card-title class="text-h5">
        {{ title }}
      </v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <slot name="form-content"></slot>
        </v-form>
      </v-card-text>
      
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn 
          color="grey-darken-1" 
          variant="text" 
          @click="closeDialog"
        >
          Cancelar
        </v-btn>
        <v-btn 
          color="primary" 
          :loading="loading"
          :disabled="!valid || loading"
          @click="handleSubmit"
        >
          {{ submitText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'FormDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Formulario'
    },
    submitText: {
      type: String,
      default: 'Guardar'
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'submit'],
  setup(props, { emit }) {
    const dialog = ref(props.modelValue)
    const valid = ref(false)
    const form = ref(null)
    
    watch(() => props.modelValue, (newVal) => {
      dialog.value = newVal
    })
    
    watch(dialog, (newVal) => {
      emit('update:modelValue', newVal)
    })
    
    const closeDialog = () => {
      dialog.value = false
      if (form.value) {
        form.value.reset()
      }
    }
    
    const handleSubmit = () => {
      if (form.value && form.value.validate()) {
        emit('submit')
      }
    }
    
    return {
      dialog,
      valid,
      form,
      closeDialog,
      handleSubmit
    }
  }
}
</script>
