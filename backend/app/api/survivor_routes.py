"""Rotas de sobreviventes."""

from fastapi import APIRouter

from app.api.schemas import GameView, RoleRequest, build_view
from app.models.survivor import Survivor
from app.services import survivor_service
from app.services.game_manager import manager

router = APIRouter()


@router.get("", response_model=list[Survivor])
def list_survivors() -> list[Survivor]:
    """Lista todos os sobreviventes.

    Returns:
        Os sobreviventes, vivos ou mortos.
    """
    with manager.session() as state:
        return state.survivors


@router.post("/{survivor_id}/role", response_model=GameView)
def change_role(survivor_id: str, request: RoleRequest) -> GameView:
    """Altera a funcao de um sobrevivente.

    Args:
        survivor_id: Sobrevivente a alterar.
        request: Nova funcao.

    Returns:
        A partida atualizada.
    """
    with manager.session() as state:
        survivor_service.set_role(state, survivor_id, request.role)
        return build_view(state)


@router.post("/{survivor_id}/treat", response_model=GameView)
def treat(survivor_id: str) -> GameView:
    """Trata um sobrevivente ferido com um remedio.

    Args:
        survivor_id: Sobrevivente a tratar.

    Returns:
        A partida atualizada.
    """
    with manager.session() as state:
        survivor_service.treat(state, survivor_id)
        return build_view(state)
