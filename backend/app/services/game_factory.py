"""Criacao de partidas e escolha do abrigo."""

import random
import uuid

from app.core import balance
from app.core.errors import GameError
from app.models.game import GameState, GameStatus, LogKind
from app.models.resources import Resources
from app.models.survivor import SurvivorRole, SurvivorSkills
from app.models.world import SectorType
from app.services.building_service import get_or_create_building, recompute_integrity
from app.services.survivor_service import create_survivor
from app.services.world_generator import generate_world

SHELTER_SECTORS = (SectorType.RESIDENTIAL, SectorType.COMMERCIAL, SectorType.INDUSTRIAL)


def new_game(width: int, height: int, seed: int | None = None) -> GameState:
    """Cria uma partida nova, ainda sem abrigo escolhido.

    Args:
        width: Largura do mapa em celulas.
        height: Altura do mapa em celulas.
        seed: Semente da partida. Se omitida, e sorteada.

    Returns:
        A partida em fase de preparacao.
    """
    if seed is None:
        seed = random.SystemRandom().randrange(1, 2**31)
    world = generate_world(width, height, random.Random(f"{seed}:world"))
    state = GameState(id=str(uuid.uuid4()), seed=seed, world=world)
    state.add_log(LogKind.INFO, "Choose a building to serve as your shelter.")
    return state


def claim_base(state: GameState, building_id: str) -> GameState:
    """Define o abrigo, cria os sobreviventes iniciais e inicia a partida.

    Args:
        state: Partida em fase de preparacao.
        building_id: Construcao escolhida como abrigo.

    Returns:
        A mesma partida, agora em andamento.

    Raises:
        GameError: Se a partida ja comecou ou o local nao serve de abrigo.
    """
    if state.status != GameStatus.SETUP:
        raise GameError("The shelter has already been chosen", 409)

    cell = state.cell_for_building(building_id)
    if cell.sector_type not in SHELTER_SECTORS:
        raise GameError("This location cannot serve as a shelter")

    building = get_or_create_building(state, building_id)
    building.searched = True
    building.loot = Resources()
    building.survivor_present = False
    recompute_integrity(building)
    cell.is_explored = True

    state.base_building_id = building_id
    state.base_cell = cell.coordinates
    state.resources = Resources(**balance.STARTING_RESOURCES)

    rng = state.rng("start")
    create_survivor(state, rng, SurvivorRole.LEADER, SurvivorSkills(
        construction=2, combat=2, scavenging=2, medicine=2))
    create_survivor(state, rng, SurvivorRole.GUARD, SurvivorSkills(
        construction=1, combat=3, scavenging=1, medicine=1))
    create_survivor(state, rng, SurvivorRole.SCAVENGER, SurvivorSkills(
        construction=1, combat=1, scavenging=3, medicine=1))

    state.status = GameStatus.PLAYING
    state.add_log(
        LogKind.SUCCESS,
        f"Shelter established in a {cell.sector_type.value} building. "
        f"Survive {balance.TARGET_DAY} days.",
    )
    return state
