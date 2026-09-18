import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/readiness': 'http://localhost:8000',
      '/adjudication': 'http://localhost:8000',
      '/eval': 'http://localhost:8000',
      '/extract-policy': 'http://localhost:8000',
      '/extract-evidence': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})
