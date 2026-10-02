"""Acesso as construcoes de uma partida."""

import random

from app.core import balance
from app.models.building import Aperture, ApertureState, Building, Room
from app.models.game import GameState
from app.services.building_generator import BuildingGenerator


def get_or_create_building(state: GameState, building_id: str) -> Building:
    """Retorna a construcao, gerando-a na primeira visita.

    A geracao usa uma semente derivada da partida e do identificador, entao
    a mesma construcao e sempre igual, independente da ordem das visitas.

    Args:
        state: Estado da partida.
        building_id: Identificador da construcao.

    Returns:
        A construcao, nova ou ja existente.

    Raises:
        GameError: Se nenhuma celula do mapa tiver esse identificador.
    """
    if building_id in state.buildings:
        return state.buildings[building_id]

    cell = state.cell_for_building(building_id)
    rng = random.Random(f"{state.seed}:building:{building_id}")
    building = BuildingGenerator.generate(cell.sector_type.value, building_id, rng)
    state.buildings[building_id] = building
    return building


def find_aperture(building: Building, aperture_id: str) -> tuple[Room, Aperture] | None:
    """Procura uma abertura em uma construcao.

    Args:
        building: Construcao a pesquisar.
        aperture_id: Identificador da abertura.

    Returns:
        O par (comodo, abertura), ou None se nao existir.
    """
    for room in building.rooms:
        for aperture in room.apertures:
            if aperture.id == aperture_id:
                return room, aperture
    return None


def recompute_integrity(building: Building) -> None:
    """Recalcula a integridade geral a partir da saude das aberturas.

    Args:
        building: Construcao a atualizar.
    """
    apertures = [a for room in building.rooms for a in room.apertures]
    if not apertures:
        building.overall_integrity = 0
        return
    ratios = [
        0.0 if a.state == ApertureState.BROKEN else min(a.health, balance.FORTIFIED_HEALTH)
        / balance.FORTIFIED_HEALTH
        for a in apertures
    ]
    building.overall_integrity = round(100 * sum(ratios) / len(ratios))
