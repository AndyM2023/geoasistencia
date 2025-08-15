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

// Importar estilos CSS personalizados
import './styles/index.css'

// Aplicar estilos críticos inmediatamente
document.body.style.backgroundColor = '#0a0a0f';
document.body.style.color = '#ffffff';

// Precargar el servicio de mapas para máxima velocidad
import mapService from './services/mapService'
// El singleton se inicializa automáticamente

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
