import { useState } from 'react';
import { useGameStore } from '../store/gameStore';

/**
 * Tela inicial: nova partida ou retomada de um jogo salvo.
 */
export const StartScreen = () => {
    const { newGame, loadGame, saves, busy } = useGameStore();
    const [size, setSize] = useState(20);
    const [seed, setSeed] = useState('');

    const start = () => {
        const parsed = seed.trim() === '' ? undefined : Number(seed);
        void newGame(size, size, Number.isFinite(parsed) ? parsed : undefined);
    };

    return (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-black/85">
            <div className="w-[28rem] max-w-full border border-green-500/40 bg-gray-900 p-8 rounded space-y-6">
                <div>
                    <h2 className="text-3xl font-bold tracking-widest text-green-500">Z-CITY</h2>
                    <p className="text-sm text-gray-400 mt-2">
                        The city has fallen. Pick a shelter, gather supplies and hold out until
                        help arrives. Zombies attack every night.
                    </p>
                </div>

                <div className="space-y-3 text-sm">
                    <label className="flex items-center justify-between gap-4">
                        <span className="text-gray-400">Map size</span>
                        <select
                            value={size}
                            onChange={(e) => setSize(Number(e.target.value))}
                            className="bg-gray-800 border border-gray-600 px-2 py-1"
                        >
                            <option value={12}>Small (12x12)</option>
                            <option value={20}>Medium (20x20)</option>
                            <option value={28}>Large (28x28)</option>
                        </select>
                    </label>
                    <label className="flex items-center justify-between gap-4">
                        <span className="text-gray-400">Seed (optional)</span>
                        <input
                            value={seed}
                            onChange={(e) => setSeed(e.target.value.replace(/\D/g, ''))}
                            placeholder="random"
                            className="bg-gray-800 border border-gray-600 px-2 py-1 w-32"
                        />
                    </label>
                </div>

                <button
                    disabled={busy}
                    onClick={start}
                    className="w-full py-2 border border-green-500 text-green-500 hover:bg-green-500 hover:text-black transition-colors uppercase tracking-wider disabled:opacity-50"
                >
                    New game
                </button>

                {saves.length > 0 && (
                    <div className="space-y-2">
                        <h3 className="text-xs uppercase text-gray-500">Saved games</h3>
                        {saves.map((save) => (
                            <button
                                key={save.slot}
                                disabled={busy}
                                onClick={() => void loadGame(save.slot)}
                                className="w-full flex justify-between px-3 py-1.5 text-sm border border-gray-600 hover:border-green-500 text-gray-300"
                            >
                                <span>{save.slot}</span>
                                <span className="text-gray-500">
                                    day {save.day} - {save.status}
                                </span>
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
