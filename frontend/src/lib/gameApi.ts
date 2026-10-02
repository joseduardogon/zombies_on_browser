import { isAxiosError } from 'axios';
import api from './api';
import type { Building, GameView, SaveInfo, SurvivorRole } from '../types/game';

/** Erro de requisicao com a mensagem ja pronta para o jogador. */
export class ApiError extends Error {
    /** Status HTTP, ou 0 se o servidor nao respondeu. */
    readonly status: number;

    /**
     * Cria o erro.
     *
     * @param message Mensagem legivel.
     * @param status Status HTTP, ou 0 sem resposta.
     */
    constructor(message: string, status: number) {
        super(message);
        this.status = status;
    }
}

/**
 * Executa uma requisicao e traduz falhas em `ApiError`.
 *
 * Usa o campo `detail` enviado pelo backend quando existir.
 *
 * @param request Funcao que dispara a requisicao.
 * @return O corpo da resposta.
 */
async function call<T>(request: () => Promise<{ data: T }>): Promise<T> {
    try {
        return (await request()).data;
    } catch (err) {
        if (isAxiosError(err)) {
            if (err.response) {
                const detail = err.response.data?.detail;
                const message = typeof detail === 'string' ? detail : err.response.statusText;
                throw new ApiError(message || 'Request failed', err.response.status);
            }
            throw new ApiError('Network Error: Unreachable (Check Backend)', 0);
        }
        throw err;
    }
}

/** Chamadas tipadas a API do jogo. */
export const gameApi = {
    /** Busca a partida corrente. */
    getGame: () => call<GameView>(() => api.get('/api/game')),

    /**
     * Cria uma nova partida.
     *
     * @param width Largura do mapa.
     * @param height Altura do mapa.
     * @param seed Semente opcional.
     */
    newGame: (width: number, height: number, seed?: number) =>
        call<GameView>(() => api.post('/api/game/new', { width, height, seed })),

    /**
     * Avanca o tempo.
     *
     * @param hours Horas a avancar.
     */
    tick: (hours: number) => call<GameView>(() => api.post('/api/game/tick', { hours })),

    /** Lista os jogos salvos. */
    listSaves: () => call<SaveInfo[]>(() => api.get('/api/game/saves')),

    /**
     * Grava a partida em um espaco.
     *
     * @param slot Nome do espaco.
     */
    save: (slot: string) => call<SaveInfo[]>(() => api.post('/api/game/save', { slot })),

    /**
     * Carrega um jogo salvo.
     *
     * @param slot Nome do espaco.
     */
    load: (slot: string) => call<GameView>(() => api.post('/api/game/load', { slot })),

    /**
     * Busca uma construcao.
     *
     * @param buildingId Identificador da construcao.
     */
    getBuilding: (buildingId: string) =>
        call<Building>(() => api.get(`/api/building/${buildingId}`)),

    /**
     * Escolhe o abrigo.
     *
     * @param buildingId Construcao escolhida.
     */
    claimBase: (buildingId: string) =>
        call<GameView>(() => api.post('/api/base/claim', { building_id: buildingId })),

    /**
     * Reforca uma abertura do abrigo.
     *
     * @param apertureId Abertura a reforcar.
     * @param survivorId Sobrevivente que faz o trabalho.
     */
    reinforce: (apertureId: string, survivorId: string) =>
        call<GameView>(() =>
            api.post('/api/base/reinforce', { aperture_id: apertureId, survivor_id: survivorId }),
        ),

    /**
     * Altera a funcao de um sobrevivente.
     *
     * @param survivorId Sobrevivente a alterar.
     * @param role Nova funcao.
     */
    setRole: (survivorId: string, role: SurvivorRole) =>
        call<GameView>(() => api.post(`/api/survivors/${survivorId}/role`, { role })),

    /**
     * Trata um sobrevivente ferido.
     *
     * @param survivorId Sobrevivente a tratar.
     */
    treat: (survivorId: string) =>
        call<GameView>(() => api.post(`/api/survivors/${survivorId}/treat`)),

    /**
     * Envia um sobrevivente a vasculhar uma construcao.
     *
     * @param survivorId Sobrevivente que vai.
     * @param buildingId Construcao alvo.
     */
    sendExpedition: (survivorId: string, buildingId: string) =>
        call<GameView>(() =>
            api.post('/api/expeditions', { survivor_id: survivorId, building_id: buildingId }),
        ),
};
