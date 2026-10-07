# Testes

Pasta: `tests/`. Rodam com:

```bash
poetry lock
poetry install
poetry run pytest
```

O `poetry lock` so e necessario na primeira vez: `pytest` e `httpx` foram declarados em `pyproject.toml` sem regenerar o `poetry.lock`.

Sao 58 testes, todos rapidos (menos de um segundo no total).

| Arquivo | O que cobre |
|---------|-------------|
| `conftest.py` | Fixtures: banco temporario, cliente HTTP, partida em preparacao e em andamento |
| `test_world_and_buildings.py` | Geracao do mapa, identificadores, tamanhos, determinismo das construcoes |
| `test_simulation.py` | Relogio, necessidades, sono, vitoria, derrota, determinismo da partida |
| `test_expeditions.py` | Duracao, pilhagem, encontro fatal, sobrevivente resgatado |
| `test_defense.py` | Reforco, ondas, tiro dos guardas, abertura mais fraca, invasao |
| `test_persistence_and_api.py` | SQLite, autosave, fluxo completo via HTTP e erros |

## Fixtures

```python
@pytest.fixture(autouse=True)
def isolated_repository(tmp_path: Path):
    repository = GameRepository(tmp_path / "test.db")
    manager.configure(repository)
    yield repository
    manager.configure(None)
```

`autouse` faz **todo** teste rodar com um banco temporario proprio. Sem isso, o autosave de um teste vazaria para o seguinte (e poluiria `backend/data/`).

```python
@pytest.fixture
def state() -> GameState:
    return game_factory.new_game(20, 20, seed=42)
```

A semente fixa (`42`) torna o mapa igual em toda execucao, entao os testes podem procurar "uma casa" ou "uma loja" sem sorte envolvida.

## Como forcar cenarios

Os testes alteram o estado diretamente ou trocam constantes de balanceamento com `monkeypatch`. Por exemplo, para garantir que um encontro mate:

```python
    monkeypatch.setitem(balance.SECTOR_DANGER, cell.sector_type, 1.0)
    monkeypatch.setattr(balance, "ENCOUNTER_MIN_DAMAGE", 500)
    monkeypatch.setattr(balance, "ENCOUNTER_MAX_DAMAGE", 500)
```

Isso so e possivel porque as regras leem os numeros de `balance` em tempo de execucao (veja [balance](../core/balance.md)).

## Por que assim

- **Regras testadas sem HTTP.** A maior parte dos testes chama `services/` direto; so `test_persistence_and_api.py` usa o cliente HTTP, para garantir o contrato (status, corpo `detail`, formato de `GameView`).
- **Determinismo como propriedade testada.** `test_same_seed_and_actions_give_same_result` simula 72 horas duas vezes e compara os dois estados completos.
