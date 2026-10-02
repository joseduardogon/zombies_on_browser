import { useEffect } from 'react';
import { useGameStore } from '../store/gameStore';

/** Duracao real, em milissegundos, de uma hora de jogo na velocidade 1x. */
export const BASE_TICK_MS = 1500;

/**
 * Avanca o relogio do jogo em tempo real conforme a velocidade escolhida.
 *
 * O servidor e quem decide o que acontece em cada hora: o hook apenas pede
 * um tick por intervalo. Nada e disparado com o jogo pausado ou encerrado.
 */
export function useGameClock(): void {
    const speed = useGameStore((s) => s.speed);
    const status = useGameStore((s) => s.game?.status);
    const tick = useGameStore((s) => s.tick);

    useEffect(() => {
        if (speed === 0 || status !== 'playing') return;
        const timer = window.setInterval(() => {
            void tick(1);
        }, BASE_TICK_MS / speed);
        return () => window.clearInterval(timer);
    }, [speed, status, tick]);
}
