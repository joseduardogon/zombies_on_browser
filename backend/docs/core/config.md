# config.py

Arquivo: `app/core/config.py`.

## O que e

Resolve onde fica o arquivo SQLite das partidas salvas.

## Como foi feito

```python
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "zombies.db"
...
def get_db_path() -> Path:
    return Path(os.environ.get("ZOB_DB_PATH", DEFAULT_DB_PATH))
```

- `parents[2]` sobe de `app/core/config.py` ate a pasta `backend/`, entao o padrao e `backend/data/zombies.db`, independente do diretorio de onde o servidor foi iniciado.
- A variavel de ambiente `ZOB_DB_PATH` substitui o caminho. Foi usada para apontar o servidor de desenvolvimento a um banco temporario durante os testes manuais.
- A pasta `data/` esta no `.gitignore` do backend, entao saves nunca entram no repositorio.

### Pasta do frontend

```python
def get_static_dir() -> Path | None:
    value = os.environ.get("ZOB_STATIC_DIR")
    if value and Path(value).is_dir():
        return Path(value)
    return None
```

Dentro do container o backend serve tambem o frontend compilado. `ZOB_STATIC_DIR` aponta para essa pasta; se a variavel nao existe (desenvolvimento) ou a pasta nao existe, o retorno e `None` e a API roda sozinha.

## Por que assim

- **Caminho relativo ao codigo, nao ao cwd.** `uvicorn` pode ser iniciado de qualquer pasta; um caminho relativo ao diretorio atual criaria bancos diferentes a cada vez.
- **A funcao e chamada sob demanda.** `GameManager.repository` chama `get_db_path()` so quando precisa abrir o banco, e nao na importacao. Assim os testes podem trocar o repositorio antes de qualquer arquivo ser criado.
