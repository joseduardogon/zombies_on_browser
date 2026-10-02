"""Configuracao da aplicacao lida do ambiente."""

import os
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "zombies.db"


def get_db_path() -> Path:
    """Resolve o caminho do banco SQLite.

    Returns:
        O valor de ZOB_DB_PATH, se definido, ou o caminho padrao em `data/`.
    """
    return Path(os.environ.get("ZOB_DB_PATH", DEFAULT_DB_PATH))
