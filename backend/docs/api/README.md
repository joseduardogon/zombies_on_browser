# Modulo api

Pasta: `app/api/`. A camada HTTP. Cada arquivo define um `APIRouter` fino: valida o corpo da requisicao, abre uma sessao em `game_manager`, chama uma funcao de `services/` e devolve a partida atualizada.

| Arquivo | Prefixo | Documento |
|---------|---------|-----------|
| `game_routes.py` | `/api/game` | [game](game.md) |
| `world_routes.py` | `/api/world` | [world](world.md) |
| `building_routes.py` | `/api/building` | [building](building.md) |
| `base_routes.py` | `/api/base` | [base](base.md) |
| `survivor_routes.py` | `/api/survivors` | [survivors](survivors.md) |
| `expedition_routes.py` | `/api/expeditions` | [expeditions](expeditions.md) |
| `schemas.py` | (nenhum) | [schemas](schemas.md) |

## Convencoes

- **Toda acao devolve `GameView`.** Assim o frontend atualiza a tela inteira com uma unica resposta, sem consultas extras.
- **Erros de regra** chegam como `{"detail": "..."}` com o status escolhido pelo servico (400, 404 ou 409). Erros de formato de corpo (por exemplo `hours: 0`) chegam como 422 do proprio FastAPI.
- **Nenhuma regra nas rotas.** Se uma rota precisa de mais que "abrir sessao, chamar servico, montar visao", a logica pertence a `services/`.

## Quadro geral

| Metodo | Caminho | O que faz |
|--------|---------|-----------|
| POST | `/api/game/new` | Cria partida |
| GET | `/api/game` | Consulta a partida corrente |
| POST | `/api/game/tick` | Avanca horas |
| GET | `/api/game/saves` | Lista saves |
| POST | `/api/game/save` | Grava em um espaco |
| POST | `/api/game/load` | Carrega um espaco |
| GET | `/api/world/state` | Mapa da cidade |
| GET | `/api/building/{id}` | Constroi e devolve uma construcao |
| POST | `/api/base/claim` | Escolhe o abrigo |
| POST | `/api/base/reinforce` | Reforca uma abertura |
| GET | `/api/survivors` | Lista sobreviventes |
| POST | `/api/survivors/{id}/role` | Muda a funcao |
| POST | `/api/survivors/{id}/treat` | Trata um ferido |
| POST | `/api/expeditions` | Envia uma expedicao |

Removidas nesta etapa: `POST /api/world/generate` e `POST /api/building/generate/{type}`. Elas geravam mundo e construcoes soltos, fora de uma partida; agora tudo nasce dentro de `POST /api/game/new`.
