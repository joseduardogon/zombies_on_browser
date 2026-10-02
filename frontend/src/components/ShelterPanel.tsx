import { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import { Bar } from './ui/Bar';

/** Madeira por reforco; espelha `BARRICADE_WOOD_COST` do backend. */
const WOOD_COST = 2;

/** Saude maxima de uma abertura; espelha `APERTURE_HEALTH_CAP`. */
const HEALTH_CAP = 300;

const STATE_STYLE: Record<string, string> = {
    open: 'text-yellow-400',
    closed: 'text-gray-300',
    barricaded: 'text-green-400',
    broken: 'text-red-500',
};

/**
 * Painel do abrigo: integridade, comodos e reforco das aberturas.
 */
export const ShelterPanel = () => {
    const { game, reinforce, busy } = useGameStore();
    const [chosen, setChosen] = useState('');
    const base = game?.base_building;
    if (!game || !base) {
        return <p className="text-sm text-gray-500">No shelter yet.</p>;
    }

    const workers = game.survivors.filter((s) => s.status === 'home');
    const workerId = workers.some((s) => s.id === chosen) ? chosen : workers[0]?.id ?? '';
    const canAfford = game.resources.wood >= WOOD_COST;

    return (
        <div className="space-y-4 text-sm">
            <div className="space-y-1">
                <h3 className="text-lg font-bold uppercase text-sky-400">Shelter ({base.type})</h3>
                <Bar label="Integrity" value={base.overall_integrity} color="bg-sky-500" />
            </div>

            <label className="flex items-center gap-2 text-xs text-gray-400">
                Worker
                <select
                    value={workerId}
                    onChange={(e) => setChosen(e.target.value)}
                    className="flex-1 bg-gray-800 border border-gray-600 px-2 py-1"
                >
                    {workers.map((s) => (
                        <option key={s.id} value={s.id}>
                            {s.name} (construction {s.skills.construction})
                        </option>
                    ))}
                </select>
            </label>

            {base.rooms.map((room) => (
                <div key={room.id} className="border border-gray-700 bg-gray-900/60 p-3 space-y-2">
                    <div className="flex justify-between">
                        <span className="font-semibold">{room.name}</span>
                        <span className="text-xs text-gray-500">
                            {room.dimensions.width}x{room.dimensions.length}m
                        </span>
                    </div>
                    {room.apertures.length === 0 && (
                        <p className="text-xs text-gray-500">No openings.</p>
                    )}
                    {room.apertures.map((aperture) => (
                        <div key={aperture.id} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                                <span className="uppercase">
                                    {aperture.type}{' '}
                                    <span className={STATE_STYLE[aperture.state]}>{aperture.state}</span>
                                </span>
                                <button
                                    disabled={
                                        busy ||
                                        !workerId ||
                                        !canAfford ||
                                        aperture.health >= HEALTH_CAP
                                    }
                                    onClick={() => void reinforce(aperture.id, workerId)}
                                    className="px-2 py-0.5 border border-amber-600 text-amber-500 hover:bg-amber-600 hover:text-black disabled:opacity-40"
                                >
                                    {aperture.state === 'broken' ? 'Repair' : 'Reinforce'} ({WOOD_COST} wood)
                                </button>
                            </div>
                            <Bar
                                label="HP"
                                value={aperture.health}
                                max={HEALTH_CAP}
                                color={aperture.state === 'broken' ? 'bg-red-600' : 'bg-green-500'}
                            />
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
};
