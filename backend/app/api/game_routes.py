"""Rotas do ciclo de vida da partida: criar, consultar, avancar e salvar."""

from fastapi import APIRouter

from app.api.schemas import GameView, NewGameRequest, SlotRequest, TickRequest, build_view
from app.services import game_factory, simulation
from app.services.game_manager import manager
from app.services.persistence import SaveInfo

router = APIRouter()


@router.post("/new", response_model=GameView)
def new_game(request: NewGameRequest) -> GameView:
    """Cria uma nova partida, descartando a corrente.

    Args:
        request: Dimensoes do mapa e semente opcional.

    Returns:
        A partida recem-criada, aguardando a escolha do abrigo.
    """
    state = game_factory.new_game(request.width, request.height, request.seed)
    return build_view(manager.replace(state))


@router.get("", response_model=GameView)
def get_game() -> GameView:
    """Retorna a partida corrente.

    Returns:
        A visao da partida. Responde 404 se nao houver nenhuma.
    """
    with manager.session() as state:
        return build_view(state)


@router.post("/tick", response_model=GameView)
def tick(request: TickRequest) -> GameView:
    """Avanca o tempo da partida.

    Args:
        request: Quantidade de horas.

    Returns:
        A partida depois da passagem de tempo.
    """
    with manager.session() as state:
        state.require_playing()
        simulation.advance_hours(state, request.hours)
        return build_view(state)


@router.get("/saves", response_model=list[SaveInfo])
def list_saves() -> list[SaveInfo]:
    """Lista os jogos salvos.

    Returns:
        Resumo de cada espaco de salvamento.
    """
    return manager.repository.list_saves()


@router.post("/save", response_model=list[SaveInfo])
def save_game(request: SlotRequest) -> list[SaveInfo]:
    """Grava a partida corrente em um espaco nomeado.

    Args:
        request: Nome do espaco.

    Returns:
        A lista atualizada de jogos salvos.
    """
    manager.save_slot(request.slot)
    return manager.repository.list_saves()


@router.post("/load", response_model=GameView)
def load_game(request: SlotRequest) -> GameView:
    """Carrega um jogo salvo e o torna a partida corrente.

    Args:
        request: Nome do espaco.

    Returns:
        A partida carregada.
    """
    return build_view(manager.load_slot(request.slot))
