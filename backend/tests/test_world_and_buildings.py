"""Testes da geracao de mundo e de construcoes."""

import random

import pytest

from app.core.errors import GameError
from app.models.world import SectorType
from app.services.building_generator import BuildingGenerator
from app.services.building_service import get_or_create_building
from app.services.world_generator import building_id_for, generate_world


def test_world_has_roads_every_four_cells():
    world = generate_world(20, 20, random.Random(1))
    roads = [c for c in world.cells if c.sector_type == SectorType.ROAD]
    assert all(c.coordinates.x % 4 == 0 or c.coordinates.y % 4 == 0 for c in roads)
    assert all(c.building_id is None and c.is_explored for c in roads)


def test_every_lot_has_stable_building_id():
    world = generate_world(20, 20, random.Random(1))
    lots = [c for c in world.cells if c.sector_type != SectorType.ROAD]
    assert lots
    for cell in lots:
        assert cell.building_id == building_id_for(cell.coordinates.x, cell.coordinates.y)
        assert not cell.is_explored


def test_world_is_reproducible_for_same_seed():
    first = generate_world(20, 20, random.Random("a"))
    second = generate_world(20, 20, random.Random("a"))
    assert first == second


@pytest.mark.parametrize("size", [4, 41])
def test_world_size_limits(size):
    with pytest.raises(GameError):
        generate_world(size, 20, random.Random(1))


@pytest.mark.parametrize("kind", ["residential", "commercial", "industrial", "forest", "x"])
def test_every_generator_builds_valid_building(kind):
    building = BuildingGenerator.generate(kind, "b-1-1", random.Random(3))
    assert building.rooms
    ids = [a.id for r in building.rooms for a in r.apertures]
    assert len(ids) == len(set(ids))
    assert not building.searched


def test_building_is_generated_once_and_deterministically(state):
    cell = next(c for c in state.world.cells if c.building_id)
    first = get_or_create_building(state, cell.building_id)
    again = get_or_create_building(state, cell.building_id)
    assert first is again

    other = game_factory_copy(state)
    assert get_or_create_building(other, cell.building_id) == first


def game_factory_copy(state):
    """Cria uma partida igual, mas sem construcoes geradas.

    Args:
        state: Partida original.

    Returns:
        Copia sem o cache de construcoes.
    """
    clone = state.model_copy(deep=True)
    clone.buildings = {}
    return clone


def test_unknown_building_is_not_found(state):
    with pytest.raises(GameError) as error:
        get_or_create_building(state, "nope")
    assert error.value.status_code == 404


def test_default_world_has_every_sector_type():
    world = generate_world(20, 20, random.Random(1))
    assert {c.sector_type for c in world.cells} >= {
        SectorType.ROAD,
        SectorType.COMMERCIAL,
        SectorType.RESIDENTIAL,
        SectorType.FOREST,
    }
