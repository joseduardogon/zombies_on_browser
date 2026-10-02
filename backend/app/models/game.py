"""Agregado de estado de uma partida."""

import random
from enum import Enum

from pydantic import BaseModel, Field, computed_field

from app.core import balance
from app.core.errors import GameError
from app.models.building import Building
from app.models.resources import Resources
from app.models.survivor import Survivor, SurvivorStatus
from app.models.world import Coordinates, WorldCell, WorldMap


class GameStatus(str, Enum):
    """Fase da partida."""

    SETUP = "setup"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


class LogKind(str, Enum):
    """Severidade de uma entrada do diario."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class LogEntry(BaseModel):
    """Entrada do diario de eventos.

    Attributes:
        day: Dia em que ocorreu.
        hour: Hora em que ocorreu.
        kind: Severidade.
        message: Texto do evento.
    """

    day: int
    hour: int
    kind: LogKind
    message: str


class Clock(BaseModel):
    """Relogio do jogo. Cada tick equivale a uma hora.

    Attributes:
        day: Dia atual, a partir de 1.
        hour: Hora atual, de 0 a 23.
        total_hours: Horas decorridas desde o inicio.
    """

    day: int = balance.START_DAY
    hour: int = balance.START_HOUR
    total_hours: int = 0

    @computed_field
    @property
    def phase(self) -> str:
        """Fase do dia.

        Returns:
            "night" entre as 20h e as 6h, "day" nas demais horas.
        """
        night = self.hour >= balance.NIGHT_START_HOUR or self.hour < balance.NIGHT_END_HOUR
        return "night" if night else "day"

    def advance(self) -> None:
        """Avanca o relogio em uma hora, virando o dia se necessario."""
        self.total_hours += 1
        self.hour += 1
        if self.hour >= 24:
            self.hour = 0
            self.day += 1


class Expedition(BaseModel):
    """Saida de um sobrevivente para vasculhar uma construcao.

    Attributes:
        id: Identificador da expedicao.
        survivor_id: Sobrevivente em campo.
        building_id: Construcao alvo.
        cell: Celula da construcao alvo.
        ticks_total: Duracao total em horas.
        ticks_remaining: Horas restantes ate a volta.
    """

    id: str
    survivor_id: str
    building_id: str
    cell: Coordinates
    ticks_total: int
    ticks_remaining: int


class Siege(BaseModel):
    """Cerco zumbi da noite atual.

    Attributes:
        wave_size: Total de zumbis previstos para a noite.
        arrived: Quantos ja chegaram ao abrigo.
        at_gate: Quantos estao atacando agora.
        killed: Quantos foram abatidos nesta noite.
    """

    wave_size: int = 0
    arrived: int = 0
    at_gate: int = 0
    killed: int = 0


class GameState(BaseModel):
    """Estado completo de uma partida.

    Attributes:
        id: Identificador da partida.
        seed: Semente que torna a geracao reproduzivel.
        rng_counter: Contador que diferencia sorteios sucessivos.
        status: Fase da partida.
        clock: Relogio do jogo.
        world: Mapa da cidade.
        buildings: Construcoes ja geradas, por identificador.
        survivors: Todos os sobreviventes, vivos ou mortos.
        resources: Estoque do abrigo.
        base_building_id: Construcao escolhida como abrigo.
        base_cell: Celula do abrigo.
        expeditions: Expedicoes em andamento.
        siege: Cerco da noite atual.
        log: Diario de eventos, do mais antigo ao mais recente.
        total_zombies_killed: Zumbis abatidos na partida.
        next_survivor_id: Proximo numero de sobrevivente.
        next_expedition_id: Proximo numero de expedicao.
    """

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
    total_zombies_killed: int = 0
    next_survivor_id: int = 1
    next_expedition_id: int = 1

    def rng(self, purpose: str) -> random.Random:
        """Cria um gerador aleatorio deterministico para um sorteio.

        Cada chamada incrementa `rng_counter`, de modo que a mesma partida
        com as mesmas acoes sempre produz o mesmo resultado.

        Args:
            purpose: Rotulo do sorteio, misturado na semente.

        Returns:
            Gerador semeado com a semente, o contador e o rotulo.
        """
        self.rng_counter += 1
        return random.Random(f"{self.seed}:{self.rng_counter}:{purpose}")

    def add_log(self, kind: LogKind, message: str) -> None:
        """Registra um evento no diario, descartando os mais antigos.

        Args:
            kind: Severidade do evento.
            message: Texto do evento.
        """
        self.log.append(
            LogEntry(day=self.clock.day, hour=self.clock.hour, kind=kind, message=message)
        )
        del self.log[: -balance.LOG_LIMIT]

    def find_survivor(self, survivor_id: str) -> Survivor:
        """Busca um sobrevivente pelo identificador.

        Args:
            survivor_id: Identificador procurado.

        Returns:
            O sobrevivente encontrado.

        Raises:
            GameError: Com status 404 se nao existir.
        """
        for survivor in self.survivors:
            if survivor.id == survivor_id:
                return survivor
        raise GameError("Survivor not found", 404)

    def alive_survivors(self) -> list[Survivor]:
        """Lista os sobreviventes vivos.

        Returns:
            Sobreviventes cujo status nao e DEAD.
        """
        return [s for s in self.survivors if s.status != SurvivorStatus.DEAD]

    def home_survivors(self) -> list[Survivor]:
        """Lista os sobreviventes presentes no abrigo.

        Returns:
            Sobreviventes com status HOME.
        """
        return [s for s in self.survivors if s.status == SurvivorStatus.HOME]

    def cell_for_building(self, building_id: str) -> WorldCell:
        """Busca a celula que contem uma construcao.

        Args:
            building_id: Identificador da construcao.

        Returns:
            A celula correspondente.

        Raises:
            GameError: Com status 404 se nenhuma celula tiver a construcao.
        """
        for cell in self.world.cells:
            if cell.building_id == building_id:
                return cell
        raise GameError("Building not found", 404)

    def require_playing(self) -> None:
        """Garante que a partida esta em andamento.

        Raises:
            GameError: Com status 409 se a partida nao estiver em andamento.
        """
        if self.status != GameStatus.PLAYING:
            raise GameError(f"Game is not in progress ({self.status.value})", 409)
