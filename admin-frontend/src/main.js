import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        dark: true,
        colors: {
          primary: '#00d4ff',
          secondary: '#3b82f6',
          accent: '#8b5cf6',
          background: '#0a0a0f',
          surface: '#16213e',
          'surface-variant': '#1e293b',
          'on-surface': '#ffffff',
          'on-surface-variant': '#cbd5e1',
          error: '#ef4444',
          success: '#10b981',
          warning: '#f59e0b',
          info: '#06b6d4',
        }
      }
    }
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

// Inicializar la aplicación
app.mount('#app')
