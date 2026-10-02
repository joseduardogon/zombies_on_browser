"""Rotas de geracao e consulta de construcoes."""

import uuid
from typing import Callable

from fastapi import APIRouter, HTTPException

from app.models.building import Building
from app.services.building_generator import BuildingGenerator

router = APIRouter()

buildings: dict[str, Building] = {}

_GENERATORS: dict[str, Callable[[str], Building]] = {
    "residential": BuildingGenerator.generate_residential,
    "commercial": BuildingGenerator.generate_commercial,
    "industrial": BuildingGenerator.generate_industrial,
    "forest": BuildingGenerator.generate_forest,
}


@router.post("/generate/{type}", response_model=Building)
def generate_building(type: str) -> Building:
    """Gera e armazena uma nova construcao.

    Args:
        type: Tipo da construcao. Tipos desconhecidos geram uma residencia.

    Returns:
        A construcao gerada.
    """
    building_id = str(uuid.uuid4())
    generator = _GENERATORS.get(type, BuildingGenerator.generate_residential)
    building = generator(building_id)
    buildings[building_id] = building
    return building


@router.get("/{building_id}", response_model=Building)
def get_building(building_id: str) -> Building:
    """Busca uma construcao ja gerada.

    Args:
        building_id: Identificador da construcao.

    Returns:
        A construcao correspondente.

    Raises:
        HTTPException: Com status 404 se a construcao nao existir.
    """
    if building_id not in buildings:
        raise HTTPException(status_code=404, detail="Building not found")
    return buildings[building_id]
