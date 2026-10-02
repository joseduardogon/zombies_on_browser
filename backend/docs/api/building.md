# API de construcoes

Arquivo: `app/api/building_routes.py`. Prefixo: `/api/building`.

## POST /generate/{type}

Gera uma construcao nova, guarda em memoria e a retorna.

Tipos aceitos: `residential`, `commercial`, `industrial`, `forest`. Qualquer outro valor gera uma residencia.

Resposta: [Building](../models/building.md).

## GET /{building_id}

Retorna uma construcao ja gerada. Responde 404 se o identificador for desconhecido.

## Limitacoes atuais

- O frontend gera uma construcao nova a cada clique; as celulas do mapa ainda nao guardam `building_id`.
- O armazenamento e um dicionario em memoria.
