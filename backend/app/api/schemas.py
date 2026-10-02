"""Esquemas de requisicao e resposta da API."""

from pydantic import BaseModel, Field

from app.core import balance
from app.models.building import Building
from app.models.game import Clock, Expedition, GameState, GameStatus, LogEntry, Siege
from app.models.resources import Resources
from app.models.survivor import Survivor, SurvivorRole
from app.models.world import Coordinates, WorldMap
from app.services.building_service import get_or_create_building


class NewGameRequest(BaseModel):
    """Pedido de nova partida.

    Attributes:
        width: Largura do mapa em celulas.
        height: Altura do mapa em celulas.
        seed: Semente opcional para repetir uma partida.
    """

    width: int = 20
    height: int = 20
    seed: int | None = None


class TickRequest(BaseModel):
    """Pedido de passagem de tempo.

    Attributes:
        hours: Horas a avancar, de 1 a 24.
    """

    hours: int = Field(default=1, ge=1, le=24)


class SlotRequest(BaseModel):
    """Pedido de salvar ou carregar um espaco.

    Attributes:
        slot: Nome do espaco de salvamento.
    """

    slot: str = Field(default="manual", min_length=1, max_length=40)


class ClaimBaseRequest(BaseModel):
    """Escolha do abrigo.

    Attributes:
        building_id: Construcao escolhida.
    """

    building_id: str


class ReinforceRequest(BaseModel):
    """Pedido de reforco de uma abertura.

    Attributes:
        aperture_id: Abertura a reforcar.
        survivor_id: Sobrevivente que faz o trabalho.
    """

    aperture_id: str
    survivor_id: str


class RoleRequest(BaseModel):
    """Mudanca de funcao.

    Attributes:
        role: Nova funcao.
    """

    role: SurvivorRole


class ExpeditionRequest(BaseModel):
    """Pedido de expedicao.

    Attributes:
        survivor_id: Sobrevivente que vai.
        building_id: Construcao alvo.
    """

    survivor_id: str
    building_id: str


class GameView(BaseModel):
    """Visao da partida enviada ao cliente.

    Reune tudo o que a interface precisa em uma unica resposta. As
    construcoes distantes ficam de fora e sao pedidas sob demanda.

    Attributes:
        id: Identificador da partida.
        seed: Semente da partida.
        status: Fase da partida.
        clock: Relogio do jogo.
        target_day: Dia que precisa ser alcancado para vencer.
        world: Mapa da cidade.
        survivors: Todos os sobreviventes.
        resources: Estoque do abrigo.
        base_building: Construcao do abrigo, se ja escolhido.
        base_cell: Celula do abrigo.
        expeditions: Expedicoes em andamento.
        siege: Cerco da noite atual.
        log: Diario de eventos.
        total_zombies_killed: Zumbis abatidos na partida.
    """

    id: str
    seed: int
    status: GameStatus
    clock: Clock
    target_day: int
    world: WorldMap
    survivors: list[Survivor]
    resources: Resources
    base_building: Building | None
    base_cell: Coordinates | None
    expeditions: list[Expedition]
    siege: Siege
    log: list[LogEntry]
    total_zombies_killed: int


def build_view(state: GameState) -> GameView:
    """Converte a partida na visao enviada ao cliente.

    Args:
        state: Partida corrente.

    Returns:
        A visao correspondente.
    """
    base = state.buildings.get(state.base_building_id) if state.base_building_id else None
    return GameView(
        id=state.id,
        seed=state.seed,
        status=state.status,
        clock=state.clock,
        target_day=balance.TARGET_DAY,
        world=state.world,
        survivors=state.survivors,
        resources=state.resources,
        base_building=base,
        base_cell=state.base_cell,
        expeditions=state.expeditions,
        siege=state.siege,
        log=state.log,
        total_zombies_killed=state.total_zombies_killed,
    )


def build_building_view(state: GameState, building_id: str) -> Building:
    """Prepara uma construcao para o cliente, escondendo o que nao foi descoberto.

    Args:
        state: Partida corrente.
        building_id: Identificador da construcao.

    Returns:
        Copia da construcao. A pilhagem e o sobrevivente isolado so aparecem
        depois que o local foi vasculhado.
    """
    building = get_or_create_building(state, building_id)
    if building.searched:
        return building.model_copy(update={"survivor_present": False})
    return building.model_copy(update={"loot": Resources(), "survivor_present": False})
