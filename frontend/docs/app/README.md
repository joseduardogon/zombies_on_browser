# Modulo app

Arquivos: `src/main.tsx` e `src/App.tsx`.

`main.tsx` monta o React em `#root` dentro de `StrictMode`.

`App` chama `generateWorld` ao montar e escolhe o que exibir:

| Estado        | Tela                                              |
|---------------|---------------------------------------------------|
| `isLoading`   | Mensagem de carregamento                          |
| `error`       | Tela "SIGNAL LOST" com botao de nova tentativa    |
| demais        | [CityMap3D](../components/city-map-3d.md)         |

[BuildingView](../components/building-view.md) fica sobreposto e so aparece com uma construcao selecionada.
