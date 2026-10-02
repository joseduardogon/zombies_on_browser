# building.py

Arquivo: `app/models/building.py`.

## O que e

Construcoes, seus comodos e suas aberturas (portas e janelas). As aberturas sao o ponto de contato entre o jogador e o perigo: sao elas que os zumbis atacam.

## Como foi feito

`RoomType` ganhou tres tipos para que todos os geradores produzam dados validos:

```python
class RoomType(str, Enum):
    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    GARAGE = "garage"
    STORAGE = "storage"
    INDUSTRIAL = "industrial"
    OUTDOOR = "outdoor"
    SHELTER = "shelter"
    EMPTY = "empty"
```

A `Building` agora guarda a pilhagem e se o local ja foi vasculhado:

```python
    id: str
    type: str
    rooms: list[Room]
    overall_integrity: int
    loot: Resources = Field(default_factory=Resources)
    searched: bool = False
    survivor_present: bool = False
```

- `loot` e o que ainda pode ser coletado. Cada expedicao leva uma fracao e o resto continua la.
- `searched` marca que alguem ja esteve la; e o que libera a exibicao da pilhagem restante no frontend.
- `survivor_present` indica um sobrevivente isolado esperando resgate. Fica escondido do cliente ate o local ser vasculhado (veja [schemas](../api/schemas.md)).

## O que mudou

- **Bug corrigido.** Os geradores de fabrica e de floresta criavam comodos com `type="industrial"`, `"outdoor"` e `"shelter"`, valores que nao existiam em `RoomType`. A validacao do Pydantic falhava e as rotas dessas construcoes devolviam erro 500. Os tres valores foram adicionados ao enum.
- **`Aperture` nao mudou.** `health` continua sendo a durabilidade da porta ou da barricada. O teto de 300 vive em `balance.APERTURE_HEALTH_CAP`, nao no modelo, para que seja um parametro de balanceamento.

## Por que assim

- **A integridade e um valor derivado.** `overall_integrity` e recalculada por `recompute_integrity` ([building_service](../services/building_service.md)) sempre que uma abertura muda; o modelo so a armazena.
- **Pilhagem no proprio objeto.** Colocar `loot` dentro da construcao faz o save/load guardar a pilhagem restante junto, sem tabela paralela.
