# Modelos de construcao

Arquivo: `app/models/building.py`.

| Modelo          | Campos                                                                         |
|-----------------|--------------------------------------------------------------------------------|
| `RoomType`      | `living_room`, `kitchen`, `bedroom`, `bathroom`, `garage`, `storage`, `industrial`, `outdoor`, `shelter`, `empty` |
| `ApertureState` | `open`, `closed`, `barricaded`, `broken`                                       |
| `Aperture`      | `id`, `type` (`door` ou `window`), `state`, `health`                           |
| `Room`          | `id`, `name`, `type`, `dimensions` (`width`, `length`), `apertures`, `insulation`, `security` |
| `Building`      | `id`, `type`, `rooms`, `overall_integrity`                                     |

`health` representa a durabilidade da porta ou da barricada. As aberturas sao o ponto de entrada dos zumbis na futura simulacao de cerco.
