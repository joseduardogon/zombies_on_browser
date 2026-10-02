# simulation.py

Arquivo: `app/services/simulation.py`.

## O que e

O motor de tempo. Uma funcao, `advance_hour`, define a ordem de tudo o que acontece quando passa uma hora de jogo.

## Como foi feito

```python
    state.require_playing()
    state.clock.advance()
    hour = state.clock.hour

    if hour == balance.NIGHT_START_HOUR:
        zombie_service.start_night(state)
    if hour in balance.ASSAULT_HOURS:
        zombie_service.assault_round(state)
    if hour == balance.NIGHT_END_HOUR:
        zombie_service.end_night(state)

    survivor_service.update_needs_hour(state)
    expedition_service.advance_expeditions(state)
    _check_end(state)
```

A ordem importa:

1. **O relogio avanca primeiro**, e os eventos reagem a nova hora. Assim `hour == 20` dispara a onda exatamente quando o relogio marca 20h.
2. **Os zumbis agem antes das necessidades.** Um guarda que atira esta cansado quando as necessidades sao atualizadas; e quem morreu na invasao nao come mais naquela hora.
3. **As expedicoes por ultimo.** O retorno acontece depois do desgaste, entao quem volta no final da hora ja conta como presente na proxima.
4. **Fim de jogo ao final**, depois que mortes e passagem de dia ja foram resolvidas.

### Varias horas

```python
    for _ in range(hours):
        if state.status != GameStatus.PLAYING:
            break
        advance_hour(state)
```

`advance_hours` repete e **para** se a partida acabar. Sem isso, pedir 24 horas depois de perder continuaria a simular um jogo encerrado.

### Vitoria e derrota

```python
    if not state.alive_survivors():
        state.status = GameStatus.LOST
```

```python
    elif state.clock.day > balance.TARGET_DAY:
        state.status = GameStatus.WON
```

Perde-se quando morre o ultimo sobrevivente; ganha-se quando o dia passa do 30, ou seja, ao viver 30 dias e 30 noites completos.

## Por que assim

- **O servidor e quem manda no tempo.** O frontend apenas pede "avance 1 hora" em intervalos; todas as regras ficam no backend, e o jogo e igual qualquer que seja a velocidade escolhida.
- **Ticks explicitos, sem tarefa em segundo plano.** Uma thread simulando sozinha seria nao deterministica e dificil de testar. Com `POST /api/game/tick`, cada teste controla exatamente quantas horas passam.
- **Testes de tempo.** `test_clock_rolls_over_midnight`, `test_wave_arrives_at_dusk_and_ends_at_dawn` e `test_winning_after_target_day` cobrem as bordas dessa funcao.
