import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,

    proxy: {
      '/accounts': {
        target: 'http://192.168.1.38:8080',
        changeOrigin: true
      },
      '/api': {
        target: 'http://192.168.1.38:8080',
        changeOrigin: true
      }
    }
  }
})
