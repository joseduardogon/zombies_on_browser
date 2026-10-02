# BuildingGenerator

Arquivo: `app/services/building_generator.py`.

Metodos estaticos que recebem o `building_id` e retornam um [Building](../models/building.md).

| Metodo                | Resultado                                                    | Integridade |
|-----------------------|--------------------------------------------------------------|-------------|
| `generate_residential`| Sala, cozinha e quarto, com porta e janelas                  | 100         |
| `generate_commercial` | Salao unico com porta de vidro e vitrine                     | 80          |
| `generate_industrial` | Galpao unico com porta reforcada e janela                    | 90          |
| `generate_forest`     | Clareira e barraca abandonada                                | 10          |

Os comodos de loja reutilizam `living_room` como espaco aberto ate existir um tipo proprio.
