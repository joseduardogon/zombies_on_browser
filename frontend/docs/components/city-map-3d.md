# CityMap3D

Arquivo: `src/components/CityMap3D.tsx`.

Desenha a grade do mundo com transformacoes CSS 3D (`rotateX(60deg) rotateZ(-45deg)`). Cada celula mede 40px.

| Setor                                      | Renderizacao                                  |
|--------------------------------------------|-----------------------------------------------|
| `forest`                                   | Arvore triangular                             |
| `road`                                     | Face superior e, a cada 7 celulas, um carro   |
| `residential`, `commercial`, `industrial`  | Bloco com topo e duas laterais                |

Ao clicar em uma celula, chama `fetchBuilding` com o setor. A altura e as cores de cada setor vem de [city-3d.css](../styles/README.md).

Pendente: arrastar para mover a camera (indicado no HUD como "Coming Soon").
