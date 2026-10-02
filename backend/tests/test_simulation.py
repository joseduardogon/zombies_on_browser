"""Testes do relogio, das necessidades e da condicao de fim de jogo."""

import pytest

from app.core import balance
from app.core.errors import GameError
from app.models.game import GameStatus
from app.models.survivor import SurvivorRole, SurvivorStatus
from app.services import game_factory, simulation, survivor_service


def test_claim_base_starts_game(playing):
    assert playing.status == GameStatus.PLAYING
    assert len(playing.survivors) == balance.STARTING_SURVIVORS
    assert playing.resources.food == balance.STARTING_RESOURCES["food"]
    assert playing.base_building_id in playing.buildings
    assert {s.role for s in playing.survivors} == {
        SurvivorRole.LEADER,
        SurvivorRole.GUARD,
        SurvivorRole.SCAVENGER,
    }


def test_claim_rejects_forest_and_second_claim(playing):
    fresh = game_factory.new_game(20, 20, seed=7)
    forest = next(c for c in fresh.world.cells if c.sector_type.value == "forest")
    with pytest.raises(GameError):
        game_factory.claim_base(fresh, forest.building_id)
    with pytest.raises(GameError) as error:
        game_factory.claim_base(playing, playing.base_building_id)
    assert error.value.status_code == 409


def test_clock_rolls_over_midnight(playing):
    playing.clock.hour = 23
    simulation.advance_hour(playing)
    assert (playing.clock.day, playing.clock.hour) == (2, 0)
    assert playing.clock.phase == "night"


def test_phase_changes_at_dawn_and_dusk(playing):
    playing.clock.hour = 5
    simulation.advance_hour(playing)
    assert playing.clock.phase == "day"
    playing.clock.hour = 19
    simulation.advance_hour(playing)
    assert playing.clock.phase == "night"


def test_cannot_advance_before_claiming(state):
    with pytest.raises(GameError) as error:
        simulation.advance_hour(state)
    assert error.value.status_code == 409


def test_needs_decay_each_hour(playing):
    survivor = playing.survivors[0]
    playing.resources.food = playing.resources.water = 0
    simulation.advance_hour(playing)
    assert survivor.needs.hunger == 100 - balance.HUNGER_DECAY
    assert survivor.needs.thirst == 100 - balance.THIRST_DECAY


def test_survivor_eats_and_drinks_when_hungry(playing):
    survivor = playing.survivors[0]
    survivor.needs.hunger = 50.0
    survivor.needs.thirst = 50.0
    food, water = playing.resources.food, playing.resources.water
    survivor_service.update_needs_hour(playing)
    assert survivor.needs.hunger > 50
    assert survivor.needs.thirst > 50
    assert playing.resources.food < food
    assert playing.resources.water < water


def test_starvation_kills_and_ends_game(playing):
    playing.resources.food = playing.resources.water = 0
    simulation.advance_hours(playing, 24 * 10)
    assert all(s.status == SurvivorStatus.DEAD for s in playing.survivors)
    assert playing.status == GameStatus.LOST


def test_survivors_sleep_but_guards_do_not(playing):
    playing.clock.hour = 0
    for survivor in playing.survivors:
        survivor.needs.fatigue = 50.0
    guard = next(s for s in playing.survivors if s.role == SurvivorRole.GUARD)
    sleeper = next(s for s in playing.survivors if s.role == SurvivorRole.SCAVENGER)
    survivor_service.update_needs_hour(playing)
    assert sleeper.needs.fatigue > 50
    assert guard.needs.fatigue < 50


def test_winning_after_target_day(playing):
    playing.clock.day = balance.TARGET_DAY
    playing.clock.hour = 23
    simulation.advance_hour(playing)
    assert playing.status == GameStatus.WON


def test_same_seed_and_actions_give_same_result():
    def run():
        game = game_factory.new_game(20, 20, seed=5)
        cell = next(c for c in game.world.cells if c.sector_type.value == "residential")
        game_factory.claim_base(game, cell.building_id)
        simulation.advance_hours(game, 72)
        return game.model_dump(exclude={"id"})

    assert run() == run()


def test_set_role_and_treat(playing):
    survivor = playing.survivors[2]
    survivor_service.set_role(playing, survivor.id, SurvivorRole.BUILDER)
    assert survivor.role == SurvivorRole.BUILDER

    survivor.needs.health = 40.0
    survivor_service.treat(playing, survivor.id)
    assert survivor.needs.health > 40
    assert playing.resources.medicine == balance.STARTING_RESOURCES["medicine"] - 1

    playing.resources.medicine = 0
    survivor.needs.health = 10.0
    with pytest.raises(GameError):
        survivor_service.treat(playing, survivor.id)


def test_treat_rejects_healthy_survivor(playing):
    with pytest.raises(GameError):
        survivor_service.treat(playing, playing.survivors[0].id)
