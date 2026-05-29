// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"

export default defineConfig({
  base: './',
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: '127.0.0.1',      // ← ADD THIS LINE (was missing, Electron needs it)
    proxy: {
      '/api': 'http://localhost:8000',
    }
  }
})
