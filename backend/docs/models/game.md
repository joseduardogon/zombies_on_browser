# game.py

Arquivo: `app/models/game.py`.

## O que e

O agregado `GameState`: tudo o que e preciso para descrever uma partida do inicio ao fim. Serializar esse objeto em JSON e o save; le-lo de volta e o load.

## Como foi feito

### O estado

```python
class GameState(BaseModel):
    id: str
    seed: int
    rng_counter: int = 0
    status: GameStatus = GameStatus.SETUP
    clock: Clock = Field(default_factory=Clock)
    world: WorldMap
    buildings: dict[str, Building] = Field(default_factory=dict)
    survivors: list[Survivor] = Field(default_factory=list)
    resources: Resources = Field(default_factory=Resources)
    base_building_id: str | None = None
    base_cell: Coordinates | None = None
    expeditions: list[Expedition] = Field(default_factory=list)
    siege: Siege = Field(default_factory=Siege)
    log: list[LogEntry] = Field(default_factory=list)
```

`status` percorre `SETUP` (escolhendo o abrigo), `PLAYING`, e termina em `WON` ou `LOST`.

### O relogio

```python
class Clock(BaseModel):
    day: int = balance.START_DAY
    hour: int = balance.START_HOUR
    total_hours: int = 0

    @computed_field
    @property
    def phase(self) -> str:
        night = self.hour >= balance.NIGHT_START_HOUR or self.hour < balance.NIGHT_END_HOUR
        return "night" if night else "day"

    def advance(self) -> None:
        self.total_hours += 1
        self.hour += 1
        if self.hour >= 24:
            self.hour = 0
            self.day += 1
```

Cada tick e uma hora. `phase` e um `computed_field`: nao e armazenado, mas aparece no JSON enviado ao frontend, que assim nao precisa repetir a regra de que a noite vai das 20h as 6h.

### Aleatoriedade deterministica

```python
    def rng(self, purpose: str) -> random.Random:
        self.rng_counter += 1
        return random.Random(f"{self.seed}:{self.rng_counter}:{purpose}")
```

Em vez de guardar um gerador aleatorio (que nao serializa), o estado guarda a **semente** e um **contador**. Cada sorteio cria um `Random` novo a partir de `semente:contador:rotulo`. Consequencias:

- a partida inteira se reconstroi do JSON, inclusive os sorteios futuros;
- duas partidas com a mesma semente e as mesmas acoes dao o mesmo resultado (teste `test_same_seed_and_actions_give_same_result`);
- o rotulo (`"wave"`, `"expedition"`, `"intrusion"`) deixa cada sorteio independente dos demais.

### Diario

```python
        self.log.append(
            LogEntry(day=self.clock.day, hour=self.clock.hour, kind=kind, message=message)
        )
        del self.log[: -balance.LOG_LIMIT]
```

O diario guarda no maximo 200 entradas. O `del self.log[: -LIMITE]` descarta as mais antigas; com menos de 200 entradas a fatia e vazia e nada acontece.

### Auxiliares

`find_survivor`, `alive_survivors`, `home_survivors` e `cell_for_building` evitam que cada servico repita o mesmo laco. `require_playing` e a trava usada por toda acao:

```python
        if self.status != GameStatus.PLAYING:
            raise GameError(f"Game is not in progress ({self.status.value})", 409)
```

## Por que assim

- **Um objeto so.** Com tudo em `GameState`, salvar e carregar sao uma linha cada, e os testes montam qualquer cenario alterando campos.
- **`Expedition` e `Siege` como modelos proprios.** A expedicao registra `ticks_total` e `ticks_remaining` (o frontend mostra "2h left"). O cerco registra `arrived`, `at_gate` e `killed`, que alimentam o banner vermelho durante a noite.
- **Sem `Random` guardado.** Era a alternativa mais simples, mas quebraria o save/load: ao retomar, a sequencia de sorteios recomecaria de outro ponto.
