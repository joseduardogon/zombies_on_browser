# game_routes.py

Arquivo: `app/api/game_routes.py`. Prefixo: `/api/game`.

## O que e

O ciclo de vida da partida: criar, consultar, avancar o tempo e salvar ou carregar.

## Endpoints

### POST /new

```python
@router.post("/new", response_model=GameView)
def new_game(request: NewGameRequest) -> GameView:
    state = game_factory.new_game(request.width, request.height, request.seed)
    return build_view(manager.replace(state))
```

Corpo: `{"width": 20, "height": 20, "seed": null}`; todos opcionais. Cria o mundo, descarta a partida anterior e grava o autosave. Mapas fora de 8 a 40 geram 400.

### GET /api/game

```python
    with manager.session() as state:
        return build_view(state)
```

A partida corrente, ou 404 se ainda nao existe. O frontend chama isso ao abrir: 404 mostra a tela inicial, 200 retoma o jogo.

### POST /tick

```python
    with manager.session() as state:
        state.require_playing()
        simulation.advance_hours(state, request.hours)
        return build_view(state)
```

Corpo: `{"hours": 1}` (1 a 24). Antes de escolher o abrigo responde 409. O frontend o chama a cada 1,5 s em 1x, 0,75 s em 2x e 0,375 s em 4x, e com `hours: 6` no botao "+6h".

### Salvamentos

```python
    manager.save_slot(request.slot)
    return manager.repository.list_saves()
```

- `GET /saves` lista os espacos;
- `POST /save` grava a partida no espaco informado (padrao `manual`) e devolve a lista atualizada;
- `POST /load` carrega um espaco como partida corrente (404 se vazio).

## Por que assim

- **`/new` em vez de `/generate`.** Gerar mundo e iniciar partida sao a mesma operacao para o jogador, e isso evita que existam mundos soltos, sem relogio nem sobreviventes.
- **O `tick` valida a fase na rota.** `advance_hours` nao reclama quando a partida nao esta em andamento: ela apenas para (`break`) ao primeiro tick. A chamada explicita a `require_playing` na rota e o que produz o 409; sem ela, pedir horas antes de escolher o abrigo responderia 200 sem avancar nada.
- **Salvar devolve a lista.** O menu do frontend se atualiza na mesma resposta.
