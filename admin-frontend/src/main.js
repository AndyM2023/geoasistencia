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

// Asegurar que los estilos se carguen correctamente
document.addEventListener('DOMContentLoaded', () => {
  // Verificar que los estilos estén cargados
  const styleSheets = Array.from(document.styleSheets);
  console.log('Hojas de estilo cargadas:', styleSheets.length);
  
  // Aplicar estilos críticos si es necesario
  if (!styleSheets.some(sheet => sheet.href && sheet.href.includes('index.css'))) {
    console.warn('Estilos personalizados no cargados, aplicando estilos de respaldo');
    document.body.style.backgroundColor = '#0a0a0f';
    document.body.style.color = '#ffffff';
  }
});

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
