"""Geracao procedural de construcoes."""

import random
from typing import Callable

from app.core import balance
from app.models.building import Aperture, ApertureState, Building, Room, RoomType
from app.models.resources import Resources

LOOT_RANGES: dict[str, dict[str, tuple[int, int]]] = {
    "residential": {
        "food": (2, 6),
        "water": (2, 5),
        "wood": (0, 3),
        "scrap": (0, 2),
        "medicine": (0, 2),
        "ammo": (0, 3),
    },
    "commercial": {
        "food": (4, 10),
        "water": (3, 8),
        "wood": (0, 1),
        "scrap": (1, 4),
        "medicine": (0, 3),
        "ammo": (0, 4),
    },
    "industrial": {
        "food": (0, 2),
        "water": (0, 2),
        "wood": (2, 6),
        "scrap": (5, 12),
        "medicine": (0, 1),
        "ammo": (0, 4),
    },
    "forest": {
        "food": (1, 4),
        "water": (2, 5),
        "wood": (4, 10),
        "scrap": (0, 1),
        "medicine": (0, 1),
        "ammo": (0, 1),
    },
}


def roll_loot(kind: str, rng: random.Random) -> Resources:
    """Sorteia os recursos disponiveis em uma construcao.

    Args:
        kind: Tipo da construcao.
        rng: Gerador aleatorio.

    Returns:
        Os recursos sorteados conforme `LOOT_RANGES`.
    """
    return Resources(
        **{name: rng.randint(low, high) for name, (low, high) in LOOT_RANGES[kind].items()}
    )


class _RoomFactory:
    """Cria comodos e aberturas com identificadores previsiveis.

    Attributes:
        building_id: Construcao a que os comodos pertencem.
    """

    def __init__(self, building_id: str) -> None:
        """Inicia a fabrica.

        Args:
            building_id: Identificador da construcao.
        """
        self.building_id = building_id
        self._rooms = 0

    def aperture(self, kind: str, room_id: str, index: int, health: int) -> Aperture:
        """Cria uma abertura fechada.

        Args:
            kind: "door" ou "window".
            room_id: Comodo da abertura.
            index: Posicao da abertura no comodo.
            health: Durabilidade inicial.

        Returns:
            A abertura criada.
        """
        return Aperture(
            id=f"{room_id}_a{index}",
            type=kind,
            state=ApertureState.CLOSED,
            health=health,
        )

    def room(
        self,
        name: str,
        room_type: RoomType,
        size: tuple[int, int],
        openings: list[tuple[str, int]],
        insulation: int = 0,
        security: int = 0,
    ) -> Room:
        """Cria um comodo.

        Args:
            name: Nome de exibicao.
            room_type: Tipo do comodo.
            size: Largura e comprimento.
            openings: Pares (tipo, durabilidade) das aberturas.
            insulation: Isolamento termico.
            security: Nivel de seguranca.

        Returns:
            O comodo criado.
        """
        self._rooms += 1
        room_id = f"{self.building_id}_r{self._rooms}"
        return Room(
            id=room_id,
            name=name,
            type=room_type,
            dimensions={"width": size[0], "length": size[1]},
            apertures=[
                self.aperture(kind, room_id, i + 1, health)
                for i, (kind, health) in enumerate(openings)
            ],
            insulation=insulation,
            security=security,
        )


class BuildingGenerator:
    """Fabrica de construcoes por tipo."""

    @staticmethod
    def _finish(
        building_id: str,
        kind: str,
        rooms: list[Room],
        integrity: int,
        rng: random.Random,
    ) -> Building:
        """Monta a construcao com sua pilhagem e chance de sobrevivente.

        Args:
            building_id: Identificador da construcao.
            kind: Tipo da construcao.
            rooms: Comodos ja criados.
            integrity: Integridade inicial.
            rng: Gerador aleatorio.

        Returns:
            A construcao completa.
        """
        return Building(
            id=building_id,
            type=kind,
            rooms=rooms,
            overall_integrity=integrity,
            loot=roll_loot(kind, rng),
            survivor_present=rng.random() < balance.SURVIVOR_CHANCE[kind],
        )

    @staticmethod
    def generate_residential(building_id: str, rng: random.Random) -> Building:
        """Gera uma casa com sala, cozinha, quartos e, talvez, garagem.

        Args:
            building_id: Identificador da construcao.
            rng: Gerador aleatorio.

        Returns:
            A casa gerada.
        """
        factory = _RoomFactory(building_id)
        rooms = [
            factory.room(
                "Living Room", RoomType.LIVING_ROOM, (5, 5),
                [("door", 100), ("window", 50)], insulation=50, security=20,
            ),
            factory.room(
                "Kitchen", RoomType.KITCHEN, (4, 4),
                [("window", 50)], insulation=40, security=20,
            ),
            factory.room(
                "Master Bedroom", RoomType.BEDROOM, (4, 5),
                [("window", 50)], insulation=60, security=30,
            ),
        ]
        if rng.random() < 0.5:
            rooms.append(
                factory.room(
                    "Guest Bedroom", RoomType.BEDROOM, (3, 4),
                    [("window", 40)], insulation=55, security=25,
                )
            )
        if rng.random() < 0.4:
            rooms.append(
                factory.room(
                    "Garage", RoomType.GARAGE, (5, 6),
                    [("door", 150)], insulation=20, security=15,
                )
            )
        return BuildingGenerator._finish(building_id, "residential", rooms, 100, rng)

    @staticmethod
    def generate_commercial(building_id: str, rng: random.Random) -> Building:
        """Gera uma loja com salao de vendas e deposito.

        Args:
            building_id: Identificador da construcao.
            rng: Gerador aleatorio.

        Returns:
            A loja gerada.
        """
        factory = _RoomFactory(building_id)
        rooms = [
            factory.room(
                "Sales Floor", RoomType.LIVING_ROOM, (10, 10),
                [("door", 200), ("window", 20), ("window", 20)],
            ),
            factory.room(
                "Back Storage", RoomType.STORAGE, (5, 5),
                [("door", 120)], security=30,
            ),
        ]
        return BuildingGenerator._finish(building_id, "commercial", rooms, 80, rng)

    @staticmethod
    def generate_industrial(building_id: str, rng: random.Random) -> Building:
        """Gera uma fabrica com galpao e deposito de pecas.

        Args:
            building_id: Identificador da construcao.
            rng: Gerador aleatorio.

        Returns:
            A fabrica gerada.
        """
        factory = _RoomFactory(building_id)
        rooms = [
            factory.room(
                "Factory Floor", RoomType.INDUSTRIAL, (20, 30),
                [("door", 200), ("window", 20)],
            ),
            factory.room(
                "Parts Storage", RoomType.STORAGE, (6, 8),
                [("door", 150)], security=40,
            ),
        ]
        return BuildingGenerator._finish(building_id, "industrial", rooms, 90, rng)

    @staticmethod
    def generate_forest(building_id: str, rng: random.Random) -> Building:
        """Gera uma clareira com uma barraca abandonada.

        Args:
            building_id: Identificador da construcao.
            rng: Gerador aleatorio.

        Returns:
            O acampamento gerado.
        """
        factory = _RoomFactory(building_id)
        rooms = [
            factory.room("Forest Clearing", RoomType.OUTDOOR, (10, 10), []),
            factory.room("Abandoned Tent", RoomType.SHELTER, (3, 3), [("door", 5)]),
        ]
        return BuildingGenerator._finish(building_id, "forest", rooms, 10, rng)

    @staticmethod
    def generate(kind: str, building_id: str, rng: random.Random) -> Building:
        """Gera uma construcao do tipo pedido.

        Args:
            kind: "residential", "commercial", "industrial" ou "forest".
            building_id: Identificador da construcao.
            rng: Gerador aleatorio.

        Returns:
            A construcao gerada. Tipos desconhecidos geram uma casa.
        """
        generators: dict[str, Callable[[str, random.Random], Building]] = {
            "residential": BuildingGenerator.generate_residential,
            "commercial": BuildingGenerator.generate_commercial,
            "industrial": BuildingGenerator.generate_industrial,
            "forest": BuildingGenerator.generate_forest,
        }
        return generators.get(kind, BuildingGenerator.generate_residential)(building_id, rng)
