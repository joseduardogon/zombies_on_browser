import { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import type { Speed } from '../store/gameStore';
import { RESOURCE_KEYS } from '../types/game';

const SPEEDS: { value: Speed; label: string }[] = [
    { value: 0, label: 'Pause' },
    { value: 1, label: '1x' },
    { value: 2, label: '2x' },
    { value: 4, label: '4x' },
];

const RESOURCE_COLORS: Record<(typeof RESOURCE_KEYS)[number], string> = {
    food: 'text-orange-400',
    water: 'text-sky-400',
    wood: 'text-amber-600',
    scrap: 'text-gray-300',
    medicine: 'text-pink-400',
    ammo: 'text-yellow-300',
};

/**
 * Barra superior: data e hora, controle de velocidade, recursos e salvamento.
 */
export const TopBar = () => {
    const { game, speed, setSpeed, tick, busy, saveGame, saves, loadGame, newGame } = useGameStore();
    const [menuOpen, setMenuOpen] = useState(false);
    if (!game) return null;

    const playing = game.status === 'playing';
    const hour = String(game.clock.hour).padStart(2, '0');
    const night = game.clock.phase === 'night';

    return (
        <header className="h-14 shrink-0 flex items-center gap-6 px-4 bg-gray-800 border-b border-gray-700 z-20 text-sm">
            <h1 className="font-bold tracking-wider text-green-500 whitespace-nowrap">
                COMMANDER INTERFACE // Z-CITY
            </h1>

            <div className="flex items-center gap-3 whitespace-nowrap">
                <span className="font-bold">
                    Day {game.clock.day}/{game.target_day}
                </span>
                <span className={night ? 'text-indigo-300' : 'text-yellow-300'}>
                    {hour}:00 {night ? 'NIGHT' : 'DAY'}
                </span>
            </div>

            {playing && (
                <div className="flex items-center gap-1">
                    {SPEEDS.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => setSpeed(option.value)}
                            className={`px-2 py-0.5 border text-xs ${
                                speed === option.value
                                    ? 'border-green-500 text-green-500'
                                    : 'border-gray-600 text-gray-400 hover:border-gray-400'
                            }`}
                        >
                            {option.label}
                        </button>
                    ))}
                    <button
                        disabled={busy}
                        onClick={() => void tick(6)}
                        className="ml-2 px-2 py-0.5 border border-gray-600 text-xs text-gray-300 hover:border-gray-400 disabled:opacity-50"
                    >
                        +6h
                    </button>
                </div>
            )}

            <div className="flex items-center gap-4 ml-auto">
                {game.status !== 'setup' &&
                    RESOURCE_KEYS.map((key) => (
                        <span key={key} className={`${RESOURCE_COLORS[key]} whitespace-nowrap`} title={key}>
                            {key} <b className="tabular-nums">{game.resources[key]}</b>
                        </span>
                    ))}
            </div>

            <div className="relative">
                <button
                    onClick={() => setMenuOpen((open) => !open)}
                    className="px-3 py-1 border border-gray-600 text-xs hover:border-green-500"
                >
                    Menu
                </button>
                {menuOpen && (
                    <div className="absolute right-0 top-9 w-56 bg-gray-900 border border-gray-600 p-2 space-y-1 z-50">
                        <button
                            onClick={() => {
                                void saveGame('manual');
                                setMenuOpen(false);
                            }}
                            className="w-full text-left px-2 py-1 hover:bg-gray-800"
                        >
                            Save game
                        </button>
                        <button
                            onClick={() => {
                                void newGame(game.world.width, game.world.height);
                                setMenuOpen(false);
                            }}
                            className="w-full text-left px-2 py-1 hover:bg-gray-800"
                        >
                            New game
                        </button>
                        {saves.map((save) => (
                            <button
                                key={save.slot}
                                onClick={() => {
                                    void loadGame(save.slot);
                                    setMenuOpen(false);
                                }}
                                className="w-full text-left px-2 py-1 text-gray-400 hover:bg-gray-800"
                            >
                                Load "{save.slot}" (day {save.day})
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </header>
    );
};
