"""Modelos de sobreviventes."""

from enum import Enum

from pydantic import BaseModel, Field

from app.models.world import Coordinates


class SurvivorRole(str, Enum):
    """Funcoes que um sobrevivente pode exercer."""

    LEADER = "leader"
    SCAVENGER = "scavenger"
    BUILDER = "builder"
    GUARD = "guard"
    IDLE = "idle"


class SurvivorStatus(str, Enum):
    """Situacao de um sobrevivente."""

    HOME = "home"
    AWAY = "away"
    DEAD = "dead"


class SurvivorNeeds(BaseModel):
    """Necessidades de um sobrevivente, de 0 a 100.

    Attributes:
        hunger: Saciedade de fome.
        thirst: Saciedade de sede.
        fatigue: Disposicao fisica.
        morale: Moral.
        health: Saude.
    """

    hunger: float = 100.0
    thirst: float = 100.0
    fatigue: float = 100.0
    morale: float = 100.0
    health: float = 100.0


class SurvivorSkills(BaseModel):
    """Niveis de habilidade de um sobrevivente.

    Attributes:
        construction: Construcao.
        combat: Combate.
        scavenging: Coleta.
        medicine: Medicina.
    """

    construction: int = 1
    combat: int = 1
    scavenging: int = 1
    medicine: int = 1


class Survivor(BaseModel):
    """Sobrevivente do grupo.

    Attributes:
        id: Identificador.
        name: Nome.
        role: Funcao atual.
        status: Se esta no abrigo, em expedicao ou morto.
        needs: Necessidades.
        skills: Habilidades.
        current_location: Posicao no mapa.
        assigned_building_id: Construcao em que esta alocado.
    """

    id: str
    name: str
    role: SurvivorRole = SurvivorRole.IDLE
    status: SurvivorStatus = SurvivorStatus.HOME
    needs: SurvivorNeeds = Field(default_factory=SurvivorNeeds)
    skills: SurvivorSkills = Field(default_factory=SurvivorSkills)
    current_location: Coordinates | None = None
    assigned_building_id: str | None = None
