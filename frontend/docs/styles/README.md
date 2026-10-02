# Modulo styles

- `src/index.css`: importa o Tailwind e define tema escuro e reset do `body`.
- `src/city-3d.css`: estilos do mapa isometrico.

## city-3d.css

| Classe                 | Funcao                                                     |
|------------------------|------------------------------------------------------------|
| `.viewport-3d`         | Area com perspectiva                                       |
| `.city-plane`          | Plano rotacionado que contem a grade                       |
| `.city-cell`           | Celula de 40px; sobe 5px no hover                          |
| `.block-3d`, `.face-*` | Caixa 3D controlada por `--height` e variaveis de cor      |
| `.type-<setor>`        | Define altura e cores de cada setor                        |
| `.tree`, `.car`        | Arvore estatica e carro animado (`drive`)                  |

Alturas: residencial 16px, industrial 25px, comercial 60px, via 1px.
