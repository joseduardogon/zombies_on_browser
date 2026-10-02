"""Rotas do abrigo: escolha do local e reforco das aberturas."""

from fastapi import APIRouter

from app.api.schemas import ClaimBaseRequest, GameView, ReinforceRequest, build_view
from app.services import base_service, game_factory
from app.services.game_manager import manager

router = APIRouter()


@router.post("/claim", response_model=GameView)
def claim_base(request: ClaimBaseRequest) -> GameView:
    """Escolhe o abrigo e inicia a partida.

    Args:
        request: Construcao escolhida.

    Returns:
        A partida em andamento.
    """
    with manager.session() as state:
        game_factory.claim_base(state, request.building_id)
        return build_view(state)


@router.post("/reinforce", response_model=GameView)
def reinforce(request: ReinforceRequest) -> GameView:
    """Reforca ou conserta uma abertura do abrigo.

    Args:
        request: Abertura e sobrevivente responsavel.

    Returns:
        A partida atualizada.
    """
    with manager.session() as state:
        base_service.reinforce_aperture(state, request.aperture_id, request.survivor_id)
        return build_view(state)
