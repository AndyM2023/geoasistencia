import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  css: {
    // Asegurar que Vite procese correctamente los archivos CSS
    preprocessorOptions: {
      css: {
        charset: false
      }
    }
  },
  server: {
    port: 5173,
    historyApiFallback: true, // Crucial para SPAs con Vue Router
    proxy: {
      '/app': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        // Solo proxear requests de API, no rutas del frontend
        bypass: function (req, res, proxyOptions) {
          // Si es una request para el frontend (HTML), servir index.html
          if (req.headers.accept && req.headers.accept.includes('text/html')) {
            return '/index.html'
          }
        }
      },
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  // Asegurar que los assets se sirvan correctamente
  build: {
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name].[hash].[ext]'
      }
    }
  }
})
