"""Persistencia de partidas em SQLite."""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from app.models.game import GameState


class SaveInfo(BaseModel):
    """Resumo de um jogo salvo.

    Attributes:
        slot: Nome do espaco de salvamento.
        updated_at: Data do ultimo salvamento, em ISO 8601.
        day: Dia da partida salva.
        status: Fase da partida salva.
    """

    slot: str
    updated_at: str
    day: int
    status: str


class GameRepository:
    """Guarda e recupera partidas em um arquivo SQLite.

    Cada espaco de salvamento guarda um snapshot JSON da partida inteira.

    Attributes:
        path: Caminho do arquivo do banco.
    """

    def __init__(self, path: Path) -> None:
        """Abre o repositorio e cria a tabela se necessario.

        Args:
            path: Caminho do arquivo do banco. Pastas ausentes sao criadas.
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS saves ("
                "slot TEXT PRIMARY KEY, payload TEXT NOT NULL, "
                "updated_at TEXT NOT NULL, day INTEGER NOT NULL, status TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        """Abre uma conexao com o banco.

        Returns:
            Conexao nova; quem chama deve fecha-la.
        """
        return sqlite3.connect(self.path)

    def save(self, slot: str, state: GameState) -> None:
        """Grava a partida em um espaco, substituindo o anterior.

        Args:
            slot: Nome do espaco de salvamento.
            state: Partida a gravar.
        """
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "INSERT OR REPLACE INTO saves (slot, payload, updated_at, day, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (slot, state.model_dump_json(), now, state.clock.day, state.status.value),
            )

    def load(self, slot: str) -> GameState | None:
        """Le a partida de um espaco.

        Args:
            slot: Nome do espaco de salvamento.

        Returns:
            A partida, ou None se o espaco estiver vazio.
        """
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT payload FROM saves WHERE slot = ?", (slot,)).fetchone()
        return GameState.model_validate_json(row[0]) if row else None

    def list_saves(self) -> list[SaveInfo]:
        """Lista os espacos de salvamento, do mais recente ao mais antigo.

        Returns:
            Resumo de cada jogo salvo.
        """
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT slot, updated_at, day, status FROM saves ORDER BY updated_at DESC"
            ).fetchall()
        return [SaveInfo(slot=r[0], updated_at=r[1], day=r[2], status=r[3]) for r in rows]
