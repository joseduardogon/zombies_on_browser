"""Testes das barricadas e das ondas de zumbis."""

import pytest

from app.core import balance
from app.core.errors import GameError
from app.models.building import ApertureState
from app.models.survivor import SurvivorRole, SurvivorStatus
from app.services import base_service, simulation, zombie_service


def _apertures(state):
    return [a for r in state.buildings[state.base_building_id].rooms for a in r.apertures]


def _disarm(state):
    for survivor in state.survivors:
        survivor.role = SurvivorRole.IDLE


def test_reinforce_costs_wood_and_raises_health(playing):
    aperture = _apertures(playing)[0]
    health, wood = aperture.health, playing.resources.wood
    base_service.reinforce_aperture(playing, aperture.id, playing.survivors[0].id)
    assert aperture.health > health
    assert aperture.state == ApertureState.BARRICADED
    assert playing.resources.wood == wood - balance.BARRICADE_WOOD_COST


def test_builder_reinforces_more(playing, monkeypatch):
    monkeypatch.setattr(balance, "SKILL_GAIN_CHANCE", 0.0)
    first, second = _apertures(playing)[:2]
    first.health = second.health = 10
    worker = playing.survivors[0]
    base_service.reinforce_aperture(playing, first.id, worker.id)
    gained_normal = first.health - 10
    worker.role = SurvivorRole.BUILDER
    base_service.reinforce_aperture(playing, second.id, worker.id)
    assert second.health - 10 > gained_normal


def test_reinforce_repairs_broken_aperture(playing):
    aperture = _apertures(playing)[0]
    aperture.state = ApertureState.BROKEN
    aperture.health = 0
    base_service.reinforce_aperture(playing, aperture.id, playing.survivors[0].id)
    assert aperture.state == ApertureState.BARRICADED
    assert aperture.health > 0


def test_reinforce_errors(playing):
    aperture = _apertures(playing)[0]
    worker = playing.survivors[0]
    with pytest.raises(GameError) as error:
        base_service.reinforce_aperture(playing, "nope", worker.id)
    assert error.value.status_code == 404
    playing.resources.wood = 0
    with pytest.raises(GameError):
        base_service.reinforce_aperture(playing, aperture.id, worker.id)
    playing.resources.wood = 10
    aperture.health = balance.APERTURE_HEALTH_CAP
    with pytest.raises(GameError):
        base_service.reinforce_aperture(playing, aperture.id, worker.id)
    aperture.health = 50
    worker.status = SurvivorStatus.AWAY
    with pytest.raises(GameError):
        base_service.reinforce_aperture(playing, aperture.id, worker.id)


def test_wave_arrives_at_dusk_and_ends_at_dawn(playing):
    playing.clock.hour = balance.NIGHT_START_HOUR - 1
    simulation.advance_hour(playing)
    assert playing.siege.wave_size > 0
    playing.clock.hour = balance.NIGHT_END_HOUR - 1
    simulation.advance_hour(playing)
    assert playing.siege.wave_size == 0


def test_wave_grows_with_days(playing):
    playing.clock.day = 1
    zombie_service.start_night(playing)
    early = playing.siege.wave_size
    playing.clock.day = 25
    zombie_service.start_night(playing)
    assert playing.siege.wave_size > early


def test_guards_kill_zombies_and_spend_ammo(playing):
    playing.siege.wave_size = 8
    ammo = playing.resources.ammo
    zombie_service.assault_round(playing)
    assert playing.siege.killed > 0
    assert playing.resources.ammo < ammo
    assert playing.total_zombies_killed == playing.siege.killed


def test_undefended_apertures_get_battered_and_break(playing):
    _disarm(playing)
    for aperture in _apertures(playing):
        aperture.health = 5
    playing.siege.wave_size = 80
    zombie_service.assault_round(playing)
    assert any(a.state == ApertureState.BROKEN for a in _apertures(playing))
    assert playing.siege.at_gate > 0


def test_weakest_aperture_is_hit_first(playing):
    _disarm(playing)
    for aperture in _apertures(playing):
        aperture.health = 200
    weakest = _apertures(playing)[1]
    weakest.health = 100
    playing.siege.wave_size = 8
    zombie_service.assault_round(playing)
    assert weakest.health < 100
    assert all(a.health == 200 for a in _apertures(playing) if a is not weakest)


def test_breach_hurts_survivors_and_morale(playing):
    _disarm(playing)
    for aperture in _apertures(playing):
        aperture.state = ApertureState.BROKEN
        aperture.health = 0
    playing.siege.wave_size = 40
    health = sum(s.needs.health for s in playing.survivors)
    morale = sum(s.needs.morale for s in playing.survivors)
    zombie_service.assault_round(playing)
    assert sum(s.needs.health for s in playing.survivors) < health
    assert sum(s.needs.morale for s in playing.survivors) < morale


def test_absent_survivors_are_safe_from_siege(playing):
    away = playing.survivors[2]
    away.status = SurvivorStatus.AWAY
    for aperture in _apertures(playing):
        aperture.state = ApertureState.BROKEN
        aperture.health = 0
    playing.siege.wave_size = 80
    health = away.needs.health
    zombie_service.assault_round(playing)
    assert away.needs.health == health


def test_deaths_in_breach_can_end_game(playing):
    _disarm(playing)
    for survivor in playing.survivors:
        survivor.needs.health = 1.0
    for aperture in _apertures(playing):
        aperture.state = ApertureState.BROKEN
        aperture.health = 0
    playing.siege.wave_size = 80
    zombie_service.assault_round(playing)
    simulation.advance_hour(playing)
    assert not playing.alive_survivors()
    assert playing.status.value == "lost"
