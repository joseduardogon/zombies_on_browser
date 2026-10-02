import { memo, useCallback, useRef, useState } from 'react';
import type { PointerEvent as ReactPointerEvent, WheelEvent } from 'react';
import { useGameStore } from '../store/gameStore';
import type { WorldCell } from '../types/game';
import '../city-3d.css';

const MIN_ZOOM = 0.4;
const MAX_ZOOM = 2.5;
const DRAG_THRESHOLD = 5;

/** Propriedades de uma celula do mapa. */
interface MapCellProps {
    cell: WorldCell;
    isBase: boolean;
    isSelected: boolean;
    isTarget: boolean;
    onSelect: (cell: WorldCell) => void;
}

/**
 * Compara as propriedades de uma celula para evitar redesenhos inuteis.
 *
 * @param prev Propriedades anteriores.
 * @param next Propriedades novas.
 * @return True se o desenho resultante seria identico.
 */
const sameCell = (prev: MapCellProps, next: MapCellProps): boolean =>
    prev.cell.coordinates.x === next.cell.coordinates.x &&
    prev.cell.coordinates.y === next.cell.coordinates.y &&
    prev.cell.is_explored === next.cell.is_explored &&
    prev.isBase === next.isBase &&
    prev.isSelected === next.isSelected &&
    prev.isTarget === next.isTarget &&
    prev.onSelect === next.onSelect;

/**
 * Uma celula 3D do mapa: via, floresta ou bloco de construcao.
 *
 * @param props Dados da celula e seus marcadores.
 */
const MapCell = memo(({ cell, isBase, isSelected, isTarget, onSelect }: MapCellProps) => {
    const { x, y } = cell.coordinates;
    const classes = [
        'city-cell',
        `type-${cell.sector_type}`,
        cell.is_explored && cell.sector_type !== 'road' ? 'is-explored' : '',
        isBase ? 'is-base' : '',
        isSelected ? 'is-selected' : '',
        isTarget ? 'is-target' : '',
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div
            className={classes}
            onClick={() => onSelect(cell)}
            title={`${cell.sector_type} (${x}, ${y})`}
        >
            {cell.sector_type === 'forest' ? (
                <div className="tree"></div>
            ) : cell.sector_type === 'road' ? (
                <>
                    <div className="block-3d">
                        <div className="face face-top"></div>
                    </div>
                    {(x + y) % 7 === 0 && <div className="car"></div>}
                </>
            ) : (
                <div className="block-3d">
                    <div className="face face-top"></div>
                    <div className="face face-side-1"></div>
                    <div className="face face-side-2"></div>
                </div>
            )}
        </div>
    );
}, sameCell);

/**
 * Mapa isometrico da cidade renderizado com transformacoes CSS 3D.
 *
 * Arrastar move a camera e a roda do mouse da zoom. Clicar em uma celula com
 * construcao a seleciona. O abrigo e os alvos de expedicao ficam destacados.
 */
export const CityMap3D = () => {
    const world = useGameStore((s) => s.game?.world);
    const baseCell = useGameStore((s) => s.game?.base_cell);
    const expeditions = useGameStore((s) => s.game?.expeditions);
    const selectedCell = useGameStore((s) => s.selectedCell);
    const selectCell = useGameStore((s) => s.selectCell);

    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const [zoom, setZoom] = useState(1);
    const dragged = useRef(false);

    const handlePointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
        if (event.button !== 0) return;
        dragged.current = false;
        const startX = event.clientX;
        const startY = event.clientY;
        const origin = offset;

        const onMove = (move: PointerEvent) => {
            const dx = move.clientX - startX;
            const dy = move.clientY - startY;
            if (Math.hypot(dx, dy) > DRAG_THRESHOLD) dragged.current = true;
            if (dragged.current) setOffset({ x: origin.x + dx, y: origin.y + dy });
        };
        const onUp = () => {
            window.removeEventListener('pointermove', onMove);
            window.removeEventListener('pointerup', onUp);
        };
        window.addEventListener('pointermove', onMove);
        window.addEventListener('pointerup', onUp);
    };

    const handleWheel = (event: WheelEvent<HTMLDivElement>) => {
        const factor = event.deltaY < 0 ? 1.1 : 0.9;
        setZoom((z) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z * factor)));
    };

    const handleSelect = useCallback(
        (cell: WorldCell) => {
            if (dragged.current) return;
            void selectCell(cell.building_id ? cell : null);
        },
        [selectCell],
    );

    if (!world) return null;

    const targets = new Set(expeditions?.map((e) => e.building_id));

    return (
        <div
            className="viewport-3d"
            onPointerDown={handlePointerDown}
            onWheel={handleWheel}
        >
            <div
                className="city-plane grid gap-0"
                style={{
                    gridTemplateColumns: `repeat(${world.width}, 40px)`,
                    gridTemplateRows: `repeat(${world.height}, 40px)`,
                    transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom}) rotateX(60deg) rotateZ(-45deg)`,
                }}
            >
                {world.cells.map((cell) => (
                    <MapCell
                        key={`${cell.coordinates.x}-${cell.coordinates.y}`}
                        cell={cell}
                        isBase={
                            baseCell?.x === cell.coordinates.x && baseCell?.y === cell.coordinates.y
                        }
                        isSelected={
                            selectedCell?.coordinates.x === cell.coordinates.x &&
                            selectedCell?.coordinates.y === cell.coordinates.y
                        }
                        isTarget={cell.building_id !== null && targets.has(cell.building_id)}
                        onSelect={handleSelect}
                    />
                ))}
            </div>

            <div className="absolute bottom-3 left-3 z-10 pointer-events-none text-xs text-gray-400">
                Drag to pan - Scroll to zoom - Click a building to inspect
            </div>
        </div>
    );
};
