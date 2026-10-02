# balance.py

Arquivo: `app/core/balance.py`.

## O que e

Um modulo apenas de constantes. Nenhuma funcao, nenhum estado.

## Como foi feito

As constantes estao agrupadas por assunto. O tempo do jogo:

```python
START_DAY = 1
START_HOUR = 8
TARGET_DAY = 30

NIGHT_START_HOUR = 20
NIGHT_END_HOUR = 6
SLEEP_HOURS = (0, 1, 2, 3, 4, 5)
GUARD_SLEEP_HOURS = (9, 10, 11, 12, 13, 14)
ASSAULT_HOURS = (22, 23, 0, 1, 2, 3, 4, 5)
```

- A partida comeca as 8h do dia 1 e termina quando o dia passa de `TARGET_DAY`.
- A noite vai das 20h as 6h. A onda chega as 20h, mas os ataques so ocorrem nas horas de `ASSAULT_HOURS`: sao oito rodadas, e esse numero tambem divide a onda em grupos (ver [zombie_service](../services/zombie_service.md)).
- Guardas dormem de dia (`GUARD_SLEEP_HOURS`), porque vigiam de noite.

O desgaste dos sobreviventes:

```python
HUNGER_DECAY = 2.0
THIRST_DECAY = 3.0
FATIGUE_DECAY_HOME = 1.0
FATIGUE_DECAY_AWAY = 3.0
SLEEP_RECOVERY = 6.0
EAT_THRESHOLD = 50.0
DRINK_THRESHOLD = 50.0
EAT_RESTORE = 40.0
DRINK_RESTORE = 40.0
```

Com essas taxas, cada pessoa come uma vez a cada 25 horas e bebe uma vez a cada 17. Tres sobreviventes gastam cerca de 3 comidas e 4,5 aguas por dia, e o estoque inicial (12 e 12) dura em torno de quatro dias. Essa pressao e o que obriga o jogador a sair para coletar.

Os parametros de combate:

```python
WAVE_BASE = 3
WAVE_PER_DAY = 2.2
ZOMBIE_DAMAGE = 4
GUARD_MIN_HEALTH = 20.0
GUARD_BASE_KILLS = 1
GUARD_COMBAT_DIVISOR = 2
GUARD_AMMO_BONUS = 2
GUARD_FATIGUE_COST = 6.0
```

O estoque inicial e o dicionario de nomes:

```python
STARTING_RESOURCES = {
    "food": 12,
    "water": 12,
    "wood": 6,
    "scrap": 2,
    "medicine": 1,
    "ammo": 4,
}
```

`SECTOR_DANGER` associa cada setor a chance de encontrar zumbis numa expedicao e importa `SectorType` de `app.models.world`:

```python
SECTOR_DANGER = {
    SectorType.RESIDENTIAL: 0.2,
    SectorType.COMMERCIAL: 0.3,
    SectorType.INDUSTRIAL: 0.35,
    SectorType.FOREST: 0.15,
}
```

## Por que assim

- **Um unico lugar.** Ajustar a dificuldade e mudar numeros aqui. Os testes de balanceamento (um jogador automatico que joga 30 dias com varias politicas) usam esses mesmos valores.
- **`GUARD_COMBAT_DIVISOR = 2`.** Na primeira versao um guarda matava `1 + combate` zumbis. Um unico guarda vencia todas as 30 noites em todas as sementes testadas, o que tirava qualquer tensao. Dividir o combate por 2 faz o jogador precisar de mais guardas e de municao conforme as ondas crescem.
- **`WAVE_PER_DAY = 2.2`.** A onda do dia 1 tem cerca de 5 zumbis; a do dia 30, cerca de 70.
- **Dependencia unica de modelos.** `balance.py` so importa `SectorType`, para que `app.models.game` possa importar `balance` sem criar import circular.
