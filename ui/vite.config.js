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
        target: 'http://10.70.95.95:8080',
        changeOrigin: true
      },
      '/api': {
        target: 'http://10.70.95.95:8080',
        changeOrigin: true
      }
    }
  }
})