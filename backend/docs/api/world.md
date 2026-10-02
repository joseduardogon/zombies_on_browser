# API de mundo

Arquivo: `app/api/world_routes.py`. Prefixo: `/api/world`.

## POST /generate

Gera um novo mapa e o guarda como mundo atual.

Parametros de query:

| Nome   | Tipo | Padrao | Descricao                   |
|--------|------|--------|-----------------------------|
| width  | int  | 20     | Largura do mapa em celulas  |
| height | int  | 20     | Altura do mapa em celulas   |

Resposta: [WorldMap](../models/world.md).

## GET /state

Retorna o mundo atual. Responde 404 se nenhum mundo foi gerado.

## Regras de geracao

1. Celulas com `x` ou `y` multiplo de 4 sao vias (`road`) e ja nascem exploradas.
2. As demais celulas recebem setor conforme a distancia ao centro:
   - proximas do centro (menos de 20% da dimensao): `commercial`;
   - distantes do centro (mais de 45% da dimensao): `forest`;
   - demais: `residential`.
3. Fora da floresta, cada celula tem 10% de chance de virar `industrial`.
