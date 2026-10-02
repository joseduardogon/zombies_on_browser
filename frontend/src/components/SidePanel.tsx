import { useState } from 'react';
import { CellPanel } from './CellPanel';
import { EventLog } from './EventLog';
import { ShelterPanel } from './ShelterPanel';

const TABS = [
    { id: 'location', label: 'Location' },
    { id: 'shelter', label: 'Shelter' },
    { id: 'journal', label: 'Journal' },
] as const;

type TabId = (typeof TABS)[number]['id'];

/**
 * Coluna da direita, com abas para local, abrigo e diario.
 */
export const SidePanel = () => {
    const [tab, setTab] = useState<TabId>('location');

    return (
        <aside className="w-80 shrink-0 flex flex-col bg-gray-800/90 border-l border-gray-700 z-10">
            <nav className="flex border-b border-gray-700">
                {TABS.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setTab(item.id)}
                        className={`flex-1 py-2 text-xs uppercase tracking-wider ${
                            tab === item.id
                                ? 'text-green-500 border-b-2 border-green-500'
                                : 'text-gray-500 hover:text-gray-300'
                        }`}
                    >
                        {item.label}
                    </button>
                ))}
            </nav>
            <div className="flex-1 overflow-y-auto p-3">
                {tab === 'location' && <CellPanel />}
                {tab === 'shelter' && <ShelterPanel />}
                {tab === 'journal' && <EventLog />}
            </div>
        </aside>
    );
};
