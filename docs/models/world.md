# Modelos de mundo

Arquivo: `app/models/world.py`.

| Modelo        | Campos                                                              |
|---------------|---------------------------------------------------------------------|
| `Coordinates` | `x`, `y`                                                            |
| `SectorType`  | `residential`, `commercial`, `industrial`, `forest`, `road`         |
| `WorldCell`   | `coordinates`, `sector_type`, `is_explored`, `building_id` opcional |
| `WorldMap`    | `width`, `height`, `cells` em ordem de linha                        |
