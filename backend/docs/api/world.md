# world_routes.py

Arquivo: `app/api/world_routes.py`. Prefixo: `/api/world`.

## O que e

Uma unica rota, que devolve o mapa da partida corrente.

```python
@router.get("/state", response_model=WorldMap)
def get_world_state() -> WorldMap:
    with manager.session() as state:
        return state.world
```

## O que mudou

- **`POST /generate` foi removida.** Ela gerava um mundo global, guardado em uma variavel de modulo (`current_world`) e sem relacao com sobreviventes ou relogio. A geracao agora e o servico [world_generator](../services/world_generator.md), chamado por `POST /api/game/new`.
- **Sem estado global na rota.** O mundo vive em `GameState.world`, entao e salvo e carregado junto com a partida.

## Por que assim

O frontend atual recebe o mapa dentro de `GameView` e nao usa esta rota; ela foi mantida por ser barata e util para ferramentas de depuracao e para quem quiser consumir so o mapa.
