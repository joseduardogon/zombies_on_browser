"""Expedicoes de coleta fora do abrigo."""

import math

from app.core import balance
from app.core.errors import GameError
from app.models.game import Expedition, GameState, LogKind
from app.models.resources import Resources
from app.models.survivor import Survivor, SurvivorRole, SurvivorStatus
from app.services.building_service import get_or_create_building
from app.services.survivor_service import (
    clamp,
    create_survivor,
    efficiency,
    kill_survivor,
    maybe_improve_skill,
)


def travel_hours(state: GameState, target_x: int, target_y: int) -> int:
    """Calcula as horas de viagem de ida ate uma celula.

    Args:
        state: Estado da partida.
        target_x: Coluna do destino.
        target_y: Linha do destino.

    Returns:
        Horas de ida, no minimo uma.
    """
    base = state.base_cell
    distance = abs(base.x - target_x) + abs(base.y - target_y)
    return max(1, math.ceil(distance / balance.TILES_PER_HOUR))


def start_expedition(state: GameState, survivor_id: str, building_id: str) -> Expedition:
    """Envia um sobrevivente a vasculhar uma construcao.

    A duracao e a ida, a busca e a volta. O sobrevivente fica ausente do
    abrigo ate retornar.

    Args:
        state: Estado da partida.
        survivor_id: Sobrevivente que vai.
        building_id: Construcao alvo.

    Returns:
        A expedicao criada.

    Raises:
        GameError: Se o sobrevivente nao puder sair, o alvo for o proprio
            abrigo ou a construcao nao existir.
    """
    state.require_playing()
    survivor = state.find_survivor(survivor_id)
    if survivor.status != SurvivorStatus.HOME:
        raise GameError(f"{survivor.name} is not at the shelter")
    if survivor.needs.health < balance.MIN_EXPEDITION_HEALTH:
        raise GameError(f"{survivor.name} is too hurt to leave")
    if building_id == state.base_building_id:
        raise GameError("The shelter cannot be scavenged")

    cell = state.cell_for_building(building_id)
    one_way = travel_hours(state, cell.coordinates.x, cell.coordinates.y)
    total = 2 * one_way + balance.SEARCH_HOURS

    expedition = Expedition(
        id=f"e{state.next_expedition_id}",
        survivor_id=survivor.id,
        building_id=building_id,
        cell=cell.coordinates,
        ticks_total=total,
        ticks_remaining=total,
    )
    state.next_expedition_id += 1
    state.expeditions.append(expedition)
    survivor.status = SurvivorStatus.AWAY
    survivor.current_location = cell.coordinates
    state.add_log(
        LogKind.INFO,
        f"{survivor.name} left for a {cell.sector_type.value} building ({total}h round trip).",
    )
    return expedition


def advance_expeditions(state: GameState) -> None:
    """Avanca uma hora em todas as expedicoes e conclui as que terminaram.

    Args:
        state: Estado da partida.
    """
    finished = []
    for expedition in state.expeditions:
        expedition.ticks_remaining -= 1
        if expedition.ticks_remaining <= 0:
            finished.append(expedition)
    for expedition in finished:
        if expedition in state.expeditions:
            _resolve(state, expedition)


def _loot_fraction(survivor: Survivor) -> float:
    """Calcula a fracao da pilhagem que o sobrevivente consegue carregar.

    Args:
        survivor: Sobrevivente em expedicao.

    Returns:
        Fracao entre 0 e 1.
    """
    fraction = balance.BASE_LOOT_FRACTION + balance.LOOT_FRACTION_PER_SKILL * survivor.skills.scavenging
    if survivor.role == SurvivorRole.SCAVENGER:
        fraction += balance.SCAVENGER_LOOT_BONUS
    return min(1.0, fraction * efficiency(survivor))


def _resolve(state: GameState, expedition: Expedition) -> None:
    """Conclui uma expedicao: encontro com zumbis, pilhagem e retorno.

    Args:
        state: Estado da partida.
        expedition: Expedicao que terminou.
    """
    rng = state.rng("expedition")
    survivor = state.find_survivor(expedition.survivor_id)
    state.expeditions.remove(expedition)
    building = get_or_create_building(state, expedition.building_id)
    cell = state.cell_for_building(expedition.building_id)

    danger = balance.SECTOR_DANGER[cell.sector_type]
    if state.clock.phase == "night":
        danger += balance.NIGHT_DANGER_BONUS

    if rng.random() < danger:
        damage = max(
            2,
            rng.randint(balance.ENCOUNTER_MIN_DAMAGE, balance.ENCOUNTER_MAX_DAMAGE)
            - balance.ENCOUNTER_DAMAGE_REDUCTION_PER_COMBAT * survivor.skills.combat,
        )
        survivor.needs.health = clamp(survivor.needs.health - damage)
        state.add_log(LogKind.WARNING, f"{survivor.name} ran into zombies and lost {int(damage)} health.")
        maybe_improve_skill(survivor, "combat", rng)
        if survivor.needs.health <= 0:
            kill_survivor(state, survivor, "during the expedition")
            return

    fraction = _loot_fraction(survivor)
    taken = Resources(**{
        name: int(round(value * fraction))
        for name, value in building.loot.model_dump().items()
    })
    building.loot.subtract(taken)
    building.searched = True
    cell.is_explored = True
    state.resources.add(taken)

    survivor.status = SurvivorStatus.HOME
    survivor.current_location = state.base_cell
    state.add_log(LogKind.SUCCESS, f"{survivor.name} returned with {taken.describe()}.")

    if maybe_improve_skill(survivor, "scavenging", rng):
        state.add_log(LogKind.INFO, f"{survivor.name} got better at scavenging.")

    if building.survivor_present:
        building.survivor_present = False
        if len(state.alive_survivors()) < balance.MAX_SURVIVORS:
            newcomer = create_survivor(state, rng)
            state.add_log(LogKind.SUCCESS, f"{newcomer.name} was found and joined the shelter.")
