# expedition_service.py

Arquivo: `app/services/expedition_service.py`.

## O que e

As saidas de coleta. Um sobrevivente deixa o abrigo, viaja ate uma construcao, a vasculha e volta com recursos, correndo o risco de encontrar zumbis.

## Como foi feito

### Duracao

```python
    base = state.base_cell
    distance = abs(base.x - target_x) + abs(base.y - target_y)
    return max(1, math.ceil(distance / balance.TILES_PER_HOUR))
```

A distancia e a de Manhattan (celulas na horizontal mais celulas na vertical), e a viagem anda 3 celulas por hora. A expedicao inteira dura ida, busca e volta:

```python
    one_way = travel_hours(state, cell.coordinates.x, cell.coordinates.y)
    total = 2 * one_way + balance.SEARCH_HOURS
```

### Partida

```python
    survivor.status = SurvivorStatus.AWAY
    survivor.current_location = cell.coordinates
```

O sobrevivente passa a `AWAY`: deixa de defender o abrigo e de trabalhar. As recusas sao: quem nao esta em casa, quem tem menos de 25 de saude (`"is too hurt to leave"`) e o proprio abrigo (`"The shelter cannot be scavenged"`).

### Andamento e conclusao

```python
        expedition.ticks_remaining -= 1
        if expedition.ticks_remaining <= 0:
            finished.append(expedition)
```

A cada hora `advance_expeditions` desconta uma hora e conclui as que chegaram a zero.

### Encontro com zumbis

```python
    danger = balance.SECTOR_DANGER[cell.sector_type]
    if state.clock.phase == "night":
        danger += balance.NIGHT_DANGER_BONUS

    if rng.random() < danger:
```

A chance depende do setor (20% a 35%) e sobe 20 pontos se o retorno acontece a noite. Em caso de encontro, o dano e sorteado entre 10 e 35 e reduzido em `2 * combate`; se a saude chega a zero o sobrevivente morre e a pilhagem se perde.

### Pilhagem

```python
    fraction = balance.BASE_LOOT_FRACTION + balance.LOOT_FRACTION_PER_SKILL * survivor.skills.scavenging
    if survivor.role == SurvivorRole.SCAVENGER:
        fraction += balance.SCAVENGER_LOOT_BONUS
    return min(1.0, fraction * efficiency(survivor))
```

Leva-se de 50% (mais 10% por nivel de coleta, mais 10% se a funcao for COLETOR) do que ainda resta, multiplicado pela eficiencia. O que sobra fica na construcao para uma segunda visita:

```python
    building.loot.subtract(taken)
    building.searched = True
    cell.is_explored = True
    state.resources.add(taken)
```

### Novos sobreviventes

```python
    if building.survivor_present:
        building.survivor_present = False
        if len(state.alive_survivors()) < balance.MAX_SURVIVORS:
            newcomer = create_survivor(state, rng)
```

Se a construcao escondia alguem, essa pessoa se junta ao grupo. O grupo tem teto de 12.

## Por que assim

- **Risco e retorno.** Longe e perigoso rende o mesmo que perto e seguro, mas gasta mais horas; o jogador decide se vale a pena.
- **Ausencia tem custo.** Enquanto um sobrevivente esta fora, nao pode ser guarda; mandar o coletor a noite deixa o abrigo sem ele.
- **Pilhagem finita.** Cada construcao tem uma quantidade limitada; explorar cada vez mais longe e inevitavel.
- **Deterministico.** O sorteio usa `state.rng("expedition")`; com a mesma semente e as mesmas acoes, o resultado e o mesmo.
