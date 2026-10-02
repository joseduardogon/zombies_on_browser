"""Modelos do mapa do mundo."""

from enum import Enum

from pydantic import BaseModel


class Coordinates(BaseModel):
    """Posicao em uma grade 2D.

    Attributes:
        x: Coluna.
        y: Linha.
    """

    x: int
    y: int


class SectorType(str, Enum):
    """Tipos de setor de uma celula do mapa."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    FOREST = "forest"
    ROAD = "road"


class WorldCell(BaseModel):
    """Celula do mapa do mundo.

    Attributes:
        coordinates: Posicao da celula.
        sector_type: Tipo de setor.
        is_explored: Se a celula ja foi explorada.
        building_id: Construcao associada, se houver.
    """

    coordinates: Coordinates
    sector_type: SectorType
    is_explored: bool = False
    building_id: str | None = None


class WorldMap(BaseModel):
    """Mapa completo do mundo.

    Attributes:
        width: Largura em celulas.
        height: Altura em celulas.
        cells: Celulas do mapa em ordem de linha.
    """

    width: int
    height: int
    cells: list[WorldCell]
