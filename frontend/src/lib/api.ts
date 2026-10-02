import axios from 'axios';

/**
 * Cliente HTTP compartilhado.
 *
 * Nao define baseURL: as chamadas a `/api` passam pelo proxy do Vite.
 */
const api = axios.create({
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;
