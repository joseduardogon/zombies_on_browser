# Modelos de sobrevivente

Arquivo: `app/models/survivor.py`. Ainda nao exposto por nenhuma rota.

| Modelo           | Campos                                                                   |
|------------------|--------------------------------------------------------------------------|
| `SurvivorRole`   | `leader`, `scavenger`, `builder`, `guard`, `idle`                        |
| `SurvivorNeeds`  | `hunger`, `thirst`, `fatigue`, `morale`, `health` (0 a 100)              |
| `SurvivorSkills` | `construction`, `combat`, `scavenging`, `medicine`                       |
| `Survivor`       | `id`, `name`, `role`, `needs`, `skills`, `current_location`, `assigned_building_id` |
