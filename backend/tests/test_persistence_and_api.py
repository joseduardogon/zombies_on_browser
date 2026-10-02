"""Testes da persistencia em SQLite e da API HTTP."""

from app.models.game import GameState
from app.services import simulation
from app.services.game_manager import manager
from app.services.persistence import GameRepository


def _claim(client):
    game = client.post("/api/game/new", json={"seed": 11}).json()
    lot = next(c for c in game["world"]["cells"] if c["sector_type"] == "residential")
    response = client.post("/api/base/claim", json={"building_id": lot["building_id"]})
    return response.json()


def test_repository_roundtrip(isolated_repository, playing):
    simulation.advance_hours(playing, 5)
    isolated_repository.save("slot", playing)
    loaded = isolated_repository.load("slot")
    assert isinstance(loaded, GameState)
    assert loaded == playing
    assert isolated_repository.load("missing") is None


def test_repository_lists_saves_newest_first(isolated_repository, playing):
    isolated_repository.save("a", playing)
    isolated_repository.save("b", playing)
    slots = [s.slot for s in isolated_repository.list_saves()]
    assert set(slots) == {"a", "b"}


def test_autosave_survives_restart(isolated_repository, playing):
    manager.replace(playing)
    manager.configure(GameRepository(isolated_repository.path))
    assert manager.state is None
    assert manager.load_autosave()
    assert manager.state == playing


def test_no_game_returns_404(client):
    assert client.get("/api/game").status_code == 404
    assert client.post("/api/game/tick", json={"hours": 1}).status_code == 404


def test_new_game_and_world(client):
    game = client.post("/api/game/new", json={"seed": 1}).json()
    assert game["status"] == "setup"
    assert game["target_day"] == 30
    assert len(game["world"]["cells"]) == 400
    assert client.get("/api/world/state").json()["width"] == 20


def test_invalid_world_size_is_rejected(client):
    response = client.post("/api/game/new", json={"width": 2, "height": 20})
    assert response.status_code == 400


def test_tick_requires_a_shelter(client):
    client.post("/api/game/new", json={"seed": 1})
    assert client.post("/api/game/tick", json={"hours": 1}).status_code == 409


def test_claim_then_tick_advances_clock(client):
    game = _claim(client)
    assert game["status"] == "playing"
    assert len(game["survivors"]) == 3
    assert game["base_building"]["rooms"]
    ticked = client.post("/api/game/tick", json={"hours": 3}).json()
    assert ticked["clock"]["hour"] == game["clock"]["hour"] + 3
    assert client.post("/api/game/tick", json={"hours": 0}).status_code == 422


def test_building_endpoint_hides_unsearched_loot(client):
    game = _claim(client)
    other = next(
        c for c in game["world"]["cells"]
        if c["building_id"] and c["building_id"] != game["base_building"]["id"]
    )
    building = client.get(f"/api/building/{other['building_id']}").json()
    assert building["searched"] is False
    assert all(v == 0 for v in building["loot"].values())
    assert client.get("/api/building/nope").status_code == 404


def test_full_action_flow(client):
    game = _claim(client)
    scavenger = next(s for s in game["survivors"] if s["role"] == "scavenger")
    target = next(
        c for c in game["world"]["cells"]
        if c["building_id"] and c["building_id"] != game["base_building"]["id"]
    )

    sent = client.post(
        "/api/expeditions",
        json={"survivor_id": scavenger["id"], "building_id": target["building_id"]},
    ).json()
    assert len(sent["expeditions"]) == 1
    absent = next(s for s in sent["survivors"] if s["id"] == scavenger["id"])
    assert absent["status"] == "away"

    role = client.post(f"/api/survivors/{scavenger['id']}/role", json={"role": "builder"})
    assert role.json()["survivors"][2]["role"] == "builder"

    leader = next(s for s in game["survivors"] if s["role"] == "leader")
    aperture = game["base_building"]["rooms"][0]["apertures"][0]
    reinforced = client.post(
        "/api/base/reinforce",
        json={"aperture_id": aperture["id"], "survivor_id": leader["id"]},
    ).json()
    new_state = reinforced["base_building"]["rooms"][0]["apertures"][0]
    assert new_state["health"] > aperture["health"]
    assert new_state["state"] == "barricaded"

    assert client.post(f"/api/survivors/{leader['id']}/treat").status_code == 400


def test_errors_use_detail_field(client):
    _claim(client)
    response = client.post(
        "/api/expeditions", json={"survivor_id": "s99", "building_id": "b-1-1"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Survivor not found"


def test_save_and_load_slots(client):
    _claim(client)
    saves = client.post("/api/game/save", json={"slot": "checkpoint"}).json()
    assert "checkpoint" in [s["slot"] for s in saves]

    client.post("/api/game/tick", json={"hours": 6})
    loaded = client.post("/api/game/load", json={"slot": "checkpoint"}).json()
    assert loaded["clock"]["total_hours"] == 0
    assert client.post("/api/game/load", json={"slot": "ghost"}).status_code == 404
    assert client.get("/api/game/saves").status_code == 200


def test_state_is_restored_from_autosave_by_get(client, isolated_repository):
    _claim(client)
    client.post("/api/game/tick", json={"hours": 2})
    manager.configure(GameRepository(isolated_repository.path))
    manager.load_autosave()
    assert client.get("/api/game").json()["clock"]["total_hours"] == 2
