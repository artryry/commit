import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => ({
  plugins: [react()],

  base: '/',

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // ─── Dev-server settings (not used in production) ───
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:18000',
        changeOrigin: true,
      },
    },
  },

  // ─── Production build optimisations ─────────────────
  build: {
    target: 'es2020',
    outDir: 'dist',
    sourcemap: mode === 'development',
    minify: 'esbuild',
    cssMinify: true,
    rollupOptions: {
      output: {
        // Chunk splitting for better caching (Rolldown requires function form)
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            if (id.includes('react-dom') || id.includes('react-router-dom') || id.match(/\/react\//)) {
              return 'vendor-react';
            }
            if (id.includes('@tanstack/react-query')) {
              return 'vendor-query';
            }
            if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('zod')) {
              return 'vendor-form';
            }
            if (id.includes('zustand') || id.includes('axios')) {
              return 'vendor-state';
            }
          }
        },
      },
    },
    // Warn if any chunk exceeds 500kB
    chunkSizeWarningLimit: 500,
  },
}));
