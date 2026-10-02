"""Rotas de expedicoes."""

from fastapi import APIRouter

from app.api.schemas import ExpeditionRequest, GameView, build_view
from app.services import expedition_service
from app.services.game_manager import manager

router = APIRouter()


@router.post("", response_model=GameView)
def create_expedition(request: ExpeditionRequest) -> GameView:
    """Envia um sobrevivente a vasculhar uma construcao.

    Args:
        request: Sobrevivente e construcao alvo.

    Returns:
        A partida atualizada.
    """
    with manager.session() as state:
        expedition_service.start_expedition(state, request.survivor_id, request.building_id)
        return build_view(state)
