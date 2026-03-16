import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// Get the version from environment variables or use a default value
const version = process.env.VERSION || 'latest';

// Define the base path for the build
export default defineConfig({
  optimizeDeps: {
    include: [
      '@emotion/react', 
      '@emotion/styled', 
      '@mui/material/Tooltip'
    ],
  },
  plugins: [react({
    jsxImportSource: '@emotion/react',
    babel: {
      plugins: ['@emotion/babel-plugin'],
    },
  }),],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server:{
    // port:3006, //dev
    port:3012,  //prod
  },
  // base: '/Acoustic_Chart_Dev',
  // build: {
  //   outDir: path.resolve(__dirname, `Acoustic_Chart_Dev`), // Set the output directory based on the version
  // },

  base: '/VOYA_CLIENT_APP',
  build: {
    outDir: path.resolve(__dirname, `VOYA_CLIENT_APP`), // Set the output directory based on the version
  },
});