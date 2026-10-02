"""Acoes de defesa do abrigo."""

from app.core import balance
from app.core.errors import GameError
from app.models.building import Building, ApertureState
from app.models.game import GameState, LogKind
from app.models.survivor import SurvivorRole, SurvivorStatus
from app.services.building_service import find_aperture, recompute_integrity
from app.services.survivor_service import clamp, maybe_improve_skill


def base_building(state: GameState) -> Building:
    """Retorna a construcao do abrigo.

    Args:
        state: Estado da partida.

    Returns:
        A construcao escolhida como abrigo.

    Raises:
        GameError: Se o abrigo ainda nao foi escolhido.
    """
    if state.base_building_id is None:
        raise GameError("No shelter chosen", 409)
    return state.buildings[state.base_building_id]


def reinforce_aperture(state: GameState, aperture_id: str, survivor_id: str) -> Building:
    """Reforca ou conserta uma abertura do abrigo com madeira.

    A saude ganha cresce com a habilidade de construcao do sobrevivente, com
    bonus para quem e construtor. Uma abertura quebrada volta a funcionar.

    Args:
        state: Estado da partida.
        aperture_id: Abertura a reforcar.
        survivor_id: Sobrevivente que faz o trabalho.

    Returns:
        O abrigo atualizado.

    Raises:
        GameError: Se a abertura nao existir, nao houver madeira, o
            sobrevivente nao estiver no abrigo ou a abertura ja estiver no
            limite.
    """
    state.require_playing()
    base = base_building(state)
    found = find_aperture(base, aperture_id)
    if found is None:
        raise GameError("Aperture not found", 404)
    _, aperture = found

    worker = state.find_survivor(survivor_id)
    if worker.status != SurvivorStatus.HOME:
        raise GameError(f"{worker.name} is not at the shelter")
    if aperture.health >= balance.APERTURE_HEALTH_CAP:
        raise GameError("This opening is already fully reinforced")
    if state.resources.wood < balance.BARRICADE_WOOD_COST:
        raise GameError("Not enough wood")

    gain = balance.BARRICADE_BASE_HEALTH + balance.BARRICADE_HEALTH_PER_SKILL * worker.skills.construction
    if worker.role == SurvivorRole.BUILDER:
        gain = int(gain * balance.BUILDER_BONUS)

    state.resources.wood -= balance.BARRICADE_WOOD_COST
    aperture.health = min(balance.APERTURE_HEALTH_CAP, aperture.health + gain)
    aperture.state = ApertureState.BARRICADED
    worker.needs.fatigue = clamp(worker.needs.fatigue - 4)

    if maybe_improve_skill(worker, "construction", state.rng("skill")):
        state.add_log(LogKind.INFO, f"{worker.name} got better at construction.")
    recompute_integrity(base)
    return base
