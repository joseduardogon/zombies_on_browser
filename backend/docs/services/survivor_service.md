# survivor_service.py

Arquivo: `app/services/survivor_service.py`.

## O que e

Tudo o que acontece com uma pessoa ao longo do jogo: ser criada, sentir fome e sede, dormir, ficar ferida, ser tratada, mudar de funcao ou morrer.

## Como foi feito

### Desgaste por hora

```python
        needs.hunger = clamp(needs.hunger - balance.HUNGER_DECAY)
        needs.thirst = clamp(needs.thirst - balance.THIRST_DECAY)
        if at_home:
            _consume(state, survivor)
            if _is_sleeping(survivor, hour):
                needs.fatigue = clamp(needs.fatigue + balance.SLEEP_RECOVERY)
            else:
                needs.fatigue = clamp(needs.fatigue - balance.FATIGUE_DECAY_HOME)
        else:
            needs.fatigue = clamp(needs.fatigue - balance.FATIGUE_DECAY_AWAY)
```

A cada hora, fome e sede caem. Quem esta no abrigo come e bebe se necessario e dorme se for a hora do seu turno. Quem esta fora gasta mais energia (`3.0` contra `1.0`) e nao come: carregar comida na expedicao nao foi modelado.

`clamp` mantem todo valor entre 0 e 100.

### Comer e beber automaticos

```python
    if needs.hunger <= balance.EAT_THRESHOLD and state.resources.food > 0:
        state.resources.food -= 1
        needs.hunger = clamp(needs.hunger + balance.EAT_RESTORE)
```

O jogador nao precisa clicar para alimentar cada pessoa: quando a saciedade cai a 50 e ha comida, uma unidade e consumida e restaura 40 pontos. O jogo vira um problema de **abastecimento**, e nao de microgestao.

### Quem dorme quando

```python
    if survivor.role == SurvivorRole.GUARD:
        return hour in balance.GUARD_SLEEP_HOURS
    return hour in balance.SLEEP_HOURS
```

Guardas vigiam de noite e dormem de dia. Sem isso, a energia de um guarda so podia cair: ele nunca tinha uma janela de sono, porque o sono dos demais cai de madrugada, justo quando ele esta de vigia.

### Saude, moral e morte

```python
    if needs.hunger <= 0 or needs.thirst <= 0:
        needs.health = clamp(needs.health - balance.STARVATION_DAMAGE)
```

Fome ou sede zeradas tiram 3 de saude por hora; com saude zero, `kill_survivor` marca `status = DEAD`, tira a pessoa de qualquer expedicao e registra a morte no diario. A moral cai quando o sobrevivente sofre e sobe devagar quando esta bem.

### Eficiencia

```python
    tired = min(needs.morale, needs.fatigue) < balance.LOW_EFFICIENCY_LEVEL
    return balance.LOW_EFFICIENCY_FACTOR if tired else 1.0
```

Moral ou energia abaixo de 20 reduzem pela metade o rendimento na coleta e no tiro. E o elo entre as necessidades e as acoes: nao basta alimentar, e preciso descansar e manter o grupo animado.

### Habilidades

```python
    if current >= balance.SKILL_CAP or rng.random() >= balance.SKILL_GAIN_CHANCE:
        return False
    setattr(survivor.skills, skill, current + 1)
```

Cada uso (reforcar, coletar, enfrentar zumbis) tem 30% de chance de subir a habilidade, ate o nivel 10.

### Acoes do jogador

`set_role` troca a funcao e `treat` gasta um remedio:

```python
    best = max(s.skills.medicine for s in state.home_survivors())
    heal = balance.TREAT_BASE_HEAL + balance.TREAT_SKILL_HEAL * best
```

A cura usa a melhor habilidade de medicina entre quem esta no abrigo: ter um medico no grupo vale mais remedios bem aproveitados.

## Por que assim

- **Tudo em um passe por hora.** `update_needs_hour` percorre os vivos uma vez; as regras de fome, sono, saude e moral ficam lado a lado, o que facilita equilibrar.
- **Mortos nao somem.** `kill_survivor` troca o status e preserva a pessoa na lista.
- **Nomes sem repeticao.** `create_survivor` descarta nomes ja usados; se acabarem, cai em `Survivor N`.
