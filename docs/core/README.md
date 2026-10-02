# Modulo core

Arquivo: `app/main.py`.

Cria a aplicacao FastAPI, configura o CORS e registra os routers.

## CORS

Origens liberadas: `localhost` e `127.0.0.1` nas portas 5173 e 5174 (servidor de desenvolvimento do frontend).

## Endpoints

| Metodo | Caminho   | Descricao                         |
|--------|-----------|-----------------------------------|
| GET    | `/`       | Status e mensagem da API          |
| GET    | `/health` | Verificacao de saude do servico   |

## Routers registrados

| Prefixo         | Modulo                          |
|-----------------|---------------------------------|
| `/api/world`    | [world_routes](../api/world.md) |
| `/api/building` | [building_routes](../api/building.md) |
