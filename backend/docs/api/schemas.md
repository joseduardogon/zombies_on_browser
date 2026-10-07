# schemas.py

Arquivo: `app/api/schemas.py`.

## O que e

Os corpos de requisicao e a resposta principal, `GameView`.

## Como foi feito

### Requisicoes

Cada acao tem seu modelo, validado pelo Pydantic antes de qualquer regra rodar. O limite de horas, por exemplo:

```python
class TickRequest(BaseModel):
    hours: int = Field(default=1, ge=1, le=24)
```

`hours: 0` ou `hours: 99` nunca chegam ao servico: o FastAPI responde 422.

### `GameView`

```python
class GameView(BaseModel):
    id: str
    seed: int
    status: GameStatus
    clock: Clock
    target_day: int
    world: WorldMap
    survivors: list[Survivor]
    resources: Resources
    base_building: Building | None
    base_cell: Coordinates | None
    expeditions: list[Expedition]
    siege: Siege
    log: list[LogEntry]
    total_zombies_killed: int
```

E uma versao do `GameState` pensada para o cliente. Diferencas importantes:

- **Nao inclui `buildings`.** Seriam centenas de plantas; o cliente so precisa da do abrigo (`base_building`) e pede as demais uma a uma.
- **Inclui `target_day`.** O frontend mostra "Day 3/30" e nao deveria repetir a constante.
- **Nao inclui `rng_counter`** nem outros detalhes internos.

```python
    base = state.buildings.get(state.base_building_id) if state.base_building_id else None
    return GameView(
        id=state.id,
```

### Construcao sem spoilers

```python
    building = get_or_create_building(state, building_id)
    if building.searched:
        return building.model_copy(update={"survivor_present": False})
    return building.model_copy(update={"loot": Resources(), "survivor_present": False})
```

Quando o cliente consulta uma construcao, ele recebe uma **copia**:

- se ainda nao foi vasculhada, a pilhagem vem zerada: o jogador nao pode ver o que ha dentro sem ir ate la;
- depois de vasculhada, ele ve o que sobrou;
- `survivor_present` nunca e revelado: a surpresa de encontrar alguem e parte do jogo.

## Por que assim

- **Uma resposta unica.** O frontend poderia fazer cinco chamadas depois de cada acao; com `GameView` faz uma. O custo e enviar a visao inteira a cada resposta (cerca de 40 KB em um mapa 20x20, medido logo apos escolher o abrigo, e o mapa e a maior parte), que e pequeno diante da simplicidade ganha.
- **Copia, nao o objeto.** `model_copy(update=...)` evita alterar a construcao real ao esconder campos.
