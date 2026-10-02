import { useGameStore } from '../store/gameStore';
import type { Survivor, SurvivorRole } from '../types/game';
import { Bar } from './ui/Bar';

const ROLES: SurvivorRole[] = ['leader', 'scavenger', 'builder', 'guard', 'idle'];

const STATUS_STYLE: Record<Survivor['status'], string> = {
    home: 'text-green-400',
    away: 'text-orange-400',
    dead: 'text-red-500',
};

/**
 * Cartao de um sobrevivente com necessidades, habilidades e acoes.
 *
 * @param props O sobrevivente exibido.
 */
const SurvivorCard = ({ survivor }: { survivor: Survivor }) => {
    const { setRole, treat, busy } = useGameStore();
    const medicine = useGameStore((s) => s.game?.resources.medicine ?? 0);
    const dead = survivor.status === 'dead';
    const { needs, skills } = survivor;

    return (
        <div className={`border border-gray-700 bg-gray-900/60 p-3 space-y-2 ${dead ? 'opacity-40' : ''}`}>
            <div className="flex items-center justify-between">
                <span className="font-semibold">{survivor.name}</span>
                <span className={`text-[10px] uppercase ${STATUS_STYLE[survivor.status]}`}>
                    {survivor.status}
                </span>
            </div>

            {!dead && (
                <>
                    <div className="space-y-1">
                        <Bar label="Health" value={needs.health} color="bg-red-500" />
                        <Bar label="Hunger" value={needs.hunger} color="bg-orange-500" />
                        <Bar label="Thirst" value={needs.thirst} color="bg-sky-500" />
                        <Bar label="Energy" value={needs.fatigue} color="bg-yellow-400" />
                        <Bar label="Morale" value={needs.morale} color="bg-purple-400" />
                    </div>

                    <div className="flex gap-3 text-[10px] text-gray-400 uppercase">
                        <span>BLD {skills.construction}</span>
                        <span>CMB {skills.combat}</span>
                        <span>SCV {skills.scavenging}</span>
                        <span>MED {skills.medicine}</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <select
                            value={survivor.role}
                            disabled={busy}
                            onChange={(e) => void setRole(survivor.id, e.target.value as SurvivorRole)}
                            className="flex-1 bg-gray-800 border border-gray-600 px-1 py-0.5 text-xs uppercase"
                        >
                            {ROLES.map((role) => (
                                <option key={role} value={role}>
                                    {role}
                                </option>
                            ))}
                        </select>
                        {survivor.status === 'home' && needs.health < 100 && medicine > 0 && (
                            <button
                                disabled={busy}
                                onClick={() => void treat(survivor.id)}
                                className="px-2 py-0.5 text-xs border border-pink-400 text-pink-400 hover:bg-pink-400 hover:text-black"
                            >
                                Treat
                            </button>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};

/**
 * Lista todos os sobreviventes do grupo, vivos primeiro.
 */
export const SurvivorsPanel = () => {
    const survivors = useGameStore((s) => s.game?.survivors ?? []);
    const ordered = [...survivors].sort(
        (a, b) => Number(a.status === 'dead') - Number(b.status === 'dead'),
    );

    return (
        <aside className="w-72 shrink-0 overflow-y-auto bg-gray-800/90 border-r border-gray-700 p-3 space-y-3 z-10">
            <h2 className="text-xs uppercase tracking-widest text-gray-500">
                Survivors ({survivors.filter((s) => s.status !== 'dead').length})
            </h2>
            {ordered.map((survivor) => (
                <SurvivorCard key={survivor.id} survivor={survivor} />
            ))}
            {survivors.length === 0 && (
                <p className="text-sm text-gray-500">No survivors yet. Choose a shelter first.</p>
            )}
        </aside>
    );
};
