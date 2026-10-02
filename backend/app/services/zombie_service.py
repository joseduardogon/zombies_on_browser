"""Ondas noturnas de zumbis e o cerco ao abrigo."""

import math

from app.core import balance
from app.models.building import Aperture, ApertureState
from app.models.game import GameState, LogKind, Siege
from app.models.survivor import Survivor, SurvivorRole, SurvivorStatus
from app.services.base_service import base_building
from app.services.building_service import recompute_integrity
from app.services.survivor_service import clamp, efficiency, kill_survivor


def _zombies(count: int) -> str:
    """Formata uma quantidade de zumbis no singular ou no plural.

    Args:
        count: Quantidade de zumbis.

    Returns:
        Texto como "1 zombie" ou "3 zombies".
    """
    return f"{count} zombie" if count == 1 else f"{count} zombies"


def start_night(state: GameState) -> None:
    """Sorteia o tamanho da onda da noite e inicia um novo cerco.

    Args:
        state: Estado da partida.
    """
    rng = state.rng("wave")
    day = state.clock.day
    size = balance.WAVE_BASE + int(day * balance.WAVE_PER_DAY) + rng.randint(0, day // 3)
    state.siege = Siege(wave_size=size)
    state.add_log(LogKind.WARNING, f"Night falls. A horde of about {size} zombies is heading your way.")


def end_night(state: GameState) -> None:
    """Encerra o cerco ao amanhecer.

    Args:
        state: Estado da partida.
    """
    siege = state.siege
    if siege.wave_size:
        state.add_log(
            LogKind.INFO,
            f"Dawn breaks. {_zombies(siege.killed)} put down; the rest retreat.",
        )
    state.siege = Siege()


def assault_round(state: GameState) -> None:
    """Executa uma rodada de ataque: chegada, tiros dos guardas e pancadaria.

    Args:
        state: Estado da partida.
    """
    siege = state.siege
    group = math.ceil(siege.wave_size / len(balance.ASSAULT_HOURS))
    arriving = min(group, siege.wave_size - siege.arrived)
    siege.arrived += arriving
    siege.at_gate += arriving
    if siege.at_gate == 0:
        return

    kills = min(siege.at_gate, _guard_fire(state))
    siege.at_gate -= kills
    siege.killed += kills
    state.total_zombies_killed += kills
    if kills:
        state.add_log(LogKind.INFO, f"The guards put down {_zombies(kills)}.")
    if siege.at_gate > 0:
        _batter(state)


def _guards(state: GameState) -> list[Survivor]:
    """Lista os guardas aptos a combater.

    Args:
        state: Estado da partida.

    Returns:
        Guardas no abrigo e com saude suficiente.
    """
    return [
        s
        for s in state.home_survivors()
        if s.role == SurvivorRole.GUARD and s.needs.health >= balance.GUARD_MIN_HEALTH
    ]


def _guard_fire(state: GameState) -> int:
    """Calcula quantos zumbis os guardas abatem nesta rodada.

    Cada guarda mata `1 + combate // 2` zumbis, com bonus se gastar uma municao.
    Guardas exaustos ou desmoralizados rendem metade e todos se cansam.

    Args:
        state: Estado da partida.

    Returns:
        Total de zumbis abatidos.
    """
    total = 0
    for guard in _guards(state):
        power = balance.GUARD_BASE_KILLS + guard.skills.combat // balance.GUARD_COMBAT_DIVISOR
        if state.resources.ammo > 0:
            state.resources.ammo -= 1
            power += balance.GUARD_AMMO_BONUS
        total += int(power * efficiency(guard))
        guard.needs.fatigue = clamp(guard.needs.fatigue - balance.GUARD_FATIGUE_COST)
    return total


def _weakest_aperture(state: GameState) -> Aperture | None:
    """Escolhe a abertura intacta mais fraca do abrigo.

    Args:
        state: Estado da partida.

    Returns:
        A abertura de menor saude que ainda nao quebrou, ou None.
    """
    base = base_building(state)
    intact = [
        a
        for room in base.rooms
        for a in room.apertures
        if a.state != ApertureState.BROKEN
    ]
    return min(intact, key=lambda a: a.health, default=None)


def _batter(state: GameState) -> None:
    """Os zumbis no portao atacam a abertura mais fraca.

    Se alguma abertura estiver quebrada ao fim do ataque, os zumbis invadem.

    Args:
        state: Estado da partida.
    """
    base = base_building(state)
    target = _weakest_aperture(state)
    if target is not None:
        target.health = max(0, target.health - state.siege.at_gate * balance.ZOMBIE_DAMAGE)
        if target.health == 0:
            target.state = ApertureState.BROKEN
            state.add_log(LogKind.DANGER, f"A {target.type} was broken down by the horde!")
    recompute_integrity(base)

    breached = any(
        a.state == ApertureState.BROKEN for room in base.rooms for a in room.apertures
    ) or not any(room.apertures for room in base.rooms)
    if breached:
        _intrude(state)


def _intrude(state: GameState) -> None:
    """Zumbis entram pelo abrigo e ferem sobreviventes.

    Args:
        state: Estado da partida.
    """
    rng = state.rng("intrusion")
    victims = state.home_survivors()
    if not victims:
        return
    intruders = min(state.siege.at_gate, balance.INTRUDER_CAP)
    state.add_log(LogKind.DANGER, f"{_zombies(intruders)} inside the shelter!")
    for _ in range(intruders):
        victim = rng.choice(victims)
        victim.needs.health = clamp(
            victim.needs.health
            - rng.randint(balance.INTRUDER_MIN_DAMAGE, balance.INTRUDER_MAX_DAMAGE)
        )
        if victim.needs.health <= 0:
            kill_survivor(state, victim, "defending the shelter")
            victims = state.home_survivors()
            if not victims:
                return
    for survivor in state.home_survivors():
        survivor.needs.morale = clamp(survivor.needs.morale - balance.BREACH_MORALE_LOSS)
