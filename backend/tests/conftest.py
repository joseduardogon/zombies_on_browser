"""Fixtures compartilhadas pelos testes."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.game import GameState
from app.services import game_factory
from app.services.game_manager import manager
from app.services.persistence import GameRepository


@pytest.fixture(autouse=True)
def isolated_repository(tmp_path: Path):
    """Aponta o gerenciador para um banco temporario em cada teste.

    Args:
        tmp_path: Pasta temporaria do teste.

    Yields:
        O repositorio temporario.
    """
    repository = GameRepository(tmp_path / "test.db")
    manager.configure(repository)
    yield repository
    manager.configure(None)


@pytest.fixture
def client() -> TestClient:
    """Cliente HTTP da aplicacao.

    Returns:
        Cliente de teste do FastAPI.
    """
    return TestClient(app)


@pytest.fixture
def state() -> GameState:
    """Partida em fase de preparacao com semente fixa.

    Returns:
        Partida sem abrigo escolhido.
    """
    return game_factory.new_game(20, 20, seed=42)


@pytest.fixture
def playing(state: GameState) -> GameState:
    """Partida em andamento, com abrigo em uma casa.

    Args:
        state: Partida em preparacao.

    Returns:
        Partida com abrigo residencial e os tres sobreviventes iniciais.
    """
    residential = next(
        c for c in state.world.cells if c.sector_type.value == "residential"
    )
    game_factory.claim_base(state, residential.building_id)
    return state
