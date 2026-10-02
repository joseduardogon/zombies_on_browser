# persistence.py

Arquivo: `app/services/persistence.py`.

## O que e

Guarda e recupera partidas em um arquivo SQLite, usando apenas o modulo `sqlite3` da biblioteca padrao.

## Como foi feito

### Tabela

```python
            conn.execute(
                "CREATE TABLE IF NOT EXISTS saves ("
                "slot TEXT PRIMARY KEY, payload TEXT NOT NULL, "
                "updated_at TEXT NOT NULL, day INTEGER NOT NULL, status TEXT NOT NULL)"
            )
```

Cada linha e um **espaco** de salvamento (`slot`): o `payload` e a partida inteira em JSON, e `day` e `status` ficam em colunas proprias para listar saves sem abrir o JSON.

### Gravar e ler

```python
                (slot, state.model_dump_json(), now, state.clock.day, state.status.value),
```

```python
        return GameState.model_validate_json(row[0]) if row else None
```

A serializacao e a do proprio Pydantic: o `GameState` vira JSON e volta identico (o teste `test_repository_roundtrip` compara `loaded == playing`). `INSERT OR REPLACE` substitui o save anterior do mesmo espaco.

### Conexao por operacao

```python
        with closing(self._connect()) as conn, conn:
```

Cada metodo abre uma conexao, usa e fecha. `closing` garante o fechamento do arquivo (importante no Windows, onde um arquivo aberto nao pode ser apagado) e o `with conn` faz o commit ou o rollback.

## Por que assim

- **Snapshot JSON em vez de tabelas.** O estado e um grafo de objetos aninhados (mapa, construcoes, comodos, aberturas, sobreviventes). Normalizar tudo em tabelas exigiria muito codigo para ganho zero, ja que a partida e sempre lida e gravada inteira.
- **Sem dependencias novas.** `sqlite3` ja vem com o Python; nao foi preciso SQLAlchemy.
- **Espacos nomeados.** O slot `autosave` e gravado a cada acao (ver [game_manager](game_manager.md)); o jogador pode criar outros, como `manual`, e carregar qualquer um depois.
- **`SaveInfo`.** Um modelo pequeno com espaco, data, dia e status; e o que a API devolve ao listar saves.
