"""Configuracao da aplicacao lida do ambiente."""

import os
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "zombies.db"


def get_static_dir() -> Path | None:
    """Resolve a pasta do frontend compilado, se existir.

    Returns:
        O valor de ZOB_STATIC_DIR, se for uma pasta existente, ou None.
    """
    value = os.environ.get("ZOB_STATIC_DIR")
    if value and Path(value).is_dir():
        return Path(value)
    return None


def get_db_path() -> Path:
    """Resolve o caminho do banco SQLite.

    Returns:
        O valor de ZOB_DB_PATH, se definido, ou o caminho padrao em `data/`.
    """
    return Path(os.environ.get("ZOB_DB_PATH", DEFAULT_DB_PATH))
