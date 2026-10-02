# Modulo lib

Arquivo: `src/lib/api.ts`.

Exporta uma instancia do Axios com `Content-Type: application/json`. Nao define `baseURL`: o proxy de `/api` em `vite.config.ts` encaminha para `http://127.0.0.1:8000` durante o desenvolvimento.
