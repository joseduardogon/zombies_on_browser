# Modulo services

Pasta: `app/services/`. As regras do jogo. Nenhum servico importa FastAPI: recebem e devolvem objetos de dominio e levantam `GameError` quando o pedido e invalido.

| Arquivo | Documento | Responsabilidade |
|---------|-----------|------------------|
| `world_generator.py` | [world_generator](world_generator.md) | Gera o mapa e liga cada lote a uma construcao |
| `building_generator.py` | [building_generator](building_generator.md) | Gera construcoes, comodos e pilhagem |
| `building_service.py` | [building_service](building_service.md) | Cria sob demanda e mede a integridade |
| `game_factory.py` | [game_factory](game_factory.md) | Nova partida e escolha do abrigo |
| `survivor_service.py` | [survivor_service](survivor_service.md) | Necessidades, funcoes, cura, morte |
| `base_service.py` | [base_service](base_service.md) | Reforco das aberturas do abrigo |
| `expedition_service.py` | [expedition_service](expedition_service.md) | Expedicoes de coleta |
| `zombie_service.py` | [zombie_service](zombie_service.md) | Ondas noturnas e cerco |
| `simulation.py` | [simulation](simulation.md) | A passagem de uma hora de jogo |
| `persistence.py` | [persistence](persistence.md) | Salvar e carregar em SQLite |
| `game_manager.py` | [game_manager](game_manager.md) | A partida corrente, o lock e o autosave |

## Como as pecas se encaixam

```
game_manager --guarda--> GameState
simulation.advance_hour:
    clock -> zombie_service -> survivor_service -> expedition_service -> fim de jogo
acoes do jogador:
    game_factory.claim_base | base_service.reinforce_aperture
    expedition_service.start_expedition | survivor_service.set_role / treat
```

As rotas em [api](../api/README.md) apenas validam o corpo da requisicao, abrem uma sessao em `game_manager` e chamam uma dessas funcoes.
