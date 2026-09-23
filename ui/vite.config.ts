import { defineConfig } from 'vite';

export default defineConfig({
  // Keep the dev origin aligned with FastAPI's default CORS allowlist.
  server: { port: 5173, strictPort: true },
});
