import { useEffect } from 'react';
import { useGameStore } from '../store/gameStore';

/** Tempo, em milissegundos, que um aviso informativo permanece na tela. */
const NOTICE_MS = 4000;

/**
 * Faixa de alerta durante o cerco noturno, com o andamento da onda.
 * Some quando a partida termina.
 */
export const SiegeBanner = () => {
    const siege = useGameStore((s) => s.game?.siege);
    const status = useGameStore((s) => s.game?.status);
    if (!siege || siege.wave_size === 0 || status !== 'playing') return null;

    return (
        <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 px-4 py-2 bg-red-900/80 border border-red-500 text-red-200 text-xs uppercase tracking-wider pointer-events-none">
            Horde {siege.arrived}/{siege.wave_size} arrived - {siege.at_gate} at the gate -{' '}
            {siege.killed} killed
        </div>
    );
};

/**
 * Escurece o mapa durante a noite.
 */
export const NightTint = () => {
    const phase = useGameStore((s) => s.game?.clock.phase);
    if (phase !== 'night') return null;
    return <div className="absolute inset-0 z-10 bg-indigo-950/50 pointer-events-none" />;
};

/**
 * Aviso temporario no canto da tela. Erros ficam ate serem dispensados.
 */
export const NoticeToast = () => {
    const { notice, dismissNotice } = useGameStore();

    useEffect(() => {
        if (!notice || notice.kind === 'error') return;
        const timer = window.setTimeout(dismissNotice, NOTICE_MS);
        return () => window.clearTimeout(timer);
    }, [notice, dismissNotice]);

    if (!notice) return null;
    const style =
        notice.kind === 'error'
            ? 'border-red-500 text-red-300 bg-red-950'
            : 'border-green-500 text-green-300 bg-gray-900';

    return (
        <button
            onClick={dismissNotice}
            className={`absolute bottom-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 border text-sm ${style}`}
        >
            {notice.message}
        </button>
    );
};

/**
 * Tela de fim de jogo, com o balanco da partida.
 */
export const GameOverOverlay = () => {
    const { game, newGame } = useGameStore();
    if (!game || (game.status !== 'won' && game.status !== 'lost')) return null;

    const won = game.status === 'won';
    const alive = game.survivors.filter((s) => s.status !== 'dead').length;

    return (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-black/85">
            <div
                className={`w-96 p-8 border text-center space-y-4 bg-gray-900 ${
                    won ? 'border-green-500' : 'border-red-500'
                }`}
            >
                <h2 className={`text-3xl font-bold tracking-widest ${won ? 'text-green-500' : 'text-red-500'}`}>
                    {won ? 'RESCUED' : 'OVERRUN'}
                </h2>
                <p className="text-sm text-gray-400">
                    {won
                        ? `You held the shelter for ${game.target_day} days.`
                        : `The shelter fell on day ${game.clock.day}.`}
                </p>
                <ul className="text-sm text-gray-300 space-y-1">
                    <li>Survivors alive: {alive}</li>
                    <li>Zombies put down: {game.total_zombies_killed}</li>
                    <li>Hours survived: {game.clock.total_hours}</li>
                </ul>
                <button
                    onClick={() => void newGame(game.world.width, game.world.height)}
                    className="w-full py-2 border border-green-500 text-green-500 hover:bg-green-500 hover:text-black uppercase tracking-wider"
                >
                    New game
                </button>
            </div>
        </div>
    );
};
