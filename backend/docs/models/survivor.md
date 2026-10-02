# survivor.py

Arquivo: `app/models/survivor.py`.

## O que e

O sobrevivente: nome, funcao, necessidades, habilidades, onde esta e se continua vivo. O modelo existia desde o inicio, mas nao era usado. Agora e a peca central da simulacao.

## Como foi feito

Foi acrescentado o status, que diz se o sobrevivente esta no abrigo, fora dele ou morto:

```python
class SurvivorStatus(str, Enum):
    HOME = "home"
    AWAY = "away"
    DEAD = "dead"
```

```python
class Survivor(BaseModel):
    id: str
    name: str
    role: SurvivorRole = SurvivorRole.IDLE
    status: SurvivorStatus = SurvivorStatus.HOME
    needs: SurvivorNeeds = Field(default_factory=SurvivorNeeds)
    skills: SurvivorSkills = Field(default_factory=SurvivorSkills)
    current_location: Coordinates | None = None
    assigned_building_id: str | None = None
```

Todas as necessidades comecam em 100:

```python
class SurvivorNeeds(BaseModel):
    hunger: float = 100.0
    thirst: float = 100.0
    fatigue: float = 100.0
    morale: float = 100.0
    health: float = 100.0
```

Note que `hunger` e `thirst` medem **saciedade**: 100 e saciado, 0 e faminto. O mesmo vale para `fatigue` (100 e descansado), de modo que todas as barras do frontend funcionam do mesmo jeito: cheia e bom, vazia e perigo.

## O que mudou

- **`status` em vez de varios campos booleanos.** Os tres valores sao mutuamente exclusivos. As regras filtram por status: apenas `HOME` defende o abrigo, e apenas `HOME` pode sair em expedicao.
- **O import de `Coordinates` agora e absoluto** (`from app.models.world import Coordinates`), igual ao resto do projeto.

## Por que assim

- **Morto continua na lista.** Um sobrevivente morto nao e removido de `GameState.survivors`: ele recebe `status = DEAD`. Isso preserva o historico para a tela de fim de jogo e evita reaproveitar identificadores.
- **`current_location` e opcional.** Fica `None` quando morto e e a celula da construcao alvo quando em expedicao.
