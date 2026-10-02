"""Geracao procedural do mapa da cidade."""

import random

from app.core import balance
from app.core.errors import GameError
from app.models.world import Coordinates, SectorType, WorldCell, WorldMap


def building_id_for(x: int, y: int) -> str:
    """Monta o identificador estavel da construcao de uma celula.

    Args:
        x: Coluna da celula.
        y: Linha da celula.

    Returns:
        Identificador no formato "b-x-y".
    """
    return f"b-{x}-{y}"


def pick_sector(x: int, y: int, width: int, height: int, rng: random.Random) -> SectorType:
    """Define o tipo de setor de uma celula que nao e via.

    O centro da cidade e comercial, a periferia e floresta e a zona
    intermediaria e residencial. Fora da floresta, ha chance de a celula
    virar industrial.

    Args:
        x: Coluna da celula.
        y: Linha da celula.
        width: Largura do mapa em celulas.
        height: Altura do mapa em celulas.
        rng: Gerador aleatorio da partida.

    Returns:
        O tipo de setor escolhido.
    """
    dist_center_x = abs(x - width / 2)
    dist_center_y = abs(y - height / 2)

    if dist_center_x < width * 0.2 and dist_center_y < height * 0.2:
        sector = SectorType.COMMERCIAL
    elif dist_center_x > width * 0.38 or dist_center_y > height * 0.38:
        sector = SectorType.FOREST
    else:
        sector = SectorType.RESIDENTIAL

    if sector != SectorType.FOREST and rng.random() < balance.INDUSTRIAL_CHANCE:
        sector = SectorType.INDUSTRIAL
    return sector


def generate_world(width: int, height: int, rng: random.Random) -> WorldMap:
    """Gera o mapa da cidade.

    Vias formam uma grade e ja nascem exploradas. Todo lote recebe o
    identificador de uma construcao, gerada somente quando for visitada.

    Args:
        width: Largura do mapa em celulas.
        height: Altura do mapa em celulas.
        rng: Gerador aleatorio da partida.

    Returns:
        O mapa gerado.

    Raises:
        GameError: Se as dimensoes estiverem fora dos limites permitidos.
    """
    limits = range(balance.MIN_WORLD_SIZE, balance.MAX_WORLD_SIZE + 1)
    if width not in limits or height not in limits:
        raise GameError(
            f"World size must be between {balance.MIN_WORLD_SIZE} and "
            f"{balance.MAX_WORLD_SIZE}"
        )

    cells = []
    for y in range(height):
        for x in range(width):
            coordinates = Coordinates(x=x, y=y)
            if x % balance.ROAD_SPACING == 0 or y % balance.ROAD_SPACING == 0:
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
                        sector_type=pick_sector(x, y, width, height, rng),
                        building_id=building_id_for(x, y),
                    )
                )
    return WorldMap(width=width, height=height, cells=cells)
