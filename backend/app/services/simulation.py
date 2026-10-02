"""Passagem de tempo: orquestra tudo o que acontece a cada hora."""

from app.core import balance
from app.models.game import GameState, GameStatus, LogKind
from app.services import expedition_service, survivor_service, zombie_service


def advance_hour(state: GameState) -> None:
    """Avanca a partida em uma hora.

    A ordem e: relogio, eventos da noite (chegada da onda, ataque, amanhecer),
    necessidades dos sobreviventes, expedicoes e, por fim, as condicoes de
    vitoria e derrota.

    Args:
        state: Estado da partida.
    """
    state.require_playing()
    state.clock.advance()
    hour = state.clock.hour

    if hour == balance.NIGHT_START_HOUR:
        zombie_service.start_night(state)
    if hour in balance.ASSAULT_HOURS:
        zombie_service.assault_round(state)
    if hour == balance.NIGHT_END_HOUR:
        zombie_service.end_night(state)

    survivor_service.update_needs_hour(state)
    expedition_service.advance_expeditions(state)
    _check_end(state)


def advance_hours(state: GameState, hours: int) -> None:
    """Avanca varias horas, parando se a partida terminar.

    Args:
        state: Estado da partida.
        hours: Quantidade de horas a avancar.
    """
    for _ in range(hours):
        if state.status != GameStatus.PLAYING:
            break
        advance_hour(state)


def _check_end(state: GameState) -> None:
    """Verifica as condicoes de vitoria e derrota.

    Args:
        state: Estado da partida.
    """
    if not state.alive_survivors():
        state.status = GameStatus.LOST
        state.add_log(LogKind.DANGER, "Everyone is dead. The shelter has fallen.")
    elif state.clock.day > balance.TARGET_DAY:
        state.status = GameStatus.WON
        state.add_log(
            LogKind.SUCCESS,
            f"You survived {balance.TARGET_DAY} days. Help has finally arrived.",
        )
