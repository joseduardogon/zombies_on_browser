import { create } from 'zustand';
import { isAxiosError } from 'axios';
import api from '../lib/api';

/** Posicao em uma grade 2D. */
export interface Coordinates {
    x: number;
    y: number;
}

/** Celula do mapa, espelho de `WorldCell` no backend. */
export interface WorldCell {
    coordinates: Coordinates;
    sector_type: string;
    is_explored: boolean;
    building_id?: string | null;
}

/** Mapa do mundo, espelho de `WorldMap` no backend. */
export interface WorldMap {
    width: number;
    height: number;
    cells: WorldCell[];
}

/** Porta ou janela de um comodo. */
export interface Aperture {
    id: string;
    type: 'door' | 'window';
    state: string;
    health: number;
}

/** Comodo de uma construcao. */
export interface Room {
    id: string;
    name: string;
    type: string;
    dimensions: { width: number; length: number };
    apertures: Aperture[];
}

/** Construcao explorada pelo jogador. */
export interface Building {
    id: string;
    type: string;
    rooms: Room[];
    overall_integrity: number;
}

/** Estado global do jogo e as acoes que o alteram. */
interface GameState {
    world: WorldMap | null;
    selectedBuilding: Building | null;
    isLoading: boolean;
    error: string | null;
    generateWorld: () => Promise<void>;
    fetchWorldState: () => Promise<void>;
    fetchBuilding: (type: string) => Promise<void>;
    closeBuilding: () => void;
}

/**
 * Converte um erro de requisicao em mensagem legivel.
 *
 * @param err Erro capturado.
 * @return Mensagem para exibir ao jogador.
 */
const describeError = (err: unknown): string => {
    if (isAxiosError(err)) {
        if (err.response) {
            return `Server Error: ${err.response.status} ${err.response.statusText}`;
        }
        if (err.request) {
            return 'Network Error: Unreachable (Check Backend)';
        }
    }
    return `Error: ${err instanceof Error ? err.message : String(err)}`;
};

/** Store global do jogo. */
export const useGameStore = create<GameState>((set) => ({
    world: null,
    selectedBuilding: null,
    isLoading: false,
    error: null,

    generateWorld: async () => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.post<WorldMap>('/api/world/generate');
            set({ world: response.data, isLoading: false });
        } catch (err) {
            console.error('Generate World Error:', err);
            set({ error: describeError(err), isLoading: false });
        }
    },

    fetchWorldState: async () => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.get<WorldMap>('/api/world/state');
            set({ world: response.data, isLoading: false });
        } catch (err) {
            console.error(err);
            set({ error: 'Failed to fetch world state', isLoading: false });
        }
    },

    fetchBuilding: async (type: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.post<Building>(`/api/building/generate/${type}`);
            set({ selectedBuilding: response.data, isLoading: false });
        } catch (err) {
            console.error(err);
            set({ error: 'Failed to enter building', isLoading: false });
        }
    },

    closeBuilding: () => set({ selectedBuilding: null }),
}));
