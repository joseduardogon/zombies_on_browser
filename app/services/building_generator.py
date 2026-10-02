"""Geracao procedural de construcoes."""

import uuid

from app.models.building import Aperture, ApertureState, Building, Room, RoomType


def _aperture(kind: str, state: ApertureState, health: int) -> Aperture:
    """Cria uma abertura com identificador unico.

    Args:
        kind: "door" ou "window".
        state: Estado inicial.
        health: Durabilidade inicial.

    Returns:
        A abertura criada.
    """
    return Aperture(id=str(uuid.uuid4()), type=kind, state=state, health=health)


class BuildingGenerator:
    """Fabrica de construcoes por tipo."""

    @staticmethod
    def generate_residential(building_id: str) -> Building:
        """Gera uma casa com sala, cozinha e quarto.

        Args:
            building_id: Identificador da construcao.

        Returns:
            A casa gerada.
        """
        rooms = [
            Room(
                id=str(uuid.uuid4()),
                name="Living Room",
                type=RoomType.LIVING_ROOM,
                dimensions={"width": 5, "length": 5},
                apertures=[
                    _aperture("door", ApertureState.CLOSED, 100),
                    _aperture("window", ApertureState.CLOSED, 50),
                ],
                insulation=50,
                security=20,
            ),
            Room(
                id=str(uuid.uuid4()),
                name="Kitchen",
                type=RoomType.KITCHEN,
                dimensions={"width": 4, "length": 4},
                apertures=[_aperture("window", ApertureState.CLOSED, 50)],
                insulation=40,
                security=20,
            ),
            Room(
                id=str(uuid.uuid4()),
                name="Master Bedroom",
                type=RoomType.BEDROOM,
                dimensions={"width": 4, "length": 5},
                apertures=[_aperture("window", ApertureState.CLOSED, 50)],
                insulation=60,
                security=30,
            ),
        ]
        return Building(
            id=building_id,
            type="residential",
            rooms=rooms,
            overall_integrity=100,
        )

    @staticmethod
    def generate_industrial(building_id: str) -> Building:
        """Gera uma fabrica com um unico galpao.

        Args:
            building_id: Identificador da construcao.

        Returns:
            A fabrica gerada.
        """
        factory_floor = Room(
            id=f"{building_id}_r1",
            name="Factory Floor",
            type=RoomType.INDUSTRIAL,
            dimensions={"width": 20, "length": 30},
            apertures=[
                _aperture("door", ApertureState.CLOSED, 200),
                _aperture("window", ApertureState.CLOSED, 20),
            ],
        )
        return Building(
            id=building_id,
            type="industrial",
            rooms=[factory_floor],
            overall_integrity=90,
        )

    @staticmethod
    def generate_forest(building_id: str) -> Building:
        """Gera uma clareira com uma barraca abandonada.

        Args:
            building_id: Identificador da construcao.

        Returns:
            O acampamento gerado.
        """
        clearing = Room(
            id=f"{building_id}_r1",
            name="Forest Clearing",
            type=RoomType.OUTDOOR,
            dimensions={"width": 10, "length": 10},
        )
        tent = Room(
            id=f"{building_id}_r2",
            name="Abandoned Tent",
            type=RoomType.SHELTER,
            dimensions={"width": 3, "length": 3},
            apertures=[_aperture("door", ApertureState.OPEN, 5)],
        )
        return Building(
            id=building_id,
            type="forest",
            rooms=[clearing, tent],
            overall_integrity=10,
        )

    @staticmethod
    def generate_commercial(building_id: str) -> Building:
        """Gera uma loja de salao unico com porta de vidro e vitrine.

        Args:
            building_id: Identificador da construcao.

        Returns:
            A loja gerada.
        """
        main_floor = Room(
            id=str(uuid.uuid4()),
            name="Main Floor",
            type=RoomType.LIVING_ROOM,
            dimensions={"width": 10, "length": 10},
            apertures=[
                _aperture("door", ApertureState.CLOSED, 200),
                _aperture("window", ApertureState.CLOSED, 20),
            ],
        )
        return Building(
            id=building_id,
            type="commercial",
            rooms=[main_floor],
            overall_integrity=80,
        )
