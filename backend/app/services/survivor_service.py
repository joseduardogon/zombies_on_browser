"""Regras de sobreviventes: criacao, necessidades, funcoes e cuidados."""

import random

from app.core import balance
from app.core.errors import GameError
from app.models.game import GameState, LogKind
from app.models.survivor import (
    Survivor,
    SurvivorRole,
    SurvivorSkills,
    SurvivorStatus,
)

SKILL_NAMES = ("construction", "combat", "scavenging", "medicine")


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Limita um valor a um intervalo.

    Args:
        value: Valor original.
        low: Minimo permitido.
        high: Maximo permitido.

    Returns:
        O valor dentro do intervalo.
    """
    return max(low, min(high, value))


def create_survivor(
    state: GameState,
    rng: random.Random,
    role: SurvivorRole = SurvivorRole.IDLE,
    skills: SurvivorSkills | None = None,
) -> Survivor:
    """Cria um sobrevivente no abrigo e o adiciona a partida.

    Args:
        state: Estado da partida.
        rng: Gerador aleatorio, usado para escolher o nome e as habilidades.
        role: Funcao inicial.
        skills: Habilidades iniciais. Se omitidas, sao sorteadas entre 1 e 2.

    Returns:
        O sobrevivente criado.
    """
    used = {s.name for s in state.survivors}
    free_names = [n for n in balance.SURVIVOR_NAMES if n not in used]
    name = rng.choice(free_names) if free_names else f"Survivor {state.next_survivor_id}"
    if skills is None:
        skills = SurvivorSkills(**{skill: rng.randint(1, 2) for skill in SKILL_NAMES})

    survivor = Survivor(
        id=f"s{state.next_survivor_id}",
        name=name,
        role=role,
        skills=skills,
        current_location=state.base_cell,
        assigned_building_id=state.base_building_id,
    )
    state.next_survivor_id += 1
    state.survivors.append(survivor)
    return survivor


def efficiency(survivor: Survivor) -> float:
    """Calcula o fator de eficiencia de um sobrevivente.

    Moral ou disposicao muito baixas reduzem o rendimento pela metade.

    Args:
        survivor: Sobrevivente avaliado.

    Returns:
        1.0 em condicao normal, ou o fator de baixa eficiencia.
    """
    needs = survivor.needs
    tired = min(needs.morale, needs.fatigue) < balance.LOW_EFFICIENCY_LEVEL
    return balance.LOW_EFFICIENCY_FACTOR if tired else 1.0


def kill_survivor(state: GameState, survivor: Survivor, cause: str) -> None:
    """Marca um sobrevivente como morto e registra o evento.

    Args:
        state: Estado da partida.
        survivor: Sobrevivente que morreu.
        cause: Descricao da causa da morte.
    """
    survivor.status = SurvivorStatus.DEAD
    survivor.needs.health = 0.0
    survivor.current_location = None
    state.expeditions = [e for e in state.expeditions if e.survivor_id != survivor.id]
    state.add_log(LogKind.DANGER, f"{survivor.name} died {cause}.")


def maybe_improve_skill(survivor: Survivor, skill: str, rng: random.Random) -> bool:
    """Sorteia se uma habilidade melhora apos ser usada.

    Args:
        survivor: Sobrevivente que usou a habilidade.
        skill: Nome da habilidade.
        rng: Gerador aleatorio.

    Returns:
        True se a habilidade subiu de nivel.
    """
    current = getattr(survivor.skills, skill)
    if current >= balance.SKILL_CAP or rng.random() >= balance.SKILL_GAIN_CHANCE:
        return False
    setattr(survivor.skills, skill, current + 1)
    return True


def _consume(state: GameState, survivor: Survivor) -> None:
    """Faz o sobrevivente comer e beber quando precisa e ha estoque.

    Args:
        state: Estado da partida.
        survivor: Sobrevivente no abrigo.
    """
    needs = survivor.needs
    if needs.hunger <= balance.EAT_THRESHOLD and state.resources.food > 0:
        state.resources.food -= 1
        needs.hunger = clamp(needs.hunger + balance.EAT_RESTORE)
    if needs.thirst <= balance.DRINK_THRESHOLD and state.resources.water > 0:
        state.resources.water -= 1
        needs.thirst = clamp(needs.thirst + balance.DRINK_RESTORE)


def _is_sleeping(survivor: Survivor, hour: int) -> bool:
    """Indica se o sobrevivente dorme na hora dada.

    Guardas vigiam a noite e dormem durante o dia.

    Args:
        survivor: Sobrevivente avaliado.
        hour: Hora do dia.

    Returns:
        True se a hora cai no periodo de sono da sua funcao.
    """
    if survivor.role == SurvivorRole.GUARD:
        return hour in balance.GUARD_SLEEP_HOURS
    return hour in balance.SLEEP_HOURS


def update_needs_hour(state: GameState) -> None:
    """Aplica uma hora de desgaste a todos os sobreviventes vivos.

    Fome, sede e cansaco caem; quem esta no abrigo come e bebe se houver
    estoque; quem nao e guarda dorme de madrugada e os guardas dormem de dia. Saude e moral reagem ao
    estado das necessidades, e quem chega a zero de saude morre.

    Args:
        state: Estado da partida.
    """
    hour = state.clock.hour
    for survivor in state.alive_survivors():
        needs = survivor.needs
        at_home = survivor.status == SurvivorStatus.HOME
        was_hungry = needs.hunger > 0
        was_thirsty = needs.thirst > 0

        needs.hunger = clamp(needs.hunger - balance.HUNGER_DECAY)
        needs.thirst = clamp(needs.thirst - balance.THIRST_DECAY)
        if at_home:
            _consume(state, survivor)
            if _is_sleeping(survivor, hour):
                needs.fatigue = clamp(needs.fatigue + balance.SLEEP_RECOVERY)
            else:
                needs.fatigue = clamp(needs.fatigue - balance.FATIGUE_DECAY_HOME)
        else:
            needs.fatigue = clamp(needs.fatigue - balance.FATIGUE_DECAY_AWAY)

        if was_hungry and needs.hunger <= 0:
            state.add_log(LogKind.WARNING, f"{survivor.name} is starving.")
        if was_thirsty and needs.thirst <= 0:
            state.add_log(LogKind.WARNING, f"{survivor.name} is dying of thirst.")

        _update_health_and_morale(survivor)
        if needs.health <= 0:
            kill_survivor(state, survivor, "of hunger, thirst or exhaustion")


def _update_health_and_morale(survivor: Survivor) -> None:
    """Atualiza saude e moral a partir das necessidades.

    Args:
        survivor: Sobrevivente a atualizar.
    """
    needs = survivor.needs
    if needs.hunger <= 0 or needs.thirst <= 0:
        needs.health = clamp(needs.health - balance.STARVATION_DAMAGE)
    if needs.fatigue <= 0:
        needs.health = clamp(needs.health - balance.EXHAUSTION_DAMAGE)
    if needs.hunger > 50 and needs.thirst > 50 and needs.fatigue > 30:
        needs.health = clamp(needs.health + balance.HEALTH_REGEN)

    suffering = (
        min(needs.hunger, needs.thirst) < balance.LOW_NEED_LEVEL
        or needs.health < 30
    )
    delta = -balance.MORALE_LOSS if suffering else balance.MORALE_GAIN
    needs.morale = clamp(needs.morale + delta)


def set_role(state: GameState, survivor_id: str, role: SurvivorRole) -> Survivor:
    """Altera a funcao de um sobrevivente.

    Args:
        state: Estado da partida.
        survivor_id: Sobrevivente a alterar.
        role: Nova funcao.

    Returns:
        O sobrevivente atualizado.

    Raises:
        GameError: Se a partida nao estiver em andamento ou o sobrevivente
            estiver morto.
    """
    state.require_playing()
    survivor = state.find_survivor(survivor_id)
    if survivor.status == SurvivorStatus.DEAD:
        raise GameError(f"{survivor.name} is dead")
    survivor.role = role
    return survivor


def treat(state: GameState, survivor_id: str) -> Survivor:
    """Trata um sobrevivente ferido usando um remedio.

    A cura cresce com a melhor habilidade de medicina entre os vivos no abrigo.

    Args:
        state: Estado da partida.
        survivor_id: Sobrevivente a tratar.

    Returns:
        O sobrevivente tratado.

    Raises:
        GameError: Se nao houver remedio, o alvo estiver morto, longe do
            abrigo ou ja com a saude cheia.
    """
    state.require_playing()
    patient = state.find_survivor(survivor_id)
    if patient.status != SurvivorStatus.HOME:
        raise GameError(f"{patient.name} is not at the shelter")
    if patient.needs.health >= 100:
        raise GameError(f"{patient.name} is already healthy")
    if state.resources.medicine < 1:
        raise GameError("No medicine available")

    best = max(s.skills.medicine for s in state.home_survivors())
    heal = balance.TREAT_BASE_HEAL + balance.TREAT_SKILL_HEAL * best
    state.resources.medicine -= 1
    patient.needs.health = clamp(patient.needs.health + heal)
    state.add_log(LogKind.SUCCESS, f"{patient.name} was treated and recovered {int(heal)} health.")
    return patient
