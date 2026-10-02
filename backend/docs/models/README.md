# Modulo models

Pasta: `app/models/`. Modelos Pydantic do dominio. Sao tambem os esquemas de resposta da API, por isso o frontend espelha esses tipos em `src/types/game.ts`.

| Arquivo | Documento | Conteudo |
|---------|-----------|----------|
| `world.py` | [world](world.md) | `Coordinates`, `SectorType`, `WorldCell`, `WorldMap` |
| `building.py` | [building](building.md) | Construcoes, comodos, aberturas, pilhagem |
| `survivor.py` | [survivor](survivor.md) | Sobreviventes, necessidades, habilidades, status |
| `resources.py` | [resources](resources.md) | O estoque do abrigo e a pilhagem |
| `game.py` | [game](game.md) | O agregado `GameState` e tudo que ele contem |

## Regra de dependencia

Os modelos nao importam servicos nem rotas. As unicas dependencias entre eles sao:

```
world  <-  survivor
resources  <-  building
world, building, survivor, resources, core.balance, core.errors  <-  game
```

Isso evita imports circulares e mantem os modelos faceis de testar isoladamente.
