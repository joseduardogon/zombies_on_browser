"""Rota de consulta do mapa do mundo."""

from fastapi import APIRouter

from app.models.world import WorldMap
from app.services.game_manager import manager

router = APIRouter()


@router.get("/state", response_model=WorldMap)
def get_world_state() -> WorldMap:
    """Retorna o mapa da partida corrente.

    Returns:
        O mapa da cidade. Responde 404 se nao houver partida.
    """
    with manager.session() as state:
        return state.world
