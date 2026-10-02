import { useGameStore } from '../store/gameStore';
import '../city-3d.css';

/**
 * Mapa isometrico da cidade renderizado com transformacoes CSS 3D.
 *
 * Clicar em uma celula abre a planta da construcao do setor correspondente.
 */
export const CityMap3D = () => {
    const { world, fetchBuilding } = useGameStore();

    if (!world) return null;

    return (
        <div className="viewport-3d bg-gray-900">
            <div
                className="city-plane grid gap-0"
                style={{
                    gridTemplateColumns: `repeat(${world.width}, 40px)`,
                    gridTemplateRows: `repeat(${world.height}, 40px)`,
                }}
            >
                {world.cells.map((cell) => (
                    <div
                        key={`${cell.coordinates.x}-${cell.coordinates.y}`}
                        className={`city-cell type-${cell.sector_type}`}
                        onClick={() => fetchBuilding(cell.sector_type)}
                        title={`${cell.sector_type}`}
                    >
                        {cell.sector_type === 'forest' ? (
                            <div className="tree"></div>
                        ) : cell.sector_type === 'road' ? (
                            <>
                                <div className="block-3d">
                                    <div className="face face-top"></div>
                                </div>
                                {(cell.coordinates.x + cell.coordinates.y) % 7 === 0 && <div className="car"></div>}
                            </>
                        ) : (
                            <div className="block-3d">
                                <div className="face face-top"></div>
                                <div className="face face-side-1"></div>
                                <div className="face face-side-2"></div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <div className="absolute top-4 left-4 z-10 pointer-events-none">
                <h1 className="text-2xl font-bold text-white drop-shadow-md">Z-CITY VIEW 3D</h1>
                <p className="text-sm text-gray-300">Drag to Pan (Coming Soon) | Click Buildings to Inspect</p>
            </div>
        </div>
    );
};
