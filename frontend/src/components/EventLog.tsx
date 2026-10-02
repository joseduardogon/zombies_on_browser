import { useGameStore } from '../store/gameStore';
import type { LogKind } from '../types/game';

const KIND_STYLE: Record<LogKind, string> = {
    info: 'text-gray-300',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    danger: 'text-red-400',
};

/**
 * Diario de eventos da partida, do mais recente ao mais antigo.
 */
export const EventLog = () => {
    const log = useGameStore((s) => s.game?.log ?? []);

    return (
        <ul className="space-y-1 text-xs">
            {[...log].reverse().map((entry, index) => (
                <li key={`${log.length - index}`} className={KIND_STYLE[entry.kind]}>
                    <span className="text-gray-500">
                        D{entry.day} {String(entry.hour).padStart(2, '0')}h
                    </span>{' '}
                    {entry.message}
                </li>
            ))}
        </ul>
    );
};
