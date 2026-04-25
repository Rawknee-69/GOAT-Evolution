import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:7860',
      '/ws': {
        target: 'ws://localhost:7860',
        ws: true,
      },
      '/health': 'http://localhost:7860',
      '/metadata': 'http://localhost:7860',
      '/schema': 'http://localhost:7860',
      '/tasks': 'http://localhost:7860',
      '/sse': 'http://localhost:7860',
    },
  },
})
