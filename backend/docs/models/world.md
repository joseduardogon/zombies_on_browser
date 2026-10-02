# world.py

Arquivo: `app/models/world.py`.

## O que e

O mapa da cidade como dados: uma grade de celulas, cada uma com um tipo de setor.

## Como foi feito

```python
class SectorType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    FOREST = "forest"
    ROAD = "road"
```

A celula carrega, alem do setor, a ligacao com a construcao que existe naquele lote:

```python
class WorldCell(BaseModel):
    coordinates: Coordinates
    sector_type: SectorType
    is_explored: bool = False
    building_id: str | None = None
```

## O que mudou

- **`building_id` agora e preenchido.** Antes o campo existia mas ficava sempre vazio, e cada clique do frontend gerava uma construcao nova. Agora todo lote que nao e via recebe um identificador estavel (veja [world_generator](../services/world_generator.md)), e a construcao so e criada na primeira visita.
- **`Optional[str]` virou `str | None`.** Sintaxe moderna do Python 3.12, sem `typing.Optional`.

## Por que assim

- **A celula guarda so o identificador, nao a construcao.** O mapa tem ate 1.600 celulas (40x40). Embutir cada construcao inflaria a resposta de `/api/game`, que e consultada a cada hora de jogo. As construcoes ficam em `GameState.buildings` e sao geradas sob demanda.
- **`is_explored` fica na celula.** O frontend precisa dele para escurecer lotes ja vasculhados sem pedir cada construcao.
