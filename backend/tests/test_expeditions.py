"""Testes das expedicoes de coleta."""

import pytest

from app.core import balance
from app.core.errors import GameError
from app.models.survivor import SurvivorStatus
from app.services import expedition_service, simulation
from app.services.building_service import get_or_create_building


def _target(state, sector="residential"):
    return next(
        c
        for c in state.world.cells
        if c.sector_type.value == sector and c.building_id != state.base_building_id
    )


def _safe(monkeypatch):
    monkeypatch.setattr(balance, "SECTOR_DANGER", {k: 0.0 for k in balance.SECTOR_DANGER})
    monkeypatch.setattr(balance, "NIGHT_DANGER_BONUS", 0.0)


def test_expedition_takes_round_trip_and_returns_loot(playing, monkeypatch):
    _safe(monkeypatch)
    cell = _target(playing)
    survivor = playing.survivors[2]
    building = get_or_create_building(playing, cell.building_id)
    available = building.loot.model_copy()
    expedition = expedition_service.start_expedition(playing, survivor.id, cell.building_id)

    one_way = expedition_service.travel_hours(playing, cell.coordinates.x, cell.coordinates.y)
    assert expedition.ticks_total == 2 * one_way + balance.SEARCH_HOURS
    assert survivor.status == SurvivorStatus.AWAY
    assert survivor.current_location == cell.coordinates

    before = playing.resources.model_copy()
    playing.resources.food = playing.resources.water = 999
    simulation.advance_hours(playing, expedition.ticks_total)
    assert survivor.status == SurvivorStatus.HOME
    assert survivor.current_location == playing.base_cell
    assert playing.expeditions == []
    assert cell.is_explored and building.searched
    assert playing.resources.wood >= before.wood
    assert playing.resources.wood - before.wood <= available.wood


def test_loot_is_removed_from_building(playing, monkeypatch):
    _safe(monkeypatch)
    cell = _target(playing)
    building = get_or_create_building(playing, cell.building_id)
    building.loot.scrap = 10
    scrap = playing.resources.scrap
    expedition_service.start_expedition(playing, playing.survivors[2].id, cell.building_id)
    simulation.advance_hours(playing, 30)
    taken = playing.resources.scrap - scrap
    assert taken > 0
    assert building.loot.scrap == 10 - taken


def test_cannot_send_absent_survivor_twice(playing):
    cell = _target(playing)
    survivor = playing.survivors[2]
    expedition_service.start_expedition(playing, survivor.id, cell.building_id)
    with pytest.raises(GameError):
        expedition_service.start_expedition(playing, survivor.id, cell.building_id)


def test_cannot_scavenge_shelter_or_unknown_building(playing):
    survivor = playing.survivors[0]
    with pytest.raises(GameError):
        expedition_service.start_expedition(playing, survivor.id, playing.base_building_id)
    with pytest.raises(GameError) as error:
        expedition_service.start_expedition(playing, survivor.id, "nope")
    assert error.value.status_code == 404


def test_hurt_survivor_cannot_leave(playing):
    cell = _target(playing)
    survivor = playing.survivors[0]
    survivor.needs.health = balance.MIN_EXPEDITION_HEALTH - 1
    with pytest.raises(GameError):
        expedition_service.start_expedition(playing, survivor.id, cell.building_id)


def test_encounter_can_kill_survivor(playing, monkeypatch):
    cell = _target(playing)
    monkeypatch.setitem(balance.SECTOR_DANGER, cell.sector_type, 1.0)
    monkeypatch.setattr(balance, "ENCOUNTER_MIN_DAMAGE", 500)
    monkeypatch.setattr(balance, "ENCOUNTER_MAX_DAMAGE", 500)
    survivor = playing.survivors[2]
    expedition_service.start_expedition(playing, survivor.id, cell.building_id)
    simulation.advance_hours(playing, 30)
    assert survivor.status == SurvivorStatus.DEAD
    assert playing.expeditions == []


def test_lone_survivor_joins_after_search(playing, monkeypatch):
    _safe(monkeypatch)
    cell = _target(playing)
    building = get_or_create_building(playing, cell.building_id)
    building.survivor_present = True
    count = len(playing.alive_survivors())
    expedition_service.start_expedition(playing, playing.survivors[2].id, cell.building_id)
    simulation.advance_hours(playing, 30)
    assert len(playing.alive_survivors()) == count + 1
    assert not building.survivor_present
