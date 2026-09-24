import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  root: path.resolve(__dirname),
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      // Proxy backend API calls
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Proxy per-product SVGs served by FastAPI static mount
      '/product-visuals': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Proxy all other backend routes (recommendations, users, items, etc.)
      '/recommendations': { target: 'http://localhost:8000', changeOrigin: true },
      '/users':           { target: 'http://localhost:8000', changeOrigin: true },
      '/items':           { target: 'http://localhost:8000', changeOrigin: true },
      '/config':          { target: 'http://localhost:8000', changeOrigin: true },
      '/metrics':         { target: 'http://localhost:8000', changeOrigin: true },
      '/auth':            { target: 'http://localhost:8000', changeOrigin: true },
      '/health':          { target: 'http://localhost:8000', changeOrigin: true },
    }
  }
})
