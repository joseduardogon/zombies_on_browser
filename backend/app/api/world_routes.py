"""Rotas de geracao e consulta do mapa do mundo."""

import random

from fastapi import APIRouter, HTTPException

from app.models.world import Coordinates, SectorType, WorldCell, WorldMap

router = APIRouter()

ROAD_SPACING = 4
INDUSTRIAL_CHANCE = 0.1

current_world: WorldMap | None = None


def _pick_sector(x: int, y: int, width: int, height: int) -> SectorType:
    """Define o tipo de setor de uma celula que nao e via.

    O centro da cidade e comercial, a periferia e floresta e a zona
    intermediaria e residencial. Fora da floresta, ha chance de a celula
    virar industrial.

    Args:
        x: Coluna da celula.
        y: Linha da celula.
        width: Largura do mapa em celulas.
        height: Altura do mapa em celulas.

    Returns:
        O tipo de setor escolhido.
    """
    dist_center_x = abs(x - width / 2)
    dist_center_y = abs(y - height / 2)

    if dist_center_x < width * 0.2 and dist_center_y < height * 0.2:
        sector = SectorType.COMMERCIAL
    elif dist_center_x > width * 0.45 or dist_center_y > height * 0.45:
        sector = SectorType.FOREST
    else:
        sector = SectorType.RESIDENTIAL

    if sector != SectorType.FOREST and random.random() < INDUSTRIAL_CHANCE:
        sector = SectorType.INDUSTRIAL
    return sector


@router.post("/generate", response_model=WorldMap)
def generate_world(width: int = 20, height: int = 20) -> WorldMap:
    """Gera um novo mapa e o armazena como mundo atual.

    Args:
        width: Largura do mapa em celulas.
        height: Altura do mapa em celulas.

    Returns:
        O mapa gerado.
    """
    global current_world

    cells = []
    for y in range(height):
        for x in range(width):
            coordinates = Coordinates(x=x, y=y)
            if x % ROAD_SPACING == 0 or y % ROAD_SPACING == 0:
                cells.append(
                    WorldCell(
                        coordinates=coordinates,
                        sector_type=SectorType.ROAD,
                        is_explored=True,
                    )
                )
            else:
                cells.append(
                    WorldCell(
                        coordinates=coordinates,
                        sector_type=_pick_sector(x, y, width, height),
                    )
                )

    current_world = WorldMap(width=width, height=height, cells=cells)
    return current_world


@router.get("/state", response_model=WorldMap)
def get_world_state() -> WorldMap:
    """Retorna o mundo atual.

    Returns:
        O mapa armazenado.

    Raises:
        HTTPException: Com status 404 se nenhum mundo foi gerado.
    """
    if current_world is None:
        raise HTTPException(status_code=404, detail="World not generated")
    return current_world
