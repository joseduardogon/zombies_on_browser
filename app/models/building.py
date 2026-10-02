"""Modelos de construcoes, comodos e aberturas."""

from enum import Enum

from pydantic import BaseModel


class RoomType(str, Enum):
    """Tipos de comodo."""

    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    GARAGE = "garage"
    STORAGE = "storage"
    INDUSTRIAL = "industrial"
    OUTDOOR = "outdoor"
    SHELTER = "shelter"
    EMPTY = "empty"


class ApertureState(str, Enum):
    """Estados possiveis de uma abertura."""

    OPEN = "open"
    CLOSED = "closed"
    BARRICADED = "barricaded"
    BROKEN = "broken"


class Aperture(BaseModel):
    """Porta ou janela de um comodo.

    Attributes:
        id: Identificador da abertura.
        type: "window" ou "door".
        state: Estado atual.
        health: Durabilidade da porta ou da barricada.
    """

    id: str
    type: str
    state: ApertureState
    health: int


class Room(BaseModel):
    """Comodo de uma construcao.

    Attributes:
        id: Identificador do comodo.
        name: Nome de exibicao.
        type: Tipo do comodo.
        dimensions: Dimensoes com as chaves "width" e "length".
        apertures: Portas e janelas do comodo.
        insulation: Isolamento termico.
        security: Nivel de seguranca.
    """

    id: str
    name: str
    type: RoomType
    dimensions: dict[str, int]
    apertures: list[Aperture] = []
    insulation: int = 0
    security: int = 0


class Building(BaseModel):
    """Construcao explorada pelo jogador.

    Attributes:
        id: Identificador da construcao.
        type: Categoria da construcao.
        rooms: Comodos que a compoem.
        overall_integrity: Integridade geral.
    """

    id: str
    type: str
    rooms: list[Room]
    overall_integrity: int
