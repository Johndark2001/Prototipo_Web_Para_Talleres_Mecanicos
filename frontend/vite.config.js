import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // En desarrollo la interfaz y la API comparten origen, igual que en producción
    // (ADR-001): la cookie de sesión funciona sin CORS.
    proxy: { '/api': 'http://localhost:8000' },
  },
})
