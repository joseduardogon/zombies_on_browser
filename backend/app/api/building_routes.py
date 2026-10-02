"""Rota de consulta de construcoes."""

from fastapi import APIRouter

from app.api.schemas import build_building_view
from app.models.building import Building
from app.services.game_manager import manager

router = APIRouter()


@router.get("/{building_id}", response_model=Building)
def get_building(building_id: str) -> Building:
    """Retorna uma construcao, gerando-a na primeira consulta.

    Args:
        building_id: Identificador da construcao, como "b-5-3".

    Returns:
        A construcao. Responde 404 se o identificador nao existir.
    """
    with manager.session() as state:
        return build_building_view(state, building_id)
