# Modulo store

Arquivo: `src/store/gameStore.ts`. Store global com Zustand, exposta pelo hook `useGameStore`.

## Tipos

Espelham os modelos do backend: `Coordinates`, `WorldCell`, `WorldMap`, `Aperture`, `Room`, `Building`.

## Estado

| Campo              | Tipo               | Descricao                        |
|--------------------|--------------------|----------------------------------|
| `world`            | `WorldMap \| null` | Mapa atual                       |
| `selectedBuilding` | `Building \| null` | Construcao aberta                |
| `isLoading`        | `boolean`          | Requisicao em andamento          |
| `error`            | `string \| null`   | Ultima mensagem de erro          |

## Acoes

| Acao             | Endpoint                          |
|------------------|-----------------------------------|
| `generateWorld`  | `POST /api/world/generate`        |
| `fetchWorldState`| `GET /api/world/state`            |
| `fetchBuilding`  | `POST /api/building/generate/{type}` |
| `closeBuilding`  | Local, limpa `selectedBuilding`   |

Qualquer erro preenche `error`, e o `App` troca o mapa pela tela de erro. Falhas ao abrir construcao tambem caem nessa tela.
