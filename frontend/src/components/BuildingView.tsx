import { useGameStore } from '../store/gameStore';

/**
 * Painel de planta da construcao selecionada.
 *
 * Nao renderiza nada enquanto nenhuma construcao esta selecionada.
 */
export const BuildingView = () => {
    const { selectedBuilding, closeBuilding } = useGameStore();

    if (!selectedBuilding) return null;

    return (
        <div className="absolute inset-0 bg-black/90 flex flex-col items-center justify-center z-50 p-8">
            <div className="bg-gray-800 border-2 border-green-500/50 p-6 rounded max-w-4xl w-full h-full overflow-auto relative">
                <button
                    onClick={closeBuilding}
                    className="absolute top-4 right-4 text-red-500 hover:text-red-400 border border-red-500 px-3 py-1"
                >
                    EXIT VIEW
                </button>

                <h2 className="text-2xl text-green-500 font-bold mb-6">
                    BLUEPRINT: {selectedBuilding.type.toUpperCase()} // ID: {selectedBuilding.id.slice(0, 8)}
                </h2>

                <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                    {selectedBuilding.rooms.map(room => (
                        <div key={room.id} className="border border-gray-600 bg-gray-900/50 p-4 relative">
                            <h3 className="text-lg text-white font-semibold border-b border-gray-700 pb-2 mb-2">
                                {room.name}
                            </h3>
                            <p className="text-xs text-gray-400 mb-2">
                                {room.dimensions.width}x{room.dimensions.length}m // TYPE: {room.type}
                            </p>

                            <div className="space-y-2">
                                {room.apertures.map(ap => (
                                    <div key={ap.id} className={`text-xs px-2 py-1 border ${ap.type === 'door' ? 'border-blue-500 text-blue-400' : 'border-yellow-500 text-yellow-400'
                                        }`}>
                                        [{ap.type.toUpperCase()}] {ap.state.toUpperCase()}
                                        <span className="ml-2 text-gray-500">HP: {ap.health}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
