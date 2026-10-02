# game_factory.py

Arquivo: `app/services/game_factory.py`.

## O que e

Cria uma partida nova e, depois que o jogador escolhe o abrigo, a coloca em andamento.

## Como foi feito

### Nova partida

```python
    if seed is None:
        seed = random.SystemRandom().randrange(1, 2**31)
    world = generate_world(width, height, random.Random(f"{seed}:world"))
    state = GameState(id=str(uuid.uuid4()), seed=seed, world=world)
    state.add_log(LogKind.INFO, "Choose a building to serve as your shelter.")
```

Sem semente, uma e sorteada com `SystemRandom` (aleatoriedade do sistema operacional). A semente e guardada em `state.seed`, entao qualquer partida pode ser repetida pedindo a mesma semente. A partida nasce em `SETUP`, sem sobreviventes: o jogador precisa escolher o abrigo.

### Escolha do abrigo

```python
    if cell.sector_type not in SHELTER_SECTORS:
        raise GameError("This location cannot serve as a shelter")
```

So casas, lojas e fabricas servem. Floresta nao tem paredes. Em seguida:

```python
    building = get_or_create_building(state, building_id)
    building.searched = True
    building.loot = Resources()
    building.survivor_present = False
    recompute_integrity(building)
    cell.is_explored = True
```

O abrigo ja nasce como vasculhado e sem pilhagem: o jogador vive la, nao o saqueia. A integridade e calculada na hora, porque o valor fixo do gerador (100) ignora a saude real das aberturas.

### Grupo inicial

```python
    create_survivor(state, rng, SurvivorRole.LEADER, SurvivorSkills(
        construction=2, combat=2, scavenging=2, medicine=2))
    create_survivor(state, rng, SurvivorRole.GUARD, SurvivorSkills(
        construction=1, combat=3, scavenging=1, medicine=1))
    create_survivor(state, rng, SurvivorRole.SCAVENGER, SurvivorSkills(
        construction=1, combat=1, scavenging=3, medicine=1))
```

Tres sobreviventes com papeis distintos: um lider equilibrado, um guarda forte em combate e um coletor forte em coleta. Os nomes sao sorteados da lista em `balance.SURVIVOR_NAMES`.

## Por que assim

- **A escolha do abrigo e parte do jogo.** Uma fabrica tem portas pesadas, mas pouca comida por perto; uma loja tem vitrines frageis; uma casa e equilibrada e pode ter garagem. Essa decisao inicial muda toda a partida.
- **O erro 409.** Se `claim_base` for chamada com a partida ja iniciada, levanta `GameError("The shelter has already been chosen", 409)`, impedindo trocar de abrigo no meio do jogo.
- **Semente de mundo separada.** `random.Random(f"{seed}:world")` mantem o mapa igual para a mesma semente, mesmo que outras partes das regras mudem.
