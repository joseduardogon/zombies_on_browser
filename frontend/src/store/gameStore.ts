import { create } from 'zustand';
import { ApiError, gameApi } from '../lib/gameApi';
import type {
    Building,
    GameView,
    SaveInfo,
    SurvivorRole,
    WorldCell,
} from '../types/game';

/** Velocidades do relogio: 0 pausa e os demais valores multiplicam o ritmo. */
export type Speed = 0 | 1 | 2 | 4;

/** Aviso temporario mostrado ao jogador. */
export interface Notice {
    kind: 'error' | 'info';
    message: string;
}

/** Estado global do jogo e as acoes que o alteram. */
interface GameStore {
    game: GameView | null;
    loaded: boolean;
    busy: boolean;
    fatalError: string | null;
    notice: Notice | null;
    speed: Speed;
    selectedCell: WorldCell | null;
    selectedBuilding: Building | null;
    saves: SaveInfo[];

    init: () => Promise<void>;
    newGame: (width: number, height: number, seed?: number) => Promise<void>;
    claimBase: (buildingId: string) => Promise<void>;
    tick: (hours: number) => Promise<void>;
    setSpeed: (speed: Speed) => void;
    selectCell: (cell: WorldCell | null) => Promise<void>;
    sendExpedition: (survivorId: string, buildingId: string) => Promise<void>;
    reinforce: (apertureId: string, survivorId: string) => Promise<void>;
    setRole: (survivorId: string, role: SurvivorRole) => Promise<void>;
    treat: (survivorId: string) => Promise<void>;
    refreshSaves: () => Promise<void>;
    saveGame: (slot: string) => Promise<void>;
    loadGame: (slot: string) => Promise<void>;
    dismissNotice: () => void;
}

/**
 * Converte uma falha em mensagem para o jogador.
 *
 * @param err Erro capturado.
 * @return O texto do erro.
 */
const messageOf = (err: unknown): string =>
    err instanceof Error ? err.message : String(err);

/** Store global do jogo. */
export const useGameStore = create<GameStore>((set, get) => {
    /**
     * Aplica uma nova visao da partida e mantem a selecao coerente.
     *
     * A celula selecionada e atualizada com os dados novos e, se ela acabou
     * de ser explorada, a construcao e buscada de novo para mostrar a pilhagem.
     *
     * @param game Nova visao da partida.
     */
    const applyGame = (game: GameView) => {
        const { selectedCell, selectedBuilding } = get();
        const fresh = selectedCell
            ? game.world.cells.find(
                  (c) =>
                      c.coordinates.x === selectedCell.coordinates.x &&
                      c.coordinates.y === selectedCell.coordinates.y,
              ) ?? null
            : null;
        set({
            game,
            selectedCell: fresh,
            speed: game.status === 'playing' ? get().speed : 0,
        });
        if (fresh?.building_id && selectedBuilding && !selectedBuilding.searched && fresh.is_explored) {
            void get().selectCell(fresh);
        }
    };

    /**
     * Executa uma acao que devolve a partida e trata os erros.
     *
     * Falhas de rede viram erro fatal; falhas de regra viram aviso.
     *
     * @param action Funcao que chama a API.
     * @return True se a acao teve sucesso.
     */
    const run = async (action: () => Promise<GameView>): Promise<boolean> => {
        set({ busy: true });
        try {
            applyGame(await action());
            set({ busy: false, fatalError: null });
            return true;
        } catch (err) {
            if (err instanceof ApiError && err.status === 0) {
                set({ busy: false, fatalError: err.message, speed: 0 });
            } else {
                set({ busy: false, notice: { kind: 'error', message: messageOf(err) } });
            }
            return false;
        }
    };

    return {
        game: null,
        loaded: false,
        busy: false,
        fatalError: null,
        notice: null,
        speed: 0,
        selectedCell: null,
        selectedBuilding: null,
        saves: [],

        init: async () => {
            try {
                set({ game: await gameApi.getGame(), fatalError: null });
            } catch (err) {
                if (err instanceof ApiError && err.status === 404) {
                    set({ game: null, fatalError: null });
                } else {
                    set({ fatalError: messageOf(err) });
                }
            }
            set({ loaded: true });
            await get().refreshSaves();
        },

        newGame: async (width, height, seed) => {
            set({ selectedCell: null, selectedBuilding: null, speed: 0 });
            await run(() => gameApi.newGame(width, height, seed));
        },

        claimBase: async (buildingId) => {
            await run(() => gameApi.claimBase(buildingId));
        },

        tick: async (hours) => {
            if (get().busy) return;
            await run(() => gameApi.tick(hours));
        },

        setSpeed: (speed) => set({ speed }),

        selectCell: async (cell) => {
            set({ selectedCell: cell, selectedBuilding: null });
            if (!cell?.building_id) return;
            try {
                const building = await gameApi.getBuilding(cell.building_id);
                if (get().selectedCell?.building_id === cell.building_id) {
                    set({ selectedBuilding: building });
                }
            } catch (err) {
                set({ notice: { kind: 'error', message: messageOf(err) } });
            }
        },

        sendExpedition: async (survivorId, buildingId) => {
            await run(() => gameApi.sendExpedition(survivorId, buildingId));
        },

        reinforce: async (apertureId, survivorId) => {
            await run(() => gameApi.reinforce(apertureId, survivorId));
        },

        setRole: async (survivorId, role) => {
            await run(() => gameApi.setRole(survivorId, role));
        },

        treat: async (survivorId) => {
            await run(() => gameApi.treat(survivorId));
        },

        refreshSaves: async () => {
            try {
                set({ saves: await gameApi.listSaves() });
            } catch {
                set({ saves: [] });
            }
        },

        saveGame: async (slot) => {
            try {
                set({
                    saves: await gameApi.save(slot),
                    notice: { kind: 'info', message: `Game saved to "${slot}".` },
                });
            } catch (err) {
                set({ notice: { kind: 'error', message: messageOf(err) } });
            }
        },

        loadGame: async (slot) => {
            set({ selectedCell: null, selectedBuilding: null, speed: 0 });
            if (await run(() => gameApi.load(slot))) {
                set({ notice: { kind: 'info', message: `Loaded "${slot}".` } });
            }
        },

        dismissNotice: () => set({ notice: null }),
    };
});
