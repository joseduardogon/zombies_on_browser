/** Tipo de setor de uma celula do mapa. */
export type SectorType = 'residential' | 'commercial' | 'industrial' | 'forest' | 'road';

/** Fase da partida. */
export type GameStatus = 'setup' | 'playing' | 'won' | 'lost';

/** Funcao de um sobrevivente. */
export type SurvivorRole = 'leader' | 'scavenger' | 'builder' | 'guard' | 'idle';

/** Situacao de um sobrevivente. */
export type SurvivorStatus = 'home' | 'away' | 'dead';

/** Estado de uma abertura. */
export type ApertureState = 'open' | 'closed' | 'barricaded' | 'broken';

/** Severidade de uma entrada do diario. */
export type LogKind = 'info' | 'success' | 'warning' | 'danger';

/** Nomes dos recursos do abrigo. */
export const RESOURCE_KEYS = ['food', 'water', 'wood', 'scrap', 'medicine', 'ammo'] as const;

/** Nome de um recurso. */
export type ResourceKey = (typeof RESOURCE_KEYS)[number];

/** Estoque de recursos. */
export type Resources = Record<ResourceKey, number>;

/** Posicao em uma grade 2D. */
export interface Coordinates {
    x: number;
    y: number;
}

/** Celula do mapa. */
export interface WorldCell {
    coordinates: Coordinates;
    sector_type: SectorType;
    is_explored: boolean;
    building_id: string | null;
}

/** Mapa da cidade. */
export interface WorldMap {
    width: number;
    height: number;
    cells: WorldCell[];
}

/** Porta ou janela de um comodo. */
export interface Aperture {
    id: string;
    type: 'door' | 'window';
    state: ApertureState;
    health: number;
}

/** Comodo de uma construcao. */
export interface Room {
    id: string;
    name: string;
    type: string;
    dimensions: { width: number; length: number };
    apertures: Aperture[];
    insulation: number;
    security: number;
}

/** Construcao explorada ou habitada. */
export interface Building {
    id: string;
    type: string;
    rooms: Room[];
    overall_integrity: number;
    loot: Resources;
    searched: boolean;
}

/** Necessidades de um sobrevivente, de 0 a 100. */
export interface SurvivorNeeds {
    hunger: number;
    thirst: number;
    fatigue: number;
    morale: number;
    health: number;
}

/** Habilidades de um sobrevivente. */
export interface SurvivorSkills {
    construction: number;
    combat: number;
    scavenging: number;
    medicine: number;
}

/** Sobrevivente do grupo. */
export interface Survivor {
    id: string;
    name: string;
    role: SurvivorRole;
    status: SurvivorStatus;
    needs: SurvivorNeeds;
    skills: SurvivorSkills;
    current_location: Coordinates | null;
}

/** Relogio do jogo. */
export interface Clock {
    day: number;
    hour: number;
    total_hours: number;
    phase: 'day' | 'night';
}

/** Expedicao em andamento. */
export interface Expedition {
    id: string;
    survivor_id: string;
    building_id: string;
    cell: Coordinates;
    ticks_total: number;
    ticks_remaining: number;
}

/** Cerco zumbi da noite atual. */
export interface Siege {
    wave_size: number;
    arrived: number;
    at_gate: number;
    killed: number;
}

/** Entrada do diario de eventos. */
export interface LogEntry {
    day: number;
    hour: number;
    kind: LogKind;
    message: string;
}

/** Visao completa da partida devolvida pela API. */
export interface GameView {
    id: string;
    seed: number;
    status: GameStatus;
    clock: Clock;
    target_day: number;
    world: WorldMap;
    survivors: Survivor[];
    resources: Resources;
    base_building: Building | null;
    base_cell: Coordinates | null;
    expeditions: Expedition[];
    siege: Siege;
    log: LogEntry[];
    total_zombies_killed: number;
}

/** Resumo de um jogo salvo. */
export interface SaveInfo {
    slot: string;
    updated_at: string;
    day: number;
    status: GameStatus;
}
