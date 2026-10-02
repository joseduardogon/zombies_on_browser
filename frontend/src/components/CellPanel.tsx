import { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import { RESOURCE_KEYS } from '../types/game';

/** Celulas percorridas por hora; espelha `TILES_PER_HOUR` do backend. */
const TILES_PER_HOUR = 3;

/** Horas de busca no local; espelha `SEARCH_HOURS` do backend. */
const SEARCH_HOURS = 1;

/** Saude minima para sair em expedicao; espelha `MIN_EXPEDITION_HEALTH`. */
const MIN_EXPEDITION_HEALTH = 25;

/**
 * Painel da celula selecionada: o que se sabe do local e as acoes possiveis.
 *
 * Na fase de preparacao oferece a escolha do abrigo; durante a partida,
 * permite enviar um sobrevivente em expedicao.
 */
export const CellPanel = () => {
    const { game, selectedCell, selectedBuilding, claimBase, sendExpedition, busy } = useGameStore();
    const [chosen, setChosen] = useState('');
    if (!game) return null;

    if (!selectedCell || !selectedCell.building_id) {
        return (
            <p className="text-sm text-gray-500">
                {game.status === 'setup'
                    ? 'Click a house, shop or factory and make it your shelter.'
                    : 'Click a building on the map to inspect it.'}
            </p>
        );
    }

    const { x, y } = selectedCell.coordinates;
    const isBase = game.base_building?.id === selectedCell.building_id;
    const canBeShelter = selectedCell.sector_type !== 'forest';
    const candidates = game.survivors.filter(
        (s) => s.status === 'home' && s.needs.health >= MIN_EXPEDITION_HEALTH,
    );
    const survivorId = candidates.some((s) => s.id === chosen) ? chosen : candidates[0]?.id ?? '';
    const underway = game.expeditions.find((e) => e.building_id === selectedCell.building_id);

    let eta = 0;
    if (game.base_cell) {
        const distance = Math.abs(game.base_cell.x - x) + Math.abs(game.base_cell.y - y);
        eta = 2 * Math.max(1, Math.ceil(distance / TILES_PER_HOUR)) + SEARCH_HOURS;
    }

    return (
        <div className="space-y-3 text-sm">
            <div>
                <h3 className="text-lg font-bold uppercase text-green-500">{selectedCell.sector_type}</h3>
                <p className="text-xs text-gray-400">
                    Sector ({x}, {y}) - {selectedCell.is_explored ? 'explored' : 'unexplored'}
                </p>
            </div>

            {selectedBuilding && (
                <div className="space-y-2">
                    <p className="text-xs text-gray-400">
                        {selectedBuilding.rooms.length} rooms -{' '}
                        {selectedBuilding.rooms.reduce((n, r) => n + r.apertures.length, 0)} openings
                    </p>
                    {selectedBuilding.searched && (
                        <p className="text-xs text-gray-300">
                            Left to loot:{' '}
                            {RESOURCE_KEYS.filter((k) => selectedBuilding.loot[k] > 0)
                                .map((k) => `${k} ${selectedBuilding.loot[k]}`)
                                .join(', ') || 'nothing'}
                        </p>
                    )}
                </div>
            )}

            {game.status === 'setup' && canBeShelter && (
                <button
                    disabled={busy}
                    onClick={() => void claimBase(selectedCell.building_id!)}
                    className="w-full py-2 border border-sky-400 text-sky-400 hover:bg-sky-400 hover:text-black uppercase tracking-wider"
                >
                    Make this my shelter
                </button>
            )}
            {game.status === 'setup' && !canBeShelter && (
                <p className="text-xs text-red-400">A forest clearing cannot be a shelter.</p>
            )}

            {game.status === 'playing' && isBase && (
                <p className="text-xs text-sky-400">This is your shelter. Manage it in the Shelter tab.</p>
            )}

            {game.status === 'playing' && !isBase && (
                <div className="space-y-2">
                    {underway ? (
                        <p className="text-xs text-orange-400">
                            {game.survivors.find((s) => s.id === underway.survivor_id)?.name} is on the way
                            ({underway.ticks_remaining}h left).
                        </p>
                    ) : (
                        <>
                            <select
                                value={survivorId}
                                onChange={(e) => setChosen(e.target.value)}
                                className="w-full bg-gray-800 border border-gray-600 px-2 py-1 text-xs"
                            >
                                {candidates.map((s) => (
                                    <option key={s.id} value={s.id}>
                                        {s.name} ({s.role}, scavenging {s.skills.scavenging})
                                    </option>
                                ))}
                            </select>
                            <button
                                disabled={busy || !survivorId}
                                onClick={() => void sendExpedition(survivorId, selectedCell.building_id!)}
                                className="w-full py-2 border border-orange-400 text-orange-400 hover:bg-orange-400 hover:text-black uppercase tracking-wider disabled:opacity-40"
                            >
                                Scavenge here ({eta}h round trip)
                            </button>
                            {candidates.length === 0 && (
                                <p className="text-xs text-gray-500">Nobody is fit to leave the shelter.</p>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};
