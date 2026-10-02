"""Guarda a partida corrente e coordena acesso e salvamento."""

import threading
from contextlib import contextmanager
from typing import Iterator

from app.core import balance
from app.core.config import get_db_path
from app.core.errors import GameError
from app.models.game import GameState
from app.services.persistence import GameRepository


class GameManager:
    """Mantem a partida corrente em memoria e a grava a cada alteracao.

    O acesso e serializado por um lock, porque o FastAPI executa as rotas
    sincronas em varias threads.

    Attributes:
        state: Partida corrente, ou None se ainda nao ha nenhuma.
    """

    def __init__(self) -> None:
        """Cria o gerenciador sem partida e sem repositorio."""
        self.state: GameState | None = None
        self._repository: GameRepository | None = None
        self._lock = threading.RLock()

    @property
    def repository(self) -> GameRepository:
        """Repositorio de salvamentos, aberto sob demanda.

        Returns:
            O repositorio configurado ou o padrao do ambiente.
        """
        if self._repository is None:
            self._repository = GameRepository(get_db_path())
        return self._repository

    def configure(self, repository: GameRepository | None) -> None:
        """Troca o repositorio e descarta a partida corrente.

        Args:
            repository: Novo repositorio, ou None para voltar ao padrao.
        """
        with self._lock:
            self._repository = repository
            self.state = None

    def load_autosave(self) -> bool:
        """Retoma a partida do salvamento automatico, se existir.

        Returns:
            True se uma partida foi carregada.
        """
        with self._lock:
            loaded = self.repository.load(balance.AUTOSAVE_SLOT)
            if loaded is not None:
                self.state = loaded
            return loaded is not None

    def replace(self, state: GameState) -> GameState:
        """Define a partida corrente e a grava.

        Args:
            state: Nova partida.

        Returns:
            A partida definida.
        """
        with self._lock:
            self.state = state
            self.repository.save(balance.AUTOSAVE_SLOT, state)
            return state

    @contextmanager
    def session(self) -> Iterator[GameState]:
        """Da acesso exclusivo a partida e a grava ao sair sem erro.

        Yields:
            A partida corrente.

        Raises:
            GameError: Com status 404 se nao houver partida.
        """
        with self._lock:
            if self.state is None:
                raise GameError("No game in progress", 404)
            yield self.state
            self.repository.save(balance.AUTOSAVE_SLOT, self.state)

    def save_slot(self, slot: str) -> None:
        """Grava a partida corrente em um espaco nomeado.

        Args:
            slot: Nome do espaco de salvamento.
        """
        with self._lock:
            if self.state is None:
                raise GameError("No game in progress", 404)
            self.repository.save(slot, self.state)

    def load_slot(self, slot: str) -> GameState:
        """Carrega uma partida de um espaco nomeado e a torna corrente.

        Args:
            slot: Nome do espaco de salvamento.

        Returns:
            A partida carregada.

        Raises:
            GameError: Com status 404 se o espaco estiver vazio.
        """
        with self._lock:
            loaded = self.repository.load(slot)
            if loaded is None:
                raise GameError("Save not found", 404)
            return self.replace(loaded)


manager = GameManager()
