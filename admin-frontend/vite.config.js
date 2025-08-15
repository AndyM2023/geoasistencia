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
    proxy: {
      '/app': {
        target: 'http://localhost:8000',
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
