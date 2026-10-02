/** Propriedades da barra de progresso. */
interface BarProps {
    label: string;
    value: number;
    max?: number;
    color: string;
}

/**
 * Barra horizontal rotulada, usada para necessidades e durabilidade.
 *
 * @param props Rotulo, valor atual, maximo e classe de cor do preenchimento.
 */
export const Bar = ({ label, value, max = 100, color }: BarProps) => {
    const percent = Math.max(0, Math.min(100, (value / max) * 100));
    return (
        <div className="flex items-center gap-2 text-[10px] uppercase text-gray-400">
            <span className="w-14 shrink-0">{label}</span>
            <div className="h-1.5 flex-1 bg-gray-700 rounded overflow-hidden">
                <div className={`h-full ${color}`} style={{ width: `${percent}%` }} />
            </div>
            <span className="w-7 text-right tabular-nums">{Math.round(value)}</span>
        </div>
    );
};
