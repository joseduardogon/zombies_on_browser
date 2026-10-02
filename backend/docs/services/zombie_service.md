# zombie_service.py

Arquivo: `app/services/zombie_service.py`.

## O que e

O perigo noturno. Toda noite chega uma onda de zumbis que cerca o abrigo, e o jogador sobrevive pela combinacao de guardas, municao e barricadas.

## Como foi feito

### A onda

```python
    rng = state.rng("wave")
    day = state.clock.day
    size = balance.WAVE_BASE + int(day * balance.WAVE_PER_DAY) + rng.randint(0, day // 3)
    state.siege = Siege(wave_size=size)
```

O tamanho cresce com o dia (`3 + 2,2 * dia`), com uma variacao aleatoria que tambem cresce. A onda e anunciada as 20h no diario, para o jogador ter tempo de se preparar.

### Rodadas de ataque

A onda nao chega de uma vez: as 8 horas de `ASSAULT_HOURS` recebem um oitavo cada.

```python
    group = math.ceil(siege.wave_size / len(balance.ASSAULT_HOURS))
    arriving = min(group, siege.wave_size - siege.arrived)
    siege.arrived += arriving
    siege.at_gate += arriving
```

Os zumbis que ja chegaram e nao foram abatidos ficam no portao (`at_gate`) e se acumulam de rodada em rodada.

### Os guardas atiram

```python
        power = balance.GUARD_BASE_KILLS + guard.skills.combat // balance.GUARD_COMBAT_DIVISOR
        if state.resources.ammo > 0:
            state.resources.ammo -= 1
            power += balance.GUARD_AMMO_BONUS
        total += int(power * efficiency(guard))
        guard.needs.fatigue = clamp(guard.needs.fatigue - balance.GUARD_FATIGUE_COST)
```

Cada guarda apto (no abrigo, funcao GUARD, saude de pelo menos 20) abate `1 + combate // 2` zumbis; se gastar uma municao, abate mais 2. Guardas cansados ou desmoralizados rendem metade, e cada rodada custa 6 de energia.

### Os zumbis atacam a abertura mais fraca

```python
    intact = [
        a
        for room in base.rooms
        for a in room.apertures
        if a.state != ApertureState.BROKEN
    ]
    return min(intact, key=lambda a: a.health, default=None)
```

Os zumbis que sobraram concentram o ataque na abertura **intacta de menor saude**:

```python
        target.health = max(0, target.health - state.siege.at_gate * balance.ZOMBIE_DAMAGE)
        if target.health == 0:
            target.state = ApertureState.BROKEN
```

Cada zumbi no portao tira 4 pontos por rodada. Quando a saude chega a zero, a abertura quebra.

### Invasao

```python
    breached = any(
        a.state == ApertureState.BROKEN for room in base.rooms for a in room.apertures
    ) or not any(room.apertures for room in base.rooms)
    if breached:
        _intrude(state)
```

Se existe qualquer abertura quebrada, os zumbis do portao entram: cada um fere um sobrevivente do abrigo (de 4 a 10 de dano, no maximo 12 invasores por rodada) e todos perdem 8 de moral. Sobreviventes fora do abrigo, em expedicao, estao a salvo.

### Amanhecer

```python
    state.siege = Siege()
```

As 6h o cerco termina e os zumbis restantes recuam.

## Por que assim

- **Atacar a mais fraca.** Reforcar so a porta principal nao basta. O jogador precisa nivelar o abrigo, o que faz a barra de integridade (a media das aberturas) ser a metrica certa.
- **Zumbis que sobram acumulam.** Descuidar de uma rodada piora a seguinte, o que cria a sensacao de cerco.
- **Municao como recurso de pico.** Atirar gasta municao, mas aumenta muito o abate; guarda-la para as noites dificeis e uma decisao do jogador.
- **Equilibrio medido.** Dois jogadores automaticos simples (um com um guarda fixo, outro que aumenta os guardas conforme os dias passam) jogaram 12 partidas cada e venceram 7. Um humano que se adapta deve ir melhor; a dificuldade e alta, mas vencivel.
