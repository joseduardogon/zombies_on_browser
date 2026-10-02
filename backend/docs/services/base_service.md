# base_service.py

Arquivo: `app/services/base_service.py`.

## O que e

A acao de defesa do jogador: reforcar ou consertar portas e janelas do abrigo com madeira.

## Como foi feito

### Pre-condicoes

```python
    state.require_playing()
    base = base_building(state)
    found = find_aperture(base, aperture_id)
    if found is None:
        raise GameError("Aperture not found", 404)
```

```python
    if worker.status != SurvivorStatus.HOME:
        raise GameError(f"{worker.name} is not at the shelter")
    if aperture.health >= balance.APERTURE_HEALTH_CAP:
        raise GameError("This opening is already fully reinforced")
    if state.resources.wood < balance.BARRICADE_WOOD_COST:
        raise GameError("Not enough wood")
```

Somente aberturas do abrigo podem ser reforcadas; o trabalhador precisa estar la; ha um teto de 300 pontos; e o custo e 2 madeiras.

### O ganho

```python
    gain = balance.BARRICADE_BASE_HEALTH + balance.BARRICADE_HEALTH_PER_SKILL * worker.skills.construction
    if worker.role == SurvivorRole.BUILDER:
        gain = int(gain * balance.BUILDER_BONUS)
```

O ganho base e `20 + 8 * construcao`; quem esta na funcao CONSTRUTOR ganha 50% a mais. Escolher o trabalhador certo e uma decisao real: o lider (construcao 2) soma 36; um construtor com construcao 5 soma 90.

### O efeito

```python
    state.resources.wood -= balance.BARRICADE_WOOD_COST
    aperture.health = min(balance.APERTURE_HEALTH_CAP, aperture.health + gain)
    aperture.state = ApertureState.BARRICADED
    worker.needs.fatigue = clamp(worker.needs.fatigue - 4)
```

A madeira e gasta, a saude sobe (com teto), o estado vira `barricaded` e o trabalhador se cansa um pouco. Uma abertura **quebrada** tambem passa a `barricaded` com a saude somada: reforcar e consertar sao o mesmo gesto.

Por fim a integridade geral e recalculada com `recompute_integrity(base)`.

## Por que assim

- **Madeira como gargalo.** O jogador precisa equilibrar mandar gente buscar madeira (florestas e fabricas) com ficar em casa reforcando.
- **O trabalhador e escolhido.** Em vez de um clique anonimo, a acao exige um sobrevivente, de modo que habilidade, funcao e cansaco importem.
- **Sem reforco infinito.** O teto de 300 impede que uma unica porta bloqueie todas as ondas; o jogador precisa distribuir o reforco entre todas as aberturas, ja que os zumbis atacam sempre a mais fraca.
